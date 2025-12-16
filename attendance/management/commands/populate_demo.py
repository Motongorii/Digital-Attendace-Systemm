from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit, AttendanceSession
from attendance.qr_generator import generate_session_qr
from pathlib import Path
import datetime
import os


class Command(BaseCommand):
    help = "Populate demo data (lecturer, unit, attendance session, QR)"

    def handle(self, *args, **options):
        username = os.environ.get('DEMO_LECTURER_USERNAME', 'Motog')
        email = os.environ.get('DEMO_LECTURER_EMAIL', 'motog@example.com')
        base_code = os.environ.get('DEMO_UNIT_CODE', 'CS101')

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(os.environ.get('DEMO_LECTURER_PASSWORD', 'changeme'))
            user.save()

        lecturer, _ = Lecturer.objects.get_or_create(
            user=user,
            defaults={'staff_id': 'STAFF_001', 'department': 'Computer Science', 'phone': '+254700000000'}
        )

        existing = Unit.objects.filter(code=base_code).first()
        if existing and existing.lecturer != lecturer:
            unit_code = f"{base_code}_{lecturer.user.username}"
        else:
            unit_code = base_code

        unit, _ = Unit.objects.get_or_create(
            code=unit_code,
            defaults={'name': 'Introduction to Programming', 'description': 'Fundamentals', 'lecturer': lecturer}
        )

        today = datetime.date.today()
        start_time = datetime.time(9, 0)
        end_time = datetime.time(10, 30)

        session, _ = AttendanceSession.objects.get_or_create(
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

        # Generate QR if missing
        if not session.qr_code or getattr(session.qr_code, 'size', 0) == 0:
            base_url = os.environ.get('SITE_BASE_URL', 'https://'+os.environ.get('ALLOWED_HOSTS','localhost').split(',')[0])
            qr_file = generate_session_qr(session, base_url)
            session.qr_code.save(qr_file.name, qr_file)
            session.save()
            self.stdout.write(self.style.SUCCESS(f'Generated QR for session {session.id}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'QR already exists for session {session.id}'))

        self.stdout.write(self.style.SUCCESS('Demo data populated.'))
