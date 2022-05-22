from django.urls import path
from .views import ParkingAPIView, ParkingSpotsView

urlpatterns = [
    path('api/free-spots', ParkingAPIView.as_view({'get': 'retrieve'})),
    path('web/free-spots', ParkingSpotsView.as_view()),
]