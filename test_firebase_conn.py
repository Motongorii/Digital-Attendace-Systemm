#!/usr/bin/env python
"""Quick test of Firebase connectivity."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.firebase_service import get_firebase_service

fb = get_firebase_service()
print('is_connected:', fb.is_connected)

if not fb.is_connected:
    print('Firebase not connected - check credentials and environment variables')
    sys.exit(1)

try:
    db = fb.db
    print('db client type:', type(db).__name__)
    cols = [c.id for c in db.collections()]
    print('collections found:', cols)
    print('\n✓ Firebase connectivity OK')
except Exception as e:
    print('Error:', e)
    sys.exit(1)
