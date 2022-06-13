import datetime
import pytz
import re
from django.conf import settings
from django.views.generic import TemplateView
from .models import ParkingEntry, PaymentRegister, Client, Subscription
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .utils import parking_cost, sub_cost, voucher_cost
from .models import payment_status_choices


class FreeSpotsAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        return Response({"free_spots": ParkingEntry.free_spots()})

class SubscriptionsInfoAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        timezone = pytz.timezone(settings.TIME_ZONE)
        return Response({"available_subscriptions": Subscription.subscriptions_available(),
                         "max_subscription_time": Subscription.max_possible_subscription_time()}) #max_subscription_time.days doesnt include current day.

class GetTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        plate_num = request.data["plate_nr"]
        plate_num_max_length = ParkingEntry._meta.get_field('plate_num').max_length

        if not plate_num:
            return Response({"error_msg": "Plate number cannot be empty string."}, status=400)
        if len(plate_num) > plate_num_max_length:
            return Response({"error_msg": f"Plate number cannot be longer then {plate_num_max_length} chars."}, status=400)
        if ParkingEntry.objects.filter(plate_num=plate_num, end_date=None).exists():
            return Response({"error_msg": "You cannot enter parking twice without leaving first."}, status=400)

        client, created = Client.objects.get_or_create(plate_num=plate_num)

        if Subscription.objects.filter(client_id=client).exists():
            entry = ParkingEntry(billing_type="SUB", plate_num=plate_num, client=client)
            entry.save()
            return Response({"ticket_id": entry.id})

        elif client.voucher > datetime.timedelta(seconds=0):
            entry = ParkingEntry(billing_type="VCR", plate_num=plate_num, client=client)
            entry.save()
            return Response({"ticket_id": entry.id})

        if ParkingEntry.free_spots():
            entry = ParkingEntry(billing_type="ADH", plate_num=plate_num, client=client)
            entry.save()
            return Response({"ticket_id": entry.id})
        else:
            return Response({"error_msg": "No available parking spots at the moment."}, status=status.HTTP_403_FORBIDDEN)

class PayAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        data = request.data

        if not data['ticket_id'].isnumeric():
            return Response({"error_msg": "Ticket ID is supposed to be a number."}, status=400)
        if data['payment_status'] not in [x[0] for x in payment_status_choices]:
            return Response({"error_msg": "Wrong payment status type"}, status=400)

        try:
            payment = PaymentRegister.objects.get(parking_entry_id=data['ticket_id'])
            if payment.status == 'P':
                return Response({"error_msg": "Ticket already paid."}, status=400)
            else:
                payment.status = data['payment_status']
                payment.save()
                return Response({"payment_status": payment.status})
        except:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)

class ReturnTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        timezone = pytz.timezone(settings.TIME_ZONE)

        ticket_id = request.data["ticket_id"]
        if not ticket_id.isnumeric():
            return Response({"error_msg": "Ticket ID is supposed to be a number."}, status=400)

        try:
            parking_entry = ParkingEntry.objects.get(id=ticket_id)
        except:
            return Response({"error_msg": "Ticket not found"}, status=404)
        if parking_entry.end_date:
            return Response({"error_msg": "Ticket already returned"}, status=400)

        parking_entry.end_date = timezone.localize(datetime.datetime.now())
        parking_entry.save()

        if parking_entry.billing_type == 'SUB':

            subscription = Subscription.objects.get(client_id=parking_entry.client)

            if parking_entry.end_date > subscription.end_date:

                parking_entry.overtime = parking_entry.end_date - subscription.end_date

                amount = parking_cost.calculate_parking_cost(subscription.end_date, parking_entry.end_date)
                payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)

                parking_entry.save()
                payment.save()

                return Response({"amount": payment.amount})

            elif parking_entry.end_date < subscription.start_date:

                amount = parking_cost.calculate_parking_cost(parking_entry.start_date, parking_entry.end_date)
                payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)
                payment.save()

                return Response({"amount": payment.amount})

            else:
                return Response({"amount": 0})

        elif parking_entry.billing_type == 'VCR':

            parking_time = parking_entry.end_date - parking_entry.start_date

            if parking_time > parking_entry.client.voucher:

                parking_entry.overtime = parking_time - parking_entry.client.voucher
                parking_entry.voucher = datetime.timedelta(seconds=0)

                amount = parking_cost.calculate_parking_cost(parking_entry.start_date + parking_entry.overtime,
                                                             parking_entry.end_date)
                payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)

                parking_entry.save()
                payment.save()

                return Response({"amount": payment.amount, "voucher_time_left": parking_entry.voucher})

            else:
                parking_entry.voucher -= parking_time
                parking_entry.save()

                return Response({"amount": 0, "voucher_time_left": parking_entry.voucher})

        else:
            amount = parking_cost.calculate_parking_cost(parking_entry.start_date, parking_entry.end_date)
            payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)
            payment.save()

            return Response({"amount": payment.amount})

class SubscriptionAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        data = request.data
        plate_num = data["plate_nr"]
        plate_num_max_length = ParkingEntry._meta.get_field('plate_num').max_length

        if not plate_num:
            return Response({"error_msg": "Plate number cannot be empty string."}, status=400)
        if len(plate_num) > plate_num_max_length:
            return Response({"error_msg": f"Plate number cannot be longer then {plate_num_max_length} chars."}, status=400)

        timezone = pytz.timezone(settings.TIME_ZONE)
        date_regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
        if not re.fullmatch(date_regex, data['start_date']) or not re.fullmatch(date_regex, data['end_date']):
            return Response({"error_msg:": "Wrong inputted date format."}, status=400)

        start_date = timezone.localize(datetime.datetime.strptime(data['start_date'], '%Y-%m-%d'))
        end_date = timezone.localize(datetime.datetime.strptime(data['end_date'], '%Y-%m-%d'))

        if start_date > end_date:
            return Response({"error_msg": "Start date cannot be older then end date."}, status=400)
        if start_date > timezone.localize(datetime.datetime(2200, 1, 1)):
            return Response({"error_msg": "Inserted date year value cannot be bigger then 2200"}, status=400)

        client_query = Client.objects.filter(plate_num=plate_num)

        if (client_query.exists()) and not Client.has_subscription_in_range(client_query[0], start_date, end_date):
            return Response({"error_msg": "Already Paid"}, status=400)

        else:
            amount = sub_cost.get_subscription_cost(start_date, end_date)
            return Response({"amount": amount})

class SubPayAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        data = request.data
        plate_num = data["plate_nr"]
        plate_num_max_length = ParkingEntry._meta.get_field('plate_num').max_length

        if not plate_num:
            return Response({"error_msg": "Plate number cannot be empty string."}, status=400)
        if len(plate_num) > plate_num_max_length:
            return Response({"error_msg": f"Plate number cannot be longer then {plate_num_max_length} chars."}, status=400)

        timezone = pytz.timezone(settings.TIME_ZONE)
        date_regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
        if not re.fullmatch(date_regex, data['start_date']) or not re.fullmatch(date_regex, data['end_date']):
            return Response({"error_msg:": "Wrong inputted date format."}, status=400)

        start_date = timezone.localize(datetime.datetime.strptime(data['start_date'], '%Y-%m-%d'))
        end_date = timezone.localize(datetime.datetime.strptime(data['end_date'], '%Y-%m-%d'))

        if start_date > end_date:
            return Response({"error_msg": "Start date cannot be older then end date."}, status=400)
        if start_date > timezone.localize(datetime.datetime(2200, 1, 1)):
            return Response({"error_msg": "Inserted date year value cannot be bigger then 2200"}, status=400)

        if not Subscription.subscriptions_available():
            return Response({"error_msg": "No available subscriptions at the moment."}, status=400)
        if Subscription.max_possible_subscription_time() < (end_date - start_date).days:
            return Response({"error_msg": f"Required subscription range is too big. Currently longest available subscription"
                                          f" is {Subscription.max_possible_subscription_time()} days long."}, status=400)

        client, created = Client.objects.get_or_create(plate_num=data['plate_nr'])

        if not Client.has_subscription_in_range(client, start_date, end_date):
            return Response({"error_msg": "Already Paid"}, status=400)

        amount = sub_cost.get_subscription_cost(start_date, end_date)
        payment = PaymentRegister(amount=amount, status='P')
        payment.save()

        sub = Subscription(client_id=client, start_date=start_date, end_date=end_date, payment_id=payment)
        sub.save()

        return Response({"payment_status": payment.status})

class VoucherAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        data = request.data
        plate_num = data["plate_nr"]
        plate_num_max_length = ParkingEntry._meta.get_field('plate_num').max_length

        if not plate_num:
            return Response({"error_msg": "Plate number cannot be empty string."}, status=400)
        if len(plate_num) > plate_num_max_length:
            return Response({"error_msg": f"Plate number cannot be longer then {plate_num_max_length} chars."}, status=400)

        voucher_hours = data["voucher_hours"]

        if not voucher_hours.isnumeric():
            return Response({"error_msg": "The voucher hours value must be numeric."}, status=400)

        amount = voucher_cost.get_voucher_cost(int(voucher_hours))

        return Response({"amount": amount})

class VoucherPayAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        data = request.data
        plate_num = data["plate_nr"]
        plate_num_max_length = ParkingEntry._meta.get_field('plate_num').max_length

        if not plate_num:
            return Response({"error_msg": "Plate number cannot be empty string."}, status=400)
        if len(plate_num) > plate_num_max_length:
            return Response({"error_msg": f"Plate number cannot be longer then {plate_num_max_length} chars."}, status=400)

        voucher_hours = data["voucher_hours"]

        if not voucher_hours.isnumeric():
            return Response({"error_msg": "The voucher hours value must be numeric."}, status=400)

        client, create = Client.objects.get_or_create(plate_num=plate_num)
        client.voucher += datetime.timedelta(hours=int(voucher_hours))
        client.save()

        return Response({"current_voucher_amount": client.voucher})

class FreeSpotsView(TemplateView):

    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}

class TicketMachineView(TemplateView):

    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}

class SubscriptionView(TemplateView):

    template_name = "subscription.html"
    extra_context = {"hostname": settings.HOSTNAME,
                     "datenow": str(datetime.datetime.now().date()),
                     "maxdate": str(datetime.datetime.now().date() + datetime.timedelta(days=28)),
                     }

class VoucherView(TemplateView):

    template_name = "voucher.html"
    extra_context = {"hostname": settings.HOSTNAME}


