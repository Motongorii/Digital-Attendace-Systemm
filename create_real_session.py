import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
import django
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit, AttendanceSession
from attendance.qr_generator import generate_session_qr
import datetime

username = 'Motog'
try:
    user = User.objects.get(username=username)
except User.DoesNotExist:
    print(f'User {username} not found. Aborting.')
    exit(1)

# Ensure lecturer profile exists
lecturer, _ = Lecturer.objects.get_or_create(
    user=user,
    defaults={'staff_id': 'STAFF_001', 'department': 'Computer Science', 'phone': '+254700000000'}
)
print(f'✓ Lecturer profile: {lecturer}')

# Create or select a unit for Motog. If the base code exists for another lecturer,
# create a unique code to avoid the UNIQUE constraint on `code`.
base_code = 'CS101'
existing = Unit.objects.filter(code=base_code).first()
if existing and existing.lecturer != lecturer:
    unit_code = f"{base_code}_{lecturer.user.username}"
else:
    unit_code = base_code

unit, unit_created = Unit.objects.get_or_create(
    code=unit_code,
    defaults={'name': 'Introduction to Programming', 'description': 'Fundamentals of programming', 'lecturer': lecturer}
)
# Ensure lecturer is set for the unit (in case existing unit was found without lecturer)
if unit.lecturer != lecturer:
    unit.lecturer = lecturer
    unit.save()

print(f"{('✓ Created' if unit_created else '✓ Exists')} Unit: {unit}")

# Create a session for today
today = datetime.date.today()
start_time = datetime.time(9, 0)
end_time = datetime.time(10, 30)
session, session_created = AttendanceSession.objects.get_or_create(
    unit=unit,
    lecturer=lecturer,
    date=today,
    start_time=start_time,
    defaults={
        'end_time': end_time,
        'venue': 'Room 101',
        'lecturer_name': user.get_full_name() or user.username,
        'class_year': 'Year 1',
        'semester': 1,
        'session_number': 1,
    }
)
print(f'{"✓ Created" if session_created else "✓ Exists"} Session: {session.id}')

# Generate QR if not already generated
if not session.qr_code or session.qr_code.size == 0:
    base_url = 'https://digital-attendance-system.fly.dev'
    qr_file = generate_session_qr(session, base_url)
    session.qr_code.save(qr_file.name, qr_file)
    session.save()
    print(f'✓ Generated QR: {session.qr_code.name}')
else:
    print(f'✓ QR already exists: {session.qr_code.name}')

print(f'\n✓ Session ready:')
print(f'  URL: https://digital-attendance-system.fly.dev/attend/{session.id}/')
print(f'  QR file: {session.qr_code.name}')
print(f'  Dashboard: https://digital-attendance-system.fly.dev/dashboard/')
