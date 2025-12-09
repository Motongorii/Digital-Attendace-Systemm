from django.contrib.auth.models import User
from attendance.models import Lecturer

u = User.objects.get(username='Motog')
Lecturer.objects.get_or_create(
    user=u,
    defaults={
        'staff_id': 'STAFF_MOTOG',
        'department': 'Computer Science',
        'phone': '+254700000000'
    }
)
print('✓ Lecturer profile created for Motog')
