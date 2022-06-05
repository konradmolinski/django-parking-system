import datetime
import pytz
from django.conf import settings
from django.db.models import Q
from django.views.generic import TemplateView
from .models import ParkingEntry, PaymentRegister, Client, Subscription
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from parking.utils import parking_cost, sub_cost, check_payment



class FreeSpotsAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        return Response({"free_spots": ParkingEntry.free_spots()})


class GetTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        plate_num = request.data["plate_nr"]
        try:
            client = Client.objects.get(plate_num=plate_num)
        except:
            client = Client(plate_num=plate_num)
            client.save()
        try:
            Subscription.objects.get(client_id=client)
            entry = ParkingEntry(billing_type="SUB", plate_num=plate_num, client=client)
            entry.save()
            return Response({"ticket_id":entry.id})
        except:
            if ParkingEntry.free_spots():
                entry = ParkingEntry(billing_type="ADH", plate_num=plate_num, client=client)
                entry.save()
                return Response({"ticket_id":entry.id})
            else:
                return Response(plate_num, status=status.HTTP_403_FORBIDDEN)

class PayAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        data = request.data
        try:
            payment = PaymentRegister.objects.get(parking_entry_id=data['ticket_id'])
            payment.status = data['payment_status']
            payment.save()

            return Response({"payment_status": payment.status})
        except:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)



class ReturnTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        ticket_id = request.data["ticket_id"]
        timezone = pytz.timezone(settings.TIME_ZONE)

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

        else:
            amount = parking_cost.calculate_parking_cost(parking_entry.start_date, parking_entry.end_date)
            payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)
            payment.save()

            return Response({"amount": payment.amount})


class SubscriptionAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        timezone = pytz.timezone(settings.TIME_ZONE)
        data = request.data
        start_date = timezone.localize(datetime.datetime.strptime(data['start_date'], '%Y-%m-%d'))
        end_date = timezone.localize(datetime.datetime.strptime(data['end_date'], '%Y-%m-%d'))

        client, client_created = Client.objects.get_or_create(plate_num=data['plate_nr'])

        if not check_payment.client_has_subscription_in_requested_range(client, start_date, end_date):
            return Response({"error_msg": "Already Paid"}, status=400)

        else:

            amount = sub_cost.calculate_sub_cost(start_date, end_date)
            return Response({"amount": amount})

class SubPayAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        # jesli user juz zaplacil, nie pozwalaj mu, zwroc error 400 - already paid
        timezone = pytz.timezone(settings.TIME_ZONE)
        data = request.data

        start_date = timezone.localize(datetime.datetime.strptime(data['start_date'], '%Y-%m-%d'))
        end_date = timezone.localize(datetime.datetime.strptime(data['end_date'], '%Y-%m-%d'))
        client = Client.objects.get(plate_num=data['plate_nr'])

        if not check_payment.client_has_subscription_in_requested_range(client, start_date, end_date):
            return Response({"error_msg": "Already Paid"}, status=400)

        else:
            amount = sub_cost.calculate_sub_cost(start_date, end_date)

            payment = PaymentRegister(amount=amount, status='P')
            payment.save()

            sub = Subscription(client_id=client, start_date=start_date, end_date=end_date,
                               payment_id=payment)
            sub.save()

            return Response({"payment_status": payment.status})

class FreeSpotsView(TemplateView):

    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}


class TicketMachineView(TemplateView):

    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}

class SubscriptionView(TemplateView):

    template_name = "subscription.html"
    extra_context = {"hostname": settings.HOSTNAME, "datenow": str(datetime.datetime.now().date()),
                     "maxdate": str(datetime.datetime.now().date() + datetime.timedelta(days=28))}

