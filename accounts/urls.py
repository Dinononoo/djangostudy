from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    
    # API endpoints
    path('api/register/', views.api_register, name='api_register'),
    path('api/user-info/', views.api_user_info, name='api_user_info'),
    path('api/logout/', views.api_logout, name='api_logout'),
]
