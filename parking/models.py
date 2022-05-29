from django.db import models
import datetime
import pytz
PARKING_SPOTS = 50


class Client(models.Model):
    plate_num = models.CharField(unique=True, max_length=50)
    voucher = models.DurationField()

class ParkingEntry(models.Model):

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    billing_type_choices = [
        ('ADH', 'AD_HOC'),
        ('VCR', 'VOUCHER'),
        ('SUB', 'SUBSCRIPTION'),
    ]
    billing_type = models.CharField(max_length=3, choices=billing_type_choices, default='ADH')
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    plate_num = models.CharField(max_length=50)
    overtime = models.DurationField(null=True, blank=True)
    reservation_id = models.ForeignKey('Reservation', null=True, on_delete=models.SET_NULL)

    @staticmethod
    def free_spots():
        taken_spots = ParkingEntry.objects.filter(end_date__isnull=True).count()
        return PARKING_SPOTS - taken_spots

class PaymentRegister(models.Model):

    payment_date = models.DateTimeField(auto_now_add=True)
    parking_entry_id = models.IntegerField()
    amount = models.IntegerField()
    payment_status_choices = [
        ('P', 'PAID'),
        ('U', 'UNPAID'),
    ]
    status = models.CharField(max_length=1, choices=payment_status_choices, default='U')

    @staticmethod
    def calculate_parking_cost(start_date, end_date):

        timezone = pytz.timezone("UTC")
        busy_seconds, standard_seconds, weekend_seconds = datetime.timedelta(), datetime.timedelta(), datetime.timedelta()

        price_list = {
            'busy': {
                'hours': (range(7, 10), range(15, 18)),
                'price': 10,
            },
            'standard': {
                'hours': (range(0, 7), range(10, 15), range(18, 24)),
                'price': 5,
            },
            'weekend': {
                'price': 7,
            }
        }

        last_breakpoint = start_date

        def append_tariff(breakpoint):

            nonlocal last_breakpoint
            nonlocal end_date
            second = datetime.timedelta(seconds=1)
            breakpoint = timezone.localize(breakpoint)

            if breakpoint > end_date:
                add_time = end_date - last_breakpoint + second
                last_breakpoint = end_date
            else:
                add_time = breakpoint - last_breakpoint + second
                last_breakpoint = breakpoint + second

            last_breakpoint = timezone.localize(last_breakpoint)
            return add_time

        while last_breakpoint < end_date:

            if last_breakpoint.weekday() in range(5) and last_breakpoint.hour in price_list['busy']['hours'][0]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               9, 59, 59)
                busy_seconds += append_tariff(breakpoint)

            elif last_breakpoint.weekday() in range(5) and last_breakpoint.hour in price_list['busy']['hours'][1]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               17, 59, 59)
                busy_seconds += append_tariff(breakpoint)

            elif last_breakpoint.weekday() in range(5) and last_breakpoint.hour in price_list['standard']['hours'][0]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               6, 59, 59)
                standard_seconds += append_tariff(breakpoint)

            elif last_breakpoint.weekday() in range(5) and last_breakpoint.hour in price_list['standard']['hours'][1]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               14, 59, 59)
                standard_seconds += append_tariff(breakpoint)

            elif last_breakpoint.weekday() in range(5) and last_breakpoint.hour in price_list['standard']['hours'][2]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               23, 59, 59)
                standard_seconds += append_tariff(breakpoint)

            elif last_breakpoint.weekday() in (5, 6):

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month,
                                               last_breakpoint.day, 23, 59, 59)
                weekend_seconds += append_tariff(breakpoint)

        return (busy_seconds / 3600 * price_list['busy']['price']).seconds \
               + (standard_seconds / 3600 * price_list['standard']['price']).seconds \
               + (weekend_seconds / 3600 * price_list['weekend']['price']).seconds

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


