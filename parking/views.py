from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import ParkingEntry, PaymentRegister
from django.conf import settings
import datetime
import pytz


class FreeSpotsAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        return Response({"free_spots": ParkingEntry.free_spots()})


class EnterTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        plate_num = request.data
        extra_context = {"200": status.HTTP_200_OK, "403": status.HTTP_403_FORBIDDEN}
        if ParkingEntry.free_spots():
            entry = ParkingEntry(billing_type="ADH", plate_num=plate_num["plate_nr"])
            entry.save()
            return Response({"ticket_id":entry.id})
        else:
            return Response(plate_num, status=status.HTTP_403_FORBIDDEN)


class ReturnTicketAPIView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):

        ticket_id = request.data["ticket_id"]
        timezone = pytz.timezone("UTC")
        extra_context = {"200": status.HTTP_200_OK, "403": status.HTTP_403_FORBIDDEN}

        if ParkingEntry.objects.all().filter(id=ticket_id):

            entry = ParkingEntry.objects.get(id=ticket_id)
            entry.end_date = timezone.localize(datetime.datetime.now())
            entry.save()

            amount = PaymentRegister.calculate_parking_cost(entry.start_date, entry.end_date)
            payment = PaymentRegister(parking_entry_id=ticket_id, amount=amount)
            payment.save()
            return Response({"amount":payment.amount})

        else:

            return Response(ticket_id, status=status.HTTP_403_FORBIDDEN)


class FreeSpotsView(TemplateView):

    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}


class TicketMachineView(TemplateView):

    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}