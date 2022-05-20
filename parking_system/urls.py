from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('parking.urls')),
    path('', include('parking.urls')),
]
