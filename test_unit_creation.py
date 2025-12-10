#!/usr/bin/env python
"""
Test unit creation via AJAX endpoint to diagnose the issue.
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit

# Create a test user if needed
user, created = User.objects.get_or_create(
    username='testlecturer',
    defaults={'first_name': 'Test', 'last_name': 'Lecturer'}
)

# Ensure lecturer profile exists
lecturer, created = Lecturer.objects.get_or_create(
    user=user,
    defaults={'staff_id': 'TEST_STAFF_001', 'department': 'Test Department'}
)

print(f"✓ Test user and lecturer ready: {user.username}, {lecturer}")

# Create test client
client = Client()

# Step 1: Login
print("\n[1] Logging in...")
login_ok = client.login(username='testlecturer', password='testlecturer')
print(f"    Login result: {login_ok}")

if not login_ok:
    # Try with default password or create one
    user.set_password('Test@12345')
    user.save()
    login_ok = client.login(username='testlecturer', password='Test@12345')
    print(f"    Retry login with new password: {login_ok}")

# Step 2: Test AJAX unit creation
print("\n[2] Testing AJAX unit creation via POST /unit/create-ajax/...")
unit_data = {
    'code': f'TEST_AJAX_UNIT_{os.getpid()}',
    'name': 'Test AJAX Unit',
    'description': 'Testing AJAX endpoint'
}

response = client.post(
    '/unit/create-ajax/',
    data=unit_data,
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

print(f"    Status: {response.status_code}")
print(f"    Response type: {response.get('Content-Type', 'unknown')}")

try:
    json_response = json.loads(response.content)
    print(f"    Response JSON: {json_response}")
    
    if json_response.get('success'):
        print(f"    ✓ SUCCESS: Unit created! ID: {json_response['unit']['id']}")
    else:
        print(f"    ✗ FAILED: {json_response.get('error', json_response.get('errors'))}")
except json.JSONDecodeError as e:
    print(f"    ✗ JSON parse error: {e}")
    print(f"    Raw response: {response.content[:500]}")

# Step 3: Check if unit exists in database
print("\n[3] Checking if unit exists in database...")
unit_exists = Unit.objects.filter(code=unit_data['code']).exists()
print(f"    Unit exists: {unit_exists}")

if unit_exists:
    unit = Unit.objects.get(code=unit_data['code'])
    print(f"    ✓ Unit found: {unit.code} - {unit.name}")
    print(f"    Lecturer: {unit.lecturer.user.username}")
else:
    print(f"    ✗ Unit NOT found in database")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
