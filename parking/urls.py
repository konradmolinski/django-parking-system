from django.urls import path
from .views import parkingAPIView

urlpatterns = [
    path('free-spots', parkingAPIView.as_view({'get': 'retrieve'})),
]