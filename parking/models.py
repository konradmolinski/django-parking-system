from django.db import models
PARKING_SPOTS = 50
class Client(models.Model):
    plate_num = models.CharField(unique=True, max_length=50)
    voucher = models.DurationField()

class ParkingEntry(models.Model):

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    billing_type = models.CharField(max_length=50)
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    plate_num = models.CharField(max_length=50)
    overtime = models.DurationField(null=True, blank=True)
    reservation_id = models.ForeignKey('Reservation', null=True, on_delete=models.SET_NULL)

    def free_spots(self):
        taken_spots = self.objects.filter(end_date__isnull=True).count()
        return PARKING_SPOTS - taken_spots


class PaymentRegister(models.Model):

    payment_date = models.DateTimeField(auto_now_add=True)
    parking_entry_id = models.ForeignKey(ParkingEntry, on_delete=models.PROTECT)
    amount = models.IntegerField()

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


