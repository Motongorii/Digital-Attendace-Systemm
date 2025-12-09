from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit, AttendanceSession
import os

username = 'Motog'
try:
    user = User.objects.get(username=username)
    lecturer = Lecturer.objects.get(user=user)
except (User.DoesNotExist, Lecturer.DoesNotExist):
    print('Motog or Lecturer profile not found, nothing to clean.')
    exit(0)

# Delete test units and sessions
units = Unit.objects.filter(lecturer=lecturer, code__startswith='TEST')
for unit in units:
    print('Deleting unit:', unit.code)
    # Delete sessions and QR files
    for session in unit.sessions.all():
        if session.qr_code:
            qr_path = session.qr_code.path
            if os.path.exists(qr_path):
                os.remove(qr_path)
                print('Deleted QR file:', qr_path)
        session.delete()
    unit.delete()
print('Cleanup complete.')
