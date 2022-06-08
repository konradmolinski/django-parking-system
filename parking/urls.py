from django.urls import path
from .views import (FreeSpotsAPIView, FreeSpotsView, TicketMachineView, GetTicketAPIView, ReturnTicketAPIView,\
    PayAPIView, SubscriptionView, SubscriptionAPIView, SubPayAPIView, SubscriptionsInfoAPIView)

urlpatterns = [
    path('api/free-spots', FreeSpotsAPIView.as_view({'get': 'retrieve'})),
    path('api/sub-info', SubscriptionsInfoAPIView.as_view({'get': 'retrieve'})),
    path('api/get-ticket', GetTicketAPIView.as_view({'post': 'retrieve'})),
    path('api/return-ticket', ReturnTicketAPIView.as_view({'post': 'retrieve'})),
    path('api/pay', PayAPIView.as_view({'post': 'retrieve'})),
    path('api/subscription', SubscriptionAPIView.as_view({'post': 'retrieve'})),
    path('api/pay-sub', SubPayAPIView.as_view({'post': 'retrieve'})),

    path('web/free-spots', FreeSpotsView.as_view()),
    path('web/ticket-machine', TicketMachineView.as_view()),
    path('web/subscription', SubscriptionView.as_view()),
]
