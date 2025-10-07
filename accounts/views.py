from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .forms import CustomUserCreationForm
from .models import CustomUser
import json


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'สมัครสมาชิกสำเร็จ! กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชี')
            return redirect('account_login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """API endpoint for user registration"""
    try:
        data = json.loads(request.body)
        form = CustomUserCreationForm(data)
        
        if form.is_valid():
            user = form.save()
            return Response({
                'success': True,
                'message': 'สมัครสมาชิกสำเร็จ! กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชี',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': form.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_user_info(request):
    """API endpoint to get current user info"""
    if request.user.is_authenticated:
        return Response({
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone_number': request.user.phone_number,
            'is_verified': request.user.is_verified,
            'date_joined': request.user.date_joined
        })
    else:
        return Response({
            'message': 'User not authenticated'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def api_logout(request):
    """API endpoint for logout"""
    logout(request)
    return Response({
        'success': True,
        'message': 'ออกจากระบบสำเร็จ'
    })