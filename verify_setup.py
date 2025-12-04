#!/usr/bin/env python
"""Setup verification - Initialize Django app"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

print("Django app initialized successfully!")
