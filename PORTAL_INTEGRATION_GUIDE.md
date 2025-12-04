# Lecturer Portal API Integration Guide

## Quick Start for Portal API Integration

If you already have a lecturer portal and want to integrate it with the Digital Attendance System, follow this guide.

## Step 1: Portal API Requirements

Your lecturer portal needs to provide two REST API endpoints:

### Endpoint 1: Record Single Attendance
```
POST /api/attendance/record
```

**Request Headers**:
```
Content-Type: application/json
Authorization: Bearer {API_KEY}
```

**Request Body**:
```json
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
  "api_key": "{API_KEY}"
}
```

**Expected Response (Success)**:
```json
{
  "success": true,
  "id": "attendance-uuid-123",
  "message": "Attendance recorded successfully"
}
```

**Expected Response (Error)**:
```json
{
  "success": false,
  "error": "Student not found in portal database",
  "message": "Failed to record attendance"
}
```

### Endpoint 2: Bulk Sync Students (Optional)
```
POST /api/students/bulk-sync
```

**Request Body**:
```json
{
  "action": "bulk_sync_students",
  "students": [
    {
      "admission_number": "ADM/2023/001",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    {
      "admission_number": "ADM/2023/002",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+1987654321"
    }
  ],
  "api_key": "{API_KEY}"
}
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Bulk sync completed",
  "synced_count": 2
}
```

## Step 2: Generate API Key

