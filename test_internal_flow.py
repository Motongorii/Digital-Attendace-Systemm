#!/usr/bin/env python
"""
Internal test using Django test Client to reproduce login -> create unit POST behavior without starting the dev server.
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit
from django.test import Client
from django.contrib.messages import get_messages

USERNAME = 'motog'
PASSWORD = 'motog123'

print('='*60)
print('INTERNAL TEST: Django test Client (no network)')
print('='*60)

# Ensure user exists
user, created = User.objects.get_or_create(username=USERNAME, defaults={'email':'motog@example.com','first_name':'Motog'})
if created:
    user.set_password(PASSWORD)
    user.save()
    print('Created test user')
else:
    # reset password to known value to ensure login succeeds
    user.set_password(PASSWORD)
    user.save()
    print('Ensured test user password')

# Ensure Lecturer profile exists
lecturer = None
try:
    lecturer = user.lecturer
    print('Lecturer profile exists')
except Exception:
    lecturer = Lecturer.objects.create(user=user, staff_id='MOTOG')
    print('Created Lecturer profile')

# Use test client with CSRF checks enabled to emulate browser
client = Client(enforce_csrf_checks=True)

# Step 1: GET login page to obtain CSRF cookie
resp = client.get('/login/')
print('\n[GET /login/] status:', resp.status_code)
print('Cookies:', client.cookies.keys())
csrfcookie = client.cookies.get('csrftoken')
print('CSRF cookie present:', bool(csrfcookie))

# Extract csrf token from response context if available
# Prefer token from cookie; context may be None in some views
csrfcookie = client.cookies.get('csrftoken')
csrf_token = csrfcookie.value if csrfcookie else None
print('CSRF token available (from cookie):', bool(csrf_token))

# Step 2: POST credentials to login
login_data = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrf_token or (csrfcookie.value if csrfcookie else '')
}
resp2 = client.post('/login/', login_data, follow=True)
print('\n[POST /login/] status:', resp2.status_code)
print('Redirect chain:', resp2.redirect_chain)
print('Session key after login:', client.session.session_key)

# Is authenticated?
user_obj = None
try:
    user_obj = resp2.context.get('user')
    print('Response user authenticated:', user_obj.is_authenticated)
except Exception:
    print('No user in response context')

# Step 3: GET /unit/create/ to get CSRF token for form
resp3 = client.get('/unit/create/')
print('\n[GET /unit/create/] status:', resp3.status_code)
print('URL after GET:', resp3.request.get('PATH_INFO'))
csrfcookie2 = client.cookies.get('csrftoken')
print('CSRF cookie present before POST:', bool(csrfcookie2))
csrf_form_token = None
if resp3.context and 'form' in resp3.context:
    # The template uses csrf_token tag; test client may not expose it directly
    pass

# Step 4: POST to create unit
post_data = {
    'code': f'TESTCLI_{os.getpid()}',
    'name': 'Test Unit From Client',
    'description': 'Created by internal test',
    'csrfmiddlewaretoken': csrfcookie2.value if csrfcookie2 else ''
}
resp4 = client.post('/unit/create/', post_data, follow=True)
print('\n[POST /unit/create/] status:', resp4.status_code)
print('Redirect chain:', resp4.redirect_chain)
# Print messages if available
try:
    messages = [m.message for m in get_messages(resp4.wsgi_request)]
    print('Messages:', messages)
except Exception:
    print('No messages available')

# Check if unit was created
exists = Unit.objects.filter(code=post_data['code']).exists()
print('Unit created in DB:', exists)

print('\nTest complete')
print('='*60)
