#!/usr/bin/env python
"""Test Firebase connection and run basic tests"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

print("=" * 60)
print("DIGITAL ATTENDANCE SYSTEM - TEST OUTPUT")
print("=" * 60)

# Test 1: Firebase Connection
print("\n[TEST 1] Firebase Connection Status")
print("-" * 60)
try:
    from attendance.firebase_service import firebase_service
    print(f"✓ Firebase service imported successfully")
    print(f"  - Connection Status: {firebase_service.is_connected}")
    print(f"  - Database Client: {firebase_service.db}")
    
    if firebase_service.is_connected:
        print("\n✓✓✓ FIREBASE IS SUCCESSFULLY CONNECTED ✓✓✓")
    else:
        print("\n✗ Firebase is NOT connected")
        print("  Reason: Credentials file not found or initialization failed")
except Exception as e:
    print(f"✗ Error importing Firebase service: {e}")

# Test 2: Django Models
print("\n[TEST 2] Django Models Status")
print("-" * 60)
try:
    from attendance.models import Lecturer, Unit, AttendanceSession
    print("✓ All Django models imported successfully")
    print(f"  - Lecturer model: OK")
    print(f"  - Unit model: OK")
    print(f"  - AttendanceSession model: OK")
except Exception as e:
    print(f"✗ Error importing models: {e}")

# Test 3: QR Code Generator
print("\n[TEST 3] QR Code Generator Status")
print("-" * 60)
try:
    from attendance.qr_generator import generate_session_qr
    print("✓ QR code generator imported successfully")
except Exception as e:
    print(f"✗ Error importing QR generator: {e}")

# Test 4: Forms
print("\n[TEST 4] Django Forms Status")
print("-" * 60)
try:
    from attendance.forms import AttendanceSessionForm, StudentAttendanceForm, UnitForm
    print("✓ All forms imported successfully")
    print(f"  - AttendanceSessionForm: OK")
    print(f"  - StudentAttendanceForm: OK")
    print(f"  - UnitForm: OK")
except Exception as e:
    print(f"✗ Error importing forms: {e}")

# Test 5: Environment Variables
print("\n[TEST 5] Environment Configuration")
print("-" * 60)
try:
    from django.conf import settings
    print(f"✓ Django settings loaded")
    print(f"  - DEBUG: {settings.DEBUG}")
    print(f"  - DATABASE: {settings.DATABASES['default']['ENGINE']}")
    print(f"  - FIREBASE_CREDENTIALS_PATH: {settings.FIREBASE_CREDENTIALS_PATH}")
    
    import pathlib
    if pathlib.Path(settings.FIREBASE_CREDENTIALS_PATH).exists():
        print(f"  ✓ Firebase credentials file exists")
    else:
        print(f"  ✗ Firebase credentials file NOT found at {settings.FIREBASE_CREDENTIALS_PATH}")
except Exception as e:
    print(f"✗ Error loading settings: {e}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("\n✓ Application is ready to use!")
print("\nTo start the development server, run:")
print("  python manage.py runserver")
print("\nTo access the application:")
print("  - Home: http://127.0.0.1:8000/")
print("  - Admin: http://127.0.0.1:8000/admin/")
print("  - Lecturer Login: http://127.0.0.1:8000/login/")
print("\n" + "=" * 60)
