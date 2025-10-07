from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_verified', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('ข้อมูลส่วนตัว', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        ('สิทธิ์', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('วันที่สำคัญ', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2'),
        }),
    )