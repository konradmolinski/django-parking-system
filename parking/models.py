import pytz
import datetime
from django.db import models
from django.conf import settings

class Client(models.Model):
    plate_num = models.CharField(unique=True, max_length=50)
    voucher = models.DurationField()



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
        taken_spots = ParkingEntry.objects.filter(end_date__isnull=True).count()
        return settings.PARKING_SPOTS - taken_spots



payment_status_choices = [
    ('P', 'PAID'),
    ('U', 'UNPAID'),
]
class PaymentRegister(models.Model):

    payment_date = models.DateTimeField(auto_now_add=True)
    parking_entry_id = models.IntegerField()
    amount = models.IntegerField()
    status = models.CharField(max_length=1, choices=payment_status_choices, default='U')

class Reservation(models.Model):
    client_id = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    payment_id = models.ForeignKey(PaymentRegister, on_delete=models.CASCADE)

class Subscription(models.Model):

    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    payment_id = models.ForeignKey(PaymentRegister, on_delete=models.CASCADE)
    parking_spot = models.IntegerField()


