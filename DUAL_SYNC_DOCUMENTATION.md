# Dual-Sync Feature Documentation

## Overview

The Digital Attendance System now includes **automatic dual-synchronization** of student attendance data to both **Firebase** and a **Lecturer Portal API**. This ensures attendance records are maintained in multiple systems simultaneously for redundancy and integration with existing institutional portals.

## Features

### 1. Automatic Student Registration
When a student marks attendance for the first time, they are automatically registered in the system:
- Student record created with admission number, name, email, phone
- Student automatically enrolled in the unit

### 2. Attendance Tracking with Percentage Calculation
For each attendance session:
- Attendance record links student → session
- Automatic attendance percentage calculated (out of 12 lessons per semester)
- Percentage displayed on success page

### 3. Dual-Synchronization
When attendance is marked, data is synced to both systems:
- **Firebase**: Real-time database for quick access
- **Lecturer Portal**: Institutional system via REST API

Each sync system is independent—if one fails, the other still succeeds.

## Models

### Student Model
```python
class Student:
    - admission_number: CharField (unique, indexed)
    - name: CharField
    - email: EmailField (optional)
    - phone: CharField (optional)
    - units: ManyToManyField(Unit)
    - created_at, updated_at: DateTimeField
    
    Methods:
    - get_attendance_percentage(unit=None, semester=1, max_lessons=12)
```

### Attendance Model
```python
class Attendance:
    - student: ForeignKey(Student)
    - session: ForeignKey(AttendanceSession)
    - timestamp: DateTimeField (auto_now_add)
    - synced_to_firebase: BooleanField
    - synced_to_portal: BooleanField
    - firebase_doc_id: CharField
    - portal_response: JSONField
    
    Methods:
    - get_attendance_percentage(max_lessons=12): Returns % for the unit
```

## Sync Services

### DualSyncService
Main orchestration service that coordinates Firebase and Portal syncs.

**Location**: `attendance/sync_service.py`

**Usage**:
```python
from attendance.sync_service import get_dual_sync_service

sync_result = get_dual_sync_service().sync_attendance(student, session)

# Result structure:
{
    'success': bool,
    'firebase': {
        'success': bool,
        'document_id': str,
        'error': str (if failed)
    },
    'portal': {
        'success': bool,
        'document_id': str,
        'error': str (if failed)
    },
    'attendance_percentage': float,
    'attendance_id': str,
    'created': bool
}
```

### PortalSyncService
Handles REST API communication with lecturer portal.

**Configuration** (via environment variables):
```env
LECTURER_PORTAL_API_URL=https://your-portal.example.com
LECTURER_PORTAL_API_KEY=your-api-key
PORTAL_SYNC_TIMEOUT=10
```

**Portal API Endpoints Expected**:

**Endpoint**: `POST /api/attendance/record`
```json
Request:
{
    "action": "record_attendance",
    "student": {
        "admission_number": "ADM/2023/001",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    },
    "attendance": {
        "unit_code": "CS101",
        "unit_name": "Introduction to Programming",
        "date": "2024-12-03",
        "time_slot": "09:00 - 11:00",
        "venue": "Room 101",
        "lecturer_name": "Dr. Smith",
        "timestamp": "2024-12-03T09:30:00",
        "attendance_percentage": 83.33
    },
    "api_key": "your-api-key"
}

Response:
{
    "success": true,
    "id": "attendance-uuid-123",
    "message": "Attendance recorded successfully"
}
```

**Endpoint**: `POST /api/students/bulk-sync`
```json
Request:
{
    "action": "bulk_sync_students",
    "students": [
        {
            "admission_number": "ADM/2023/001",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
    ],
    "api_key": "your-api-key"
}

Response:
{
    "success": true,
    "message": "Bulk sync completed",
    "synced_count": 1
}
```

## Updated Views

### student_attend() - Enhanced Attendance Marking
When a student submits attendance:
1. Form validation (admission number, student name)
2. Check if already marked (Firebase fallback if portal down)
3. **Create/Update Student record**
4. **Enroll student in unit** (if not already)
5. **Call DualSyncService** to sync to both Firebase and Portal
6. Display success page with **attendance percentage**

**Location**: `attendance/views.py` - `student_attend()`

## Configuration

### 1. Basic Setup (Firebase only)
If you don't have a portal, just configure Firebase as before:
```env
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```
The system will gracefully handle missing portal configuration.

### 2. With Lecturer Portal
```env
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
LECTURER_PORTAL_API_URL=https://lec-portal.example.com
LECTURER_PORTAL_API_KEY=sk_test_abcd1234efgh5678
PORTAL_SYNC_TIMEOUT=10
```

### 3. Using Docker
```dockerfile
ENV LECTURER_PORTAL_API_URL=https://lec-portal.example.com
ENV LECTURER_PORTAL_API_KEY=sk_test_abcd1234efgh5678
ENV PORTAL_SYNC_TIMEOUT=10
```

