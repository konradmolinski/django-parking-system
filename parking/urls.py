from django.urls import path
from .views import FreeSpotsAPIView, FreeSpotsView, TicketMachineView, EnterTicketAPIView, ReturnTicketAPIView

urlpatterns = [
    path('api/free-spots', FreeSpotsAPIView.as_view({'get': 'retrieve'})),
    path('web/free-spots', FreeSpotsView.as_view()),
    path('api/enter-ticket', EnterTicketAPIView.as_view({'post': 'retrieve'})),
    path('web/ticket-machine', TicketMachineView.as_view()),
    path('api/return-ticket', ReturnTicketAPIView.as_view({'post': 'retrieve'})),
]