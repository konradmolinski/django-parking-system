import datetime
import pytz
from django.conf import settings
from django.views.generic import TemplateView
from .models import ParkingEntry, PaymentRegister
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from parking.utils import parking_cost


class FreeSpotsAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        return Response({"free_spots": ParkingEntry.free_spots()})


class GetTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        plate_num = request.data
        if ParkingEntry.free_spots():
            entry = ParkingEntry(billing_type="ADH", plate_num=plate_num["plate_nr"])
            entry.save()
            return Response({"ticket_id":entry.id})
        else:
            return Response(plate_num, status=status.HTTP_403_FORBIDDEN)


class ReturnTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        ticket_id = request.data["ticket_id"]
        timezone = pytz.timezone(settings.TIME_ZONE)

        try:
            entry = ParkingEntry.objects.get(id=ticket_id)
            entry.end_date = timezone.localize(datetime.datetime.now())
            entry.save()

            amount = parking_cost.calculate_parking_cost(entry.start_date, entry.end_date)
            payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)
            payment.save()

            return Response({"amount":payment.amount})
        except:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)


class FreeSpotsView(TemplateView):

    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}


class TicketMachineView(TemplateView):

    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}