from rest_framework import generics, viewsets
from rest_framework.response import Response, Response
from .models import ParkingEntry
import json

class parkingAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})
