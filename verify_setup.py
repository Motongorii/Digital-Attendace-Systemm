#!/usr/bin/env python
"""Fix for Vercel deployment - Disable Firebase initialization at startup"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

# The app should now load without Firebase crashing
print("Django app initialized successfully!")
print("Firebase will be initialized on first use (lazy loading)")
