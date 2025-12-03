#!/usr/bin/env python
"""Diagnose attendance URL routing"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

from django.urls import resolve, reverse
from attendance.models import AttendanceSession
import uuid

print("=" * 60)
print("ATTENDANCE URL ROUTING DIAGNOSIS")
print("=" * 60)

# Test URL patterns
print("\n[TEST 1] URL Pattern Resolution")
print("-" * 60)

test_uuid = str(uuid.uuid4())
test_path = f"/attend/{test_uuid}/"

try:
    match = resolve(test_path)
    print(f"✓ Path '{test_path}' resolves correctly")
    print(f"  - View: {match.func.__name__}")
    print(f"  - Args: {match.args}")
    print(f"  - Kwargs: {match.kwargs}")
except Exception as e:
    print(f"✗ Path '{test_path}' does NOT resolve")
    print(f"  Error: {e}")

# Test reverse URL generation
print("\n[TEST 2] Reverse URL Generation")
print("-" * 60)

try:
    url = reverse('student_attend', kwargs={'session_id': test_uuid})
    print(f"✓ Reverse URL generated successfully")
    print(f"  URL: {url}")
except Exception as e:
    print(f"✗ Error generating reverse URL: {e}")

# Test with actual sessions
print("\n[TEST 3] Existing Sessions")
print("-" * 60)

sessions = AttendanceSession.objects.all()[:3]
if sessions:
    for session in sessions:
        print(f"\nSession: {session.id}")
        print(f"  - Unit: {session.unit.name}")
        print(f"  - Is Active: {session.is_active}")
        print(f"  - QR Code: {session.qr_code.name if session.qr_code else 'Not generated'}")
        
        # Test this session's URL
        session_url = reverse('student_attend', kwargs={'session_id': session.id})
        print(f"  - Attendance URL: {session_url}")
        
        # Verify it resolves
        try:
            match = resolve(session_url)
            print(f"  ✓ URL resolves correctly")
        except Exception as e:
            print(f"  ✗ URL does NOT resolve: {e}")
else:
    print("No sessions found in database")

print("\n" + "=" * 60)
