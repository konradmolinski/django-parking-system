from django.urls import path
from .views import FreeSpotsAPIView, FreeSpotsView, TicketMachineView, GetTicketAPIView, ReturnTicketAPIView

urlpatterns = [
    path('api/free-spots', FreeSpotsAPIView.as_view({'get': 'retrieve'})),
    path('web/free-spots', FreeSpotsView.as_view()),
    path('api/get-ticket', GetTicketAPIView.as_view({'post': 'retrieve'})),
    path('web/ticket-machine', TicketMachineView.as_view()),
    path('api/return-ticket', ReturnTicketAPIView.as_view({'post': 'retrieve'})),
]