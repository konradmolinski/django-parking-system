import pytz
import datetime
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.db.models import Max

class Client(models.Model):
    plate_num = models.CharField(unique=True, max_length=50)
    voucher = models.DurationField(null=True, blank=True)

    def has_subscription_in_range(self, start_date, end_date):
        pre_date_query = Subscription.objects.filter(
            Q(client_id=self),
            Q(start_date__gt=start_date),
            Q(start_date__lt=end_date)
        )

        post_date_query = Subscription.objects.filter(
            Q(client_id=self),
            Q(start_date__lt=start_date),
            Q(end_date__gt=start_date)
        )

        exact_date_query = Subscription.objects.filter(
            Q(client_id=self),
            Q(start_date=start_date) | Q(end_date=end_date)
        )
        return not (pre_date_query or post_date_query or exact_date_query)

billing_type_choices = [
    ('ADH', 'AD_HOC'),
    ('VCR', 'VOUCHER'),
    ('SUB', 'SUBSCRIPTION'),
]
class ParkingEntry(models.Model):

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    billing_type = models.CharField(max_length=3, choices=billing_type_choices, default='ADH')
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    plate_num = models.CharField(max_length=50)
    overtime = models.DurationField(null=True, blank=True)
    reservation_id = models.ForeignKey('Reservation', null=True, on_delete=models.SET_NULL)

    @staticmethod
    def free_spots():
        timezone = pytz.timezone(settings.TIME_ZONE)
        now = timezone.localize(datetime.datetime.now())
        taken_spots = ParkingEntry.objects.filter(end_date__isnull=True).count()
        sub_spots = Subscription.objects.filter(
            Q(end_date__gt=now),
            Q(start_date__lte=now)
        ).count()
        return settings.PARKING_SPOTS - taken_spots - sub_spots



payment_status_choices = [
    ('P', 'PAID'),
    ('U', 'UNPAID'),
]
class PaymentRegister(models.Model):

    payment_date = models.DateTimeField(auto_now_add=True)
    parking_entry_id = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=1, choices=payment_status_choices, default='U')

class Reservation(models.Model):
    client_id = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    payment_id = models.ForeignKey(PaymentRegister, on_delete=models.CASCADE)

class Subscription(models.Model):

    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    payment_id = models.ForeignKey(PaymentRegister, on_delete=models.CASCADE)

    @staticmethod
    def subscriptions_available():
        timezone = pytz.timezone(settings.TIME_ZONE)
        now = timezone.localize(datetime.datetime.now())
        active_subscriptions = Subscription.objects.filter(
            Q(start_date__lte=now),
            Q(end_date__gte=now)
        ).count()
        return int(settings.PARKING_SPOTS * 0.9 - active_subscriptions)

    @staticmethod
    def max_possible_subscription_time():
        timezone = pytz.timezone(settings.TIME_ZONE)
        now = timezone.localize(datetime.datetime.now())
        if Subscription.objects.filter(start_date__gt=now).count() >= settings.PARKING_SPOTS * 0.9:
            try:
                closest_upcoming_subscription = Subscription.objects.filter(start_date__gt=now)\
                    .aggregate(Max('start_date'))
                max_subscription_time = closest_upcoming_subscription['start_date__max'] - now
            except:
                max_subscription_time = datetime.timedelta(days=28)
        else:
            max_subscription_time = datetime.timedelta(days=28)
        return max_subscription_time.days

