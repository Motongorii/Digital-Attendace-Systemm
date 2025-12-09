import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
import django
django.setup()
exec(open('cleanup_test_data.py').read())
