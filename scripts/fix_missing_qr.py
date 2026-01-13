import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import AttendanceSession
from attendance.qr_generator import generate_session_qr
from django.conf import settings

base_url = getattr(settings, 'SITE_BASE_URL', 'http://127.0.0.1:8000')

sessions = AttendanceSession.objects.exclude(qr_code__isnull=True)
missing = []
for s in sessions:
    name = s.qr_code.name
    path = os.path.join(settings.MEDIA_ROOT, name) if name else None
    if not name or not os.path.exists(path):
        print('Missing for session', s.id, 'regenerating...')
        qr_file = generate_session_qr(s, base_url=base_url)
        s.qr_code.save(qr_file.name, qr_file, save=True)
        print('Saved new QR:', s.qr_code.name)
        missing.append(s.id)

if not missing:
    print('No missing QR files found')
else:
    print('Regenerated for sessions:', missing)
