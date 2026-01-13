import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer

def create_lecturer(username, password, email, staff_id, department, phone):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ User '{username}' created")
    else:
        user.set_password(password)
        user.save()
        print(f"✓ User '{username}' password updated")
    lec, lec_created = Lecturer.objects.get_or_create(
        user=user,
        defaults={'staff_id': staff_id, 'department': department, 'phone': phone}
    )
    if lec_created:
        print(f"✓ Lecturer profile created for '{username}'")
    else:
        print(f"✓ Lecturer profile already exists for '{username}'")

create_lecturer("John", "jon@123", "john@example.com", "LEC002", "Math", "0700000001")
create_lecturer("Faith", "fai@123", "faith@example.com", "LEC003", "Science", "0700000002")
