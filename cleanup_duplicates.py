#!/usr/bin/env python
"""Clean up duplicate attendance sessions before migration"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

from attendance.models import AttendanceSession
from django.db.models import Count

# Find duplicates
duplicates = AttendanceSession.objects.values('unit_id', 'semester', 'date', 'start_time').annotate(count=Count('id')).filter(count__gt=1)

print(f"Found {duplicates.count()} duplicate session combinations:")
for dup in duplicates:
    print(f"  Unit {dup['unit_id']}, Semester {dup['semester']}, {dup['date']} {dup['start_time']}")
    sessions = AttendanceSession.objects.filter(
        unit_id=dup['unit_id'],
        semester=dup['semester'],
        date=dup['date'],
        start_time=dup['start_time']
    ).order_by('-created_at')
    for i, s in enumerate(sessions):
        print(f"    [{i}] {s.id} - created: {s.created_at} - attendees: {s.attendance_records.count()}")

print("\nKeeping newest sessions and deleting older duplicates...")
deleted_count = 0
for dup in duplicates:
    sessions = AttendanceSession.objects.filter(
        unit_id=dup['unit_id'],
        semester=dup['semester'],
        date=dup['date'],
        start_time=dup['start_time']
    ).order_by('-created_at')
    
    # Keep the first (newest), delete the rest
    to_delete = sessions[1:]
    for s in to_delete:
        print(f"  Deleting {s.id} (created: {s.created_at})")
        s.delete()
        deleted_count += 1

print(f"\n✓ Deleted {deleted_count} duplicate sessions")
