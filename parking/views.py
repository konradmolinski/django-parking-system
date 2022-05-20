from rest_framework import generics, viewsets
from rest_framework.response import Response, Response
from .models import ParkingEntry
from django.shortcuts import render
import requests
import json

class parkingAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})

def home(request):
    res = requests.get('http://127.0.0.1:8000/api/free-spots').json()
    return render(request, 'parking/home.html', {
        'free_spots': res['free_spots']
    })
