#!/usr/bin/env python3
"""
สร้าง Superuser สำหรับ Admin Panel
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iotdjango.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """สร้าง superuser"""
    
    email = "admin@example.com"
    password = "admin123"
    
    # ตรวจสอบว่ามีอยู่แล้วหรือไม่
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Updated existing user: {email}")
    else:
        user = User.objects.create_superuser(
            username="admin",
            email=email,
            password=password,
            first_name="Admin",
            last_name="User"
        )
        print(f"Created superuser: {email}")
    
    print("\n" + "="*60)
    print("Superuser Details:")
    print("="*60)
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Staff: {user.is_staff}")
    print(f"Superuser: {user.is_superuser}")
    print("="*60)
    print("\nLogin to Admin Panel:")
    print("http://127.0.0.1:8000/admin/")
    print("="*60)

if __name__ == "__main__":
    create_superuser()

