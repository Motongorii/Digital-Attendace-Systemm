#!/usr/bin/env python
"""
Test login + unit creation flow locally to diagnose redirect issue.
"""
import requests
import re
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
LECTURER_USERNAME = "motog"
LECTURER_PASSWORD = "motog123"

# Create a session to maintain cookies
session = requests.Session()

print("=" * 60)
print("TEST: Login + Unit Creation Flow")
print("=" * 60)

# Step 1: Get login page and extract CSRF token
print("\n[1] GET /login/ to extract CSRF token...")
login_page = session.get(f"{BASE_URL}/login/")
print(f"    Status: {login_page.status_code}")

# Extract CSRF token from HTML
csrf_match = re.search(r'csrfmiddlewaretoken["\']?\s*value=["\']([^"\']+)["\']', login_page.text)
csrf_token = csrf_match.group(1) if csrf_match else None
print(f"    CSRF Token found: {bool(csrf_token)}")
if csrf_token:
    print(f"    Token: {csrf_token[:20]}...")

# Step 2: Login with credentials
print(f"\n[2] POST /login/ with username='{LECTURER_USERNAME}'...")
login_data = {
    'username': LECTURER_USERNAME,
    'password': LECTURER_PASSWORD,
    'csrfmiddlewaretoken': csrf_token
}
login_response = session.post(f"{BASE_URL}/login/", data=login_data, allow_redirects=False)
print(f"    Status: {login_response.status_code}")
print(f"    Redirect: {login_response.headers.get('Location', 'None')}")
print(f"    Cookies: {session.cookies}")

# Step 3: Follow redirect to dashboard
if 'Location' in login_response.headers:
    dashboard_url = urljoin(BASE_URL, login_response.headers['Location'])
    print(f"\n[3] GET {dashboard_url} (following redirect)...")
    dashboard_response = session.get(dashboard_url)
    print(f"    Status: {dashboard_response.status_code}")
    print(f"    Contains 'Welcome': {'Welcome' in dashboard_response.text}")
    print(f"    Contains 'Dashboard': {'Dashboard' in dashboard_response.text or 'dashboard' in dashboard_response.text}")
else:
    print("\n[3] No redirect from login")

# Step 4: Get /unit/create/ page to extract CSRF token
print(f"\n[4] GET /unit/create/ to extract CSRF token...")
create_unit_page = session.get(f"{BASE_URL}/unit/create/")
print(f"    Status: {create_unit_page.status_code}")

# Check if we got redirected to login instead
if "login" in create_unit_page.url or create_unit_page.status_code == 302:
    print("    WARNING: Got redirected! Status suggests login redirect.")
    print(f"    URL: {create_unit_page.url}")

# Extract CSRF token
csrf_match2 = re.search(r'csrfmiddlewaretoken["\']?\s*value=["\']([^"\']+)["\']', create_unit_page.text)
csrf_token2 = csrf_match2.group(1) if csrf_match2 else None
print(f"    CSRF Token found: {bool(csrf_token2)}")
if csrf_token2:
    print(f"    Token: {csrf_token2[:20]}...")

# Step 5: POST to create unit
print(f"\n[5] POST /unit/create/ with unit data...")
unit_data = {
    'code': f'TESTUNIT_{hash("test") % 10000}',
    'name': 'Test Unit',
    'credits': 3,
    'csrfmiddlewaretoken': csrf_token2
}
create_unit_response = session.post(f"{BASE_URL}/unit/create/", data=unit_data, allow_redirects=False)
print(f"    Status: {create_unit_response.status_code}")
print(f"    Redirect: {create_unit_response.headers.get('Location', 'None')}")
print(f"    Cookies: {session.cookies}")

if create_unit_response.status_code == 302:
    redirect_location = create_unit_response.headers.get('Location', '')
    if 'login' in redirect_location:
        print("    ERROR: Redirected to login!")
    else:
        print("    OK: Redirected elsewhere (likely success redirect)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
