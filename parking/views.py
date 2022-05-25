from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import ParkingEntry, Client
from django.conf import settings


class ScreenAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})


class UserStoryAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        plate_num = request.data
        if ParkingEntry.free_spots(ParkingEntry):
            entry = ParkingEntry(billing_type="ad hoc", plate_num=plate_num["Plate Number"])
            entry.save()
        return Response(plate_num)

class ParkingSpotsView(TemplateView):
    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}

class UserStoryView(TemplateView):
    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}