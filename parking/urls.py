from django.urls import path
from .views import parkingAPIView, home

urlpatterns = [
    path('free-spots', parkingAPIView.as_view({'get': 'retrieve'})),
    path('', home, name='home'),
]