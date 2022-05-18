from django.urls import path
from .views import parkingAPIView

urlpatterns = [
    path('', parkingAPIView.as_view({'get': 'retrieve'})),
]