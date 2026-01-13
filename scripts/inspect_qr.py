import os
import django
from django.conf import settings
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import AttendanceSession

s = AttendanceSession.objects.filter(qr_code__isnull=False).order_by('-date').first()
if not s:
    print('No session with QR found')
else:
    print('Session', s.id, 'qr', s.qr_code.name)
    img_bytes = s.qr_code.read()
    img = Image.open(BytesIO(img_bytes))
    print('format', img.format, 'size', img.size, 'mode', img.mode)
    out_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', 'inspect_test.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print('Saved', out_path)
