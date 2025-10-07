#!/usr/bin/env python3
"""
เพิ่มสิทธิ์ Admin ให้ user ที่มีอยู่
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iotdjango.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def make_admin(email):
    """เพิ่มสิทธิ์ admin ให้ user"""
    
    try:
        user = User.objects.get(email=email)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print("="*60)
        print(f"SUCCESS! {email} is now Admin")
        print("="*60)
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Staff: {user.is_staff}")
        print(f"Superuser: {user.is_superuser}")
        print("="*60)
        print("\nYou can now access Admin Panel:")
        print("http://127.0.0.1:8000/admin/")
        print("="*60)
        
    except User.DoesNotExist:
        print(f"ERROR: User {email} not found!")
        print("\nAvailable users:")
        for u in User.objects.all():
            print(f"  - {u.email} (staff: {u.is_staff})")

if __name__ == "__main__":
    # เปลี่ยน email ตรงนี้
    make_admin("nometpawee@gmail.com")
