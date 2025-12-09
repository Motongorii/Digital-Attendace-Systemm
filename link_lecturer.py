#!/usr/bin/env python
"""
Quick script to link a superuser to a Lecturer profile.
Usage: python manage.py shell < link_lecturer.py
Or: python link_lecturer.py
"""
import os
import django

# Setup Django if running standalone
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
    django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer

def link_admin_to_lecturer():
    """Link the Omuya admin user to a Lecturer profile."""
    try:
        user = User.objects.get(username='Omuya')
        print(f'✓ Found user: {user.username} ({user.email})')
        
        lecturer, created = Lecturer.objects.get_or_create(
            user=user,
            defaults={
                'staff_id': 'STAFF001',
                'department': 'Computer Science',
                'phone': '+254712345678'
            }
        )
        
        if created:
            print(f'✓ Created Lecturer profile: {lecturer}')
        else:
            print(f'✓ Lecturer profile already exists: {lecturer}')
        
        print('✓ Admin user can now access dashboard via /login/')
        return True
    except User.DoesNotExist:
        print('ERROR: User Omuya not found.')
        return False
    except Exception as e:
        print(f'ERROR: {e}')
        return False

if __name__ == '__main__':
    link_admin_to_lecturer()
