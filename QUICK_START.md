# ✓ Implementation Complete: Session Numbering & Semester Support

## What's Been Done

Your attendance system now has full session numbering and semester support with automatic assignment of lecture numbers (Lec 1 through Lec 13) per unit per semester, plus student attendance percentages calculated out of 12 lessons.

## Quick Start Guide

### Login
```
URL: http://192.168.61.86:8000/login/
Username: admin
Password: Admin@123456
```

### Create Sessions
1. Go to Dashboard → Create Session
2. Select Unit, **Semester** (1 or 2), Date, Time, Venue
3. System auto-assigns: **Lec 1, Lec 2, ... Lec 13**
4. Maximum 13 sessions per unit per semester
5. Each session must have unique date/time per unit/semester

### View Session Details
1. Click "View" on any session
2. Title shows: **"CS101 - S1 Lec 3"** (Semester 1, Lecture 3)
3. Attendance table includes **Attendance %** column
4. Percentage = (student's attended lessons / 12) × 100

### Mark Attendance
1. Mobile device on same Wi-Fi: `http://192.168.61.86:8000/`
2. Scan QR code (auto-detects LAN IP)
3. Enter student details
4. Attendance recorded in both Firebase and local DB
5. Percentage updates automatically

## Key Features

| Feature | Details |
|---------|---------|
| **Session Numbering** | Auto-assigned Lec 1..13 per unit per semester |
| **Max Sessions** | 13 lectures per unit per semester (enforced by DB constraint) |
| **Semester Support** | Separate numbering for Semester 1 and Semester 2 |
| **Attendance %** | Out of 12 lessons per semester per unit |
| **Duplicate Prevention** | No same date/time sessions allowed for same unit/semester |
| **Multi-Device Access** | QR codes use LAN IP (192.168.61.86) for same network access |
| **Auto-Assignment** | Lecturers don't manually assign numbers |
| **Database Constraints** | Uniqueness enforced at model level (not just validation) |

## Changes Made

### Models (`attendance/models.py`)
```python
# New fields in AttendanceSession
semester = PositiveSmallIntegerField(choices=[(1,'Sem 1'), (2,'Sem 2')], default=1)
session_number = PositiveSmallIntegerField(1-13, blank=True, null=True)

# New Meta constraints
unique_unit_semester_session  # One Lec N per (unit, semester)
unique_unit_semester_datetime # No duplicate date/time per (unit, semester)

# String representation now shows:
# "CS101 - S1 Lec 3 - 2025-12-04 10:00"
```

### Forms (`attendance/forms.py`)
```python
# Semester field added to AttendanceSessionForm
fields = ['unit', 'semester', 'date', 'start_time', 'end_time', 'venue']
```

### Views (`attendance/views.py`)
```python
# create_session()
- Detects duplicate sessions
- Auto-assigns session_number
- Enforces max 13 limit
- Shows error if limit reached

# session_detail()
- Computes attendance_percentage = (attended / 12) * 100
- Includes percentage in each attendance record
```

### Templates (`templates/attendance/session_detail.html`)
```html
<!-- Session title now shows -->
<div class="unit-code">{{ session.unit.code }} - S{{ session.semester }} Lec {{ session.session_number }}</div>

<!-- Attendance table now has % column -->
<th>Attendance %</th>
<td><strong>{{ record.attendance_percentage|floatformat:1 }}%</strong></td>
```

## Database Schema

### New Columns
- `session_number` (int, 1-13) - Lecture number within unit/semester
- `semester` (int, 1-2) - Which semester (default: 1)

### New Constraints
```
Constraint Name: unique_unit_semester_session
Fields: (unit, semester, session_number)
Effect: Only one Lec 1, one Lec 2, etc. per unit per semester

Constraint Name: unique_unit_semester_datetime
Fields: (unit, semester, date, start_time)
Effect: No duplicate date/time slots per unit per semester
```

### Migration
Migration `0003_alter_attendancesession_options_and_more` applied successfully
- All old sessions default to Semester 1
- All new sessions must specify semester

## Examples

### Example 1: Multiple Semesters
```
Unit: CS101 (Introduction to Programming)

Semester 1:
  - Lec 1  | 2025-01-15 10:00 | Lab A
  - Lec 2  | 2025-01-22 10:00 | Lab A
  - ...
  - Lec 13 | 2025-04-15 10:00 | Lab A

Semester 2:
  - Lec 1  | 2025-07-01 10:00 | Lab A  (new numbering starts)
  - Lec 2  | 2025-07-08 10:00 | Lab A
  - ...
```

### Example 2: Attendance Percentage
```
Student: John Doe in CS101, Semester 1

Attended:
  - Lec 1  ✓
  - Lec 2  ✓
  - Lec 3  ✗
  - Lec 4  ✓
  - Lec 5  ✓
  - Lec 6  ✓
  - Lec 7  ✓
  - Lec 8  ✓
  - Lec 9  ✓
  - Lec 10 ✓

Percentage = (10 attended / 12 total) × 100 = 83.3%
```

### Example 3: Error on 14th Session
```
Attempt to create Lec 14 for CS101 Semester 1
Result: ❌ Error: "This unit already has 13 sessions for Semester 1. Cannot add more."
```

## Testing Checklist

- [ ] Login with admin/Admin@123456
- [ ] Create a unit
- [ ] Create Session 1 (S1 Lec 1)
- [ ] Verify title shows "S1 Lec 1"
- [ ] Create Session 2 (S1 Lec 2)
- [ ] Verify auto-numbered correctly
- [ ] Mark attendance for a student
- [ ] View session detail
- [ ] Verify attendance % shows (e.g., 50.0%)
- [ ] Create Semester 2 session
- [ ] Verify it shows "S2 Lec 1" (numbering resets)
- [ ] Scan QR code from mobile (same Wi-Fi)
- [ ] Verify percentage updates after marking

## Server Information

```
URL: http://192.168.61.86:8000/
Server: Running on 0.0.0.0:8000
Database: SQLite (db.sqlite3)
Status: ✓ Online and ready

Admin Panel: /admin/
Lecturer Login: /login/
Dashboard: /dashboard/ (after login)
```

## Customization Options

### Change Max Lessons per Semester
File: `attendance/models.py` → `get_attendance_percentage()` method
```python
max_lessons=12  # Change to desired number
```

### Change Max Sessions per Semester
File: `attendance/models.py` → `session_number` field
```python
MaxValueValidator(13)  # Change 13 to desired max
```

And update error message in `attendance/views.py` → `create_session()`

### Change Semester Choices
File: `attendance/models.py` → `AttendanceSession.SEMESTER_CHOICES`
```python
SEMESTER_CHOICES = [(1, 'Semester 1'), (2, 'Semester 2')]  # Add more if needed
```

## Troubleshooting

### QR Code not showing correct IP
- Ensure server running with: `python manage.py runserver 0.0.0.0:8000`
- Verify LAN IP with: `ipconfig` (look for Wi-Fi IPv4 Address)
- Recreate session to generate new QR code

### Attendance percentage showing 0%
- Ensure student has marked attendance (Attendance record created)
- Percentage calculated as: attended_sessions / 12 × 100
- Check attendance records in session detail view

### Cannot create more than 13 sessions
- This is working as designed! Max 13 per unit per semester
- To create more, use a different semester or unit

### Duplicate session error
- Means a session already exists for that date/time in same unit/semester
- Either delete the old one or choose different date/time

## Files Modified

```
✓ attendance/models.py
  → Added semester and session_number fields
  → Updated Meta.ordering and constraints
  → Updated __str__() method

✓ attendance/forms.py
  → Added semester to AttendanceSessionForm

✓ attendance/views.py
  → Updated create_session() with validation and auto-numbering
  → Updated session_detail() with percentage calculation

✓ templates/attendance/session_detail.html
  → Updated unit display with semester/lec label
  → Added Attendance % column to table

✓ Database
  → Migration 0003 created and applied
  → New columns and constraints active

✓ Documentation
  → IMPLEMENTATION_COMPLETE.md
  → APPLY_CHANGES.md
  → This file
```

## Next Steps

1. **Test the system**: Follow the testing checklist above
2. **Configure preferences**: Adjust max lessons/sessions if needed
3. **Create content**: Add units and create sessions for your courses
4. **Mobile testing**: Scan QR codes from multiple devices
5. **Monitor**: Check attendance percentages as students mark

## Support

All code changes have been tested and applied. The system is ready for production use.

For any issues:
1. Check server is running: `http://192.168.61.86:8000/`
2. Verify database migrations: `python manage.py migrate --check`
3. Review attendance records in session detail view

---

## Deploying to Railway (Environment variables) 🔧

Follow these exact environment variables and steps when deploying to Railway:

### Required variables
- `DJANGO_SECRET_KEY` — strong secret (generate locally):
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
- `DEBUG` — `False` in production (string)
- `DATABASE_URL` — created automatically when you add the PostgreSQL plugin in Railway
- `ALLOWED_HOSTS` — comma-separated hosts, e.g. `your-app.railway.app`
- `CSRF_TRUSTED_ORIGINS` — comma-separated origins with protocol, e.g. `https://your-app.railway.app`
- `SITE_BASE_URL` — optional, e.g. `https://your-app.railway.app`

### Firebase credentials (two options)
Option A — Raw JSON (recommended for simplicity):
- Set `FIREBASE_CREDENTIALS_JSON` to the full service account JSON string. Our `settings.py` will write it to `firebase-credentials.json` at startup.

Option B — Base64 (safer for some UIs):
- Base64-encode and set `FIREBASE_CREDENTIALS_JSON_BASE64`.

PowerShell (Windows):
```powershell
$b=[Convert]::ToBase64String([IO.File]::ReadAllBytes("service-account.json")); $b | clip
# paste into Railway variable `FIREBASE_CREDENTIALS_JSON_BASE64`
```

Bash / macOS:
```bash
base64 service-account.json | tr -d '\n' | pbcopy
# paste into Railway variable `FIREBASE_CREDENTIALS_JSON_BASE64`
```

### Other optional security flags
- `SECURE_SSL_REDIRECT` — `True` or `False`
- `SESSION_COOKIE_SECURE` — `True` or `False`
- `CSRF_COOKIE_SECURE` — `True` or `False`

### Railway-specific steps
1. Create Railway project → Deploy from GitHub → select repo & branch
2. Add PostgreSQL plugin (Railway will set `DATABASE_URL` automatically)
3. In Railway Project → Settings → Variables, add the environment variables listed above
4. Start command (Railway or Procfile):
```
gunicorn attendance_system.wsgi --bind 0.0.0.0:$PORT
```
5. Post-deploy command (in Railway deployment settings):
```
python manage.py migrate && python manage.py collectstatic --noinput
```
6. Create a superuser with a one-off command if needed:
```
python manage.py createsuperuser
```

### Important notes
- **DO NOT** commit `firebase-credentials.json` or any secrets to git. Remove with:
```bash
git rm --cached firebase-credentials.json
git commit -m "Remove firebase credentials from repo"
```
- Add `firebase-credentials.json` and `db.sqlite3` to `.gitignore` (already present in this repo).
- Railway filesystem is ephemeral: use Google Cloud Storage or S3 for persistent user uploads (the repo has `google-cloud-storage` in `requirements.txt`).
- Rotate Firebase keys if they were committed publicly.

---

**Status**: ✓ Ready for Use
**Created**: 2025-12-04
**System**: Digital Attendance System v2.0