## Database Admin Interface

### Student Management
- **URL**: `/admin/attendance/student/`
- View all registered students with admission numbers
- Search by name or admission number
- Filter by units
- Edit student information
- Manage unit enrollments

### Attendance Management
- **URL**: `/admin/attendance/attendance/`
- View all attendance records
- Filter by date, sync status (Firebase/Portal)
- Search by student name or admission number
- View sync details and error responses
- Monitor sync health

## Error Handling

### Graceful Degradation
- If portal API is down: attendance still syncs to Firebase ✓
- If Firebase is down: attendance still syncs to portal ✓
- If both are down: attendance record created locally, can retry later

### Retry Logic (Future Enhancement)
```python
# Planned: Add Celery tasks for automatic retries
from attendance.sync_service import retry_failed_syncs
retry_failed_syncs()  # Retry all Attendance records where synced_to_portal=False
```

## Monitoring & Logging

### View Sync Status
```python
from attendance.models import Attendance

# Failed Firebase syncs
failed_firebase = Attendance.objects.filter(synced_to_firebase=False)

# Failed Portal syncs
failed_portal = Attendance.objects.filter(synced_to_portal=False)

# Successful syncs
successful = Attendance.objects.filter(synced_to_firebase=True, synced_to_portal=True)
```

### Portal Response Inspection
```python
from attendance.models import Attendance
import json

att = Attendance.objects.first()
print(json.dumps(att.portal_response, indent=2))
# {
#   "success": true,
#   "document_id": "attendance-uuid-123",
#   "message": "Attendance synced to portal successfully"
# }
```

## Testing

### Test in Django Shell
```bash
python manage.py shell
```

```python
from attendance.models import Student, Unit, AttendanceSession, Lecturer
from attendance.sync_service import get_dual_sync_service
from django.contrib.auth.models import User
from datetime import date, time

# Setup test data
user = User.objects.first()
lecturer = Lecturer.objects.get(user=user)
unit = Unit.objects.create(code='TEST101', name='Test Unit', lecturer=lecturer)
session = AttendanceSession.objects.create(
    unit=unit,
    lecturer=lecturer,
    date=date.today(),
    start_time=time(9, 0),
    end_time=time(11, 0),
    venue='Test Room'
)

# Create student
student, _ = Student.objects.get_or_create(
    admission_number='TEST/001',
    defaults={'name': 'Test Student'}
)
student.units.add(unit)

# Test sync
result = get_dual_sync_service().sync_attendance(student, session)
print(result)
```

### Expected Output
```json
{
    "success": true,
    "firebase": {
        "success": true,
        "document_id": "abc123def456",
        "message": "Attendance recorded (local mode - Firebase not connected)"
    },
    "portal": {
        "success": true,
        "message": "Portal sync disabled (no API URL configured)",
        "document_id": "local"
    },
    "attendance_percentage": 100.0,
    "attendance_id": "550e8400-e29b-41d4-a716-446655440000",
    "created": true
}
```

## Attendance Percentage Calculation

### Formula
```
Attendance % = (Classes Attended / Max Lessons per Semester) × 100
Default: Max Lessons = 12 per semester
```

### Example
- Student attends 10 out of 12 lessons
- Percentage = (10 / 12) × 100 = **83.33%**
- Displayed on success page and stored in portal/Firebase

### Custom Maximum
```python
from attendance.models import Student

student = Student.objects.get(admission_number='ADM/2023/001')

# Default 12 lessons
percentage = student.get_attendance_percentage(unit=unit, max_lessons=12)

# Custom 20 lessons
percentage = student.get_attendance_percentage(unit=unit, max_lessons=20)
```

## Deployment Checklist

- [ ] Create `.env` file with portal credentials
- [ ] Run `python manage.py makemigrations`
- [ ] Run `python manage.py migrate`
- [ ] Test Firebase connection
- [ ] Test Portal API connection (or disable with empty URL)
- [ ] Verify attendance recording flow
- [ ] Check admin interface for Student and Attendance models
- [ ] Monitor logs for sync errors
- [ ] Set up alerts for failed syncs (optional)

## Future Enhancements

1. **Celery Tasks**: Async sync with retry logic
2. **Webhooks**: Receive updates from portal
3. **Bulk Attendance Upload**: CSV import with dual-sync
4. **Sync Monitoring Dashboard**: Real-time sync status
5. **Automatic Retry**: Failed syncs auto-retry after delay
6. **Portal Fallback**: If primary portal down, use backup
7. **Audit Logging**: Track all sync operations
8. **API Rate Limiting**: Prevent portal API abuse

## Support

For issues or questions:
1. Check logs in `attendance/logs/`
2. Review `portal_response` field in Attendance admin
3. Run `python manage.py shell` tests above
4. Contact portal API admin for their endpoint status

---
**Last Updated**: 2024-12-03
**Version**: 1.0 - Initial Release
