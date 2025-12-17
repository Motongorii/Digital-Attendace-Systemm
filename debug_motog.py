#!/usr/bin/env python
"""Debug script to check and fix Motog user and Lecturer profile in production."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer

print("=" * 60)
print("DEBUGGING MOTOG USER AND LECTURER PROFILE")
print("=" * 60)

# Check if Motog user exists
motog_users = User.objects.filter(username='Motog')
print(f"\n1. Motog user exists: {motog_users.exists()}")
if motog_users.exists():
    u = motog_users.first()
    print(f"   Email: {u.email}")
    print(f"   Is superuser: {u.is_superuser}")
    print(f"   Is staff: {u.is_staff}")
else:
    print("   ERROR: Motog user not found!")

# Check if Lecturer profile exists
lecturer = Lecturer.objects.filter(user__username='Motog')
print(f"\n2. Lecturer profile exists: {lecturer.exists()}")
if lecturer.exists():
    l = lecturer.first()
    print(f"   Staff ID: {l.staff_id}")
    print(f"   Department: {l.department}")
else:
    print("   Lecturer profile NOT found. Creating one...")
    try:
        u = User.objects.get(username='Motog')
        l, created = Lecturer.objects.get_or_create(
            user=u,
            defaults={
                'staff_id': 'STAFF_MOTOG',
                'department': 'Computer Science',
                'phone': '+254700000000'
            }
        )
        if created:
            print(f"   ✓ Created Lecturer profile: {l}")
        else:
            print(f"   ✓ Lecturer profile already exists: {l}")
    except User.DoesNotExist:
        print("   ERROR: Motog user not found, cannot create Lecturer profile!")

# List all users
all_users = User.objects.values_list('username', flat=True)
print(f"\n3. All users in database: {list(all_users)}")

print("\n" + "=" * 60)
print("DEBUG COMPLETE")
print("=" * 60)