1. Log in to your portal as admin
2. Navigate to Settings → API Keys
3. Generate a new key for the attendance system
4. Copy the key (you'll need it in Step 3)

## Step 3: Configure Environment Variables

Create a `.env` file in the project root or update your existing one:

```env
# Firebase Configuration (existing)
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

# Portal API Configuration (NEW)
LECTURER_PORTAL_API_URL=https://your-portal-domain.com
LECTURER_PORTAL_API_KEY=your-api-key-here
PORTAL_SYNC_TIMEOUT=10
```

**Environment Variable Details**:
- `LECTURER_PORTAL_API_URL`: The base URL of your portal (required for sync)
- `LECTURER_PORTAL_API_KEY`: API key from your portal (required for sync)
- `PORTAL_SYNC_TIMEOUT`: Timeout in seconds (default: 10)

## Step 4: Restart Django

```bash
python manage.py runserver
```

## Step 5: Test the Integration

### Test via Django Admin
1. Go to http://localhost:8000/admin
2. Navigate to **Attendance → Students**
3. Create a test student (admission: TEST/001, name: Test User)
4. Navigate to **Attendance → Attendance Sessions**
5. Create a test session or use existing one
6. Navigate to **Attendance → Attendances**
7. Create an attendance record manually

Watch the logs for sync output.

### Test via Shell
```bash
python manage.py shell
```

```python
from attendance.models import Student, AttendanceSession, Unit, Lecturer
from attendance.sync_service import get_dual_sync_service
from django.contrib.auth.models import User
from datetime import date, time

# Create/get test data
lecturer = Lecturer.objects.first()
unit = Unit.objects.filter(lecturer=lecturer).first()
session = AttendanceSession.objects.filter(unit=unit).first()
student, _ = Student.objects.get_or_create(
    admission_number='SHELL/TEST/001',
    defaults={'name': 'Shell Test User'}
)
student.units.add(unit)

# Sync
result = get_dual_sync_service().sync_attendance(student, session)

# Print result
import json
print(json.dumps(result, indent=2, default=str))
```

### Expected Output
```json
{
  "success": true,
  "firebase": {
    "success": true,
    "document_id": "abc123...",
    "message": "Attendance recorded successfully"
  },
  "portal": {
    "success": true,
    "document_id": "def456...",
    "message": "Attendance synced to portal successfully"
  },
  "attendance_percentage": 100.0,
  "attendance_id": "ghi789...",
  "created": true
}
```

## Step 6: Monitor Sync Status

### Check Failed Syncs in Admin
1. Go to **Attendance → Attendances**
2. Filter by **Synced to portal**: False
3. Review the `portal_response` field to see error details

### View All Sync Details
```python
from attendance.models import Attendance
import json

# Get last attendance record
att = Attendance.objects.latest('timestamp')

print(f"Created: {att.timestamp}")
print(f"Synced to Firebase: {att.synced_to_firebase}")
print(f"Synced to Portal: {att.synced_to_portal}")
print(f"\nPortal Response:")
print(json.dumps(att.portal_response, indent=2))
```

## Troubleshooting

### Issue: "Portal sync disabled (no API URL configured)"
**Solution**: Add `LECTURER_PORTAL_API_URL` to `.env`

### Issue: "Failed to connect to portal"
**Solution**: 
- Check if portal URL is correct
- Verify portal is running and accessible
- Check firewall/network connectivity
- Verify API key is correct

### Issue: "Portal returned error"
**Solution**:
- Check `portal_response` field in Attendance admin
- Verify student exists in portal database
- Check portal logs for detailed error

### Issue: Connection timeout
**Solution**:
- Increase `PORTAL_SYNC_TIMEOUT` value (in seconds)
- Check if portal API is slow or overloaded
- Verify network latency to portal

## Monitoring & Logging

### View Sync Logs
```bash
# On Windows
Get-EventLog -LogName Application | grep "Attendance"

# On Linux
journalctl -u django_attendance
```

### Database Queries for Monitoring
```python
from attendance.models import Attendance
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

# Failed syncs in last 24 hours
failed = Attendance.objects.filter(
    Q(synced_to_firebase=False) | Q(synced_to_portal=False),
    timestamp__gte=timezone.now() - timedelta(hours=24)
)

print(f"Failed syncs: {failed.count()}")
for att in failed:
    print(f"  - {att.student.name}: {att.portal_response.get('error', 'Unknown')}")

# Success rate
total = Attendance.objects.count()
success = Attendance.objects.filter(synced_to_firebase=True, synced_to_portal=True).count()
print(f"\nSync Success Rate: {success}/{total} ({100*success/total:.1f}%)")
```

## Advanced: Handling Portal Failures

### Graceful Fallback
The system automatically handles portal failures:
- If portal API is down → Firebase sync still succeeds ✓
- If Firebase is down → Portal sync still succeeds ✓
- Records are created locally even if both fail

### Retry Failed Syncs
```python
from attendance.models import Attendance
from attendance.sync_service import get_dual_sync_service

# Get failed records
failed = Attendance.objects.filter(synced_to_portal=False)

# Retry
for att in failed:
    result = get_dual_sync_service().sync_attendance(att.student, att.session)
    if result['portal']['success']:
        att.synced_to_portal = True
        att.portal_response = result['portal']
        att.save()
        print(f"✓ Retried {att.student.name}")
    else:
        print(f"✗ Still failing: {att.student.name}")
```

## Deployment Checklist

- [ ] Add `LECTURER_PORTAL_API_URL` to production `.env`
- [ ] Add `LECTURER_PORTAL_API_KEY` to production `.env`
- [ ] Test portal API connectivity from server
- [ ] Verify API key is correct
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test attendance marking flow
- [ ] Monitor logs for sync errors
- [ ] Set up alerts for failed syncs (optional)
- [ ] Verify attendance data appears in portal

## Example: PHP Portal API Implementation

If you're building your portal, here's a sample PHP endpoint:

```php
<?php
// api/attendance/record
header('Content-Type: application/json');

// Verify API key
$api_key = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
$api_key = str_replace('Bearer ', '', $api_key);

if ($api_key !== $_ENV['ATTENDANCE_API_KEY']) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

$data = json_decode(file_get_contents('php://input'), true);

try {
    // Insert into database
    $db = new PDO($_ENV['DATABASE_URL']);
    $stmt = $db->prepare("
        INSERT INTO attendance (admission_no, student_name, unit_code, date, time_slot, venue, attendance_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ");
    
    $stmt->execute([
        $data['student']['admission_number'],
        $data['student']['name'],
        $data['attendance']['unit_code'],
        $data['attendance']['date'],
        $data['attendance']['time_slot'],
        $data['attendance']['venue'],
        $data['attendance']['attendance_percentage']
    ]);
    
    echo json_encode([
        'success' => true,
        'id' => $db->lastInsertId(),
        'message' => 'Attendance recorded successfully'
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
```

## Support

For issues with the sync system:
1. Check `.env` configuration
2. View portal_response in Attendance admin
3. Run test via shell (see Step 5)
4. Check Django logs for errors
5. Verify portal API is running

For portal-specific issues, contact your portal administrator.

---
**Last Updated**: 2024-12-03
**Version**: 1.0
