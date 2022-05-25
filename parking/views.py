from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import ParkingEntry, Client
from django.conf import settings


class FreeSpotsAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})


class TicketMachineAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        plate_num = request.data
        if ParkingEntry.free_spots(ParkingEntry):
            entry = ParkingEntry(billing_type="ADH", plate_num=plate_num["plate_nr"])
            entry.save()
            return Response({"Ticket ID":entry.id})
        else:
            return Response("There are no free parking spots at the moment.")
        # return Response(plate_num)

class FreeSpotsView(TemplateView):
    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}

class TicketMachineView(TemplateView):
    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}