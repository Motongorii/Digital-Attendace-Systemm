#!/usr/bin/env python
"""Create admin user for testing"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer

print("=" * 60)
print("CREATING ADMIN USER FOR DIGITAL ATTENDANCE SYSTEM")
print("=" * 60)

# Create superuser (admin can access both admin panel and lecturer dashboard)
username = "admin"
email = "admin@attendance.com"
password = "Admin@123456"  # This is the superuser and lecturer dashboard account

try:
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"\n✓ User '{username}' already exists")
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_superuser(username, email, password)
        print(f"\n✓ Superuser '{username}' created successfully")
    
    # Create Lecturer profile if not exists
    if not Lecturer.objects.filter(user=user).exists():
        lecturer = Lecturer.objects.create(
            user=user,
            staff_id="STAFF001",
            department="Computer Science",
            phone="+254712345678"
        )
        print(f"✓ Lecturer profile created for {username}")
    else:
        print(f"✓ Lecturer profile already exists for {username}")
    
    print("\n" + "=" * 60)
    print("LOGIN CREDENTIALS")
    print("=" * 60)
    print(f"\nUsername: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print("\nAccess URLs:")
    print(f"  - Admin Panel: http://127.0.0.1:8000/admin/")
    print(f"  - Lecturer Dashboard: http://127.0.0.1:8000/dashboard/")
    print(f"  - Lecturer Login: http://127.0.0.1:8000/login/")
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n✗ Error creating user: {e}")
    sys.exit(1)
