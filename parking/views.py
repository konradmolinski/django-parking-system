from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ParkingEntry
from .serializers import UserStorySerializer
from django.conf import settings


class ScreenAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        free_spots = ParkingEntry.free_spots(ParkingEntry)
        return Response({"free_spots": free_spots})


class UserStoryAPIView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        plate_num = request.data
        return Response(plate_num)
# @api_view(['POST'])
# def UserStoryAPIView(request):
#     serializer = UserStorySerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)

class ParkingSpotsView(TemplateView):
    template_name = "free_spots.html"
    extra_context = {"hostname": settings.HOSTNAME}

class UserStoryView(TemplateView):
    template_name = "user_story.html"
    extra_context = {"hostname": settings.HOSTNAME}