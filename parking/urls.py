from django.urls import path
from .views import parkingAPIView, parkingSpotsView

urlpatterns = [
    path('api/free-spots', parkingAPIView.as_view({'get': 'retrieve'})),
    path('web/free-spots', parkingSpotsView.as_view()),
]