from django.urls import path
from .views import ScreenAPIView, ParkingSpotsView, UserStoryView, UserStoryAPIView

urlpatterns = [
    path('api/free-spots', ScreenAPIView.as_view({'get': 'retrieve'})),
    path('web/free-spots', ParkingSpotsView.as_view()),
    path('api/user-story', UserStoryAPIView),
    path('web/user-story', UserStoryView.as_view()),
]