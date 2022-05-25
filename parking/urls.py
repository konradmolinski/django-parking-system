from django.urls import path
from .views import FreeSpotsAPIView, FreeSpotsView, TicketMachineView, TicketMachineAPIView

urlpatterns = [
    path('api/free-spots', FreeSpotsAPIView.as_view({'get': 'retrieve'})),
    path('web/free-spots', FreeSpotsView.as_view()),
    path('api/ticket-machine', TicketMachineAPIView.as_view({'post': 'retrieve'})),
    path('web/ticket-machine', TicketMachineView.as_view()),
]