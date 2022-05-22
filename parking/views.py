from django.views.generic import TemplateView
from rest_framework import generics, viewsets
from rest_framework.response import Response, Response
from .models import ParkingEntry




class parkingAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})

class parkingSpotsView(TemplateView):
    template_name = "free_spots.html"
