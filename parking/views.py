from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import ParkingEntry
from django.conf import settings


class ParkingAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})


class ParkingSpotsView(TemplateView):
    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}
