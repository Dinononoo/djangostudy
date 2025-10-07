from django.urls import path
from . import views

app_name = 'sensors'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('device/<str:device_id>/', views.device_detail, name='device_detail'),
    path('api/stats/<str:device_id>/', views.api_stats, name='api_stats'),
]
