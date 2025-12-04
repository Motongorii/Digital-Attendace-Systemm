# Session Numbering & Semester Features - Implementation Complete ✓

## Summary of Changes Applied

All changes have been successfully implemented and applied to your attendance system!

### 1. **Database Model Changes** ✓
**File: `attendance/models.py`**

- **Added `semester` field**: Choices (1 or 2), default=1
- **Added `session_number` field**: Range 1-13 per unit per semester
- **Updated Meta constraints**:
  - `unique_unit_semester_session`: Ensures max 1 session per number per semester
  - `unique_unit_semester_datetime`: Prevents duplicate date/time per unit/semester
- **Updated `__str__()` method**: Now shows "S1 Lec 1" format
- **Updated `ordering`**: By unit code, semester, session number

### 2. **Form Changes** ✓
**File: `attendance/forms.py`**

- **Updated `AttendanceSessionForm`**: Added `semester` field to form
- Lecturers can now select Semester 1 or 2 when creating sessions

### 3. **View Logic Changes** ✓
**File: `attendance/views.py`**

**`create_session` view**:
- Detects duplicate sessions (same unit/semester/date/time) and prevents creation
- Auto-assigns next available session_number (1..13)
- Rejects creation if 13 sessions already exist for that unit/semester
- Error messages guide lecturers when limits are reached

**`session_detail` view**:
- Now computes attendance percentage for each student out of 12 lessons
- Calculates based on: (attendance_count / 12) * 100
- Percentage is specific to the session's unit
- Includes percentage in every attendance record for display

### 4. **Template Changes** ✓
**File: `templates/attendance/session_detail.html`**

**Unit display**:
- Now shows: "CS101 - S1 Lec 3" format (Semester 1, Lecture 3)
- Clear visual indication of which semester and lecture number

**Attendance table**:
- New column: **Attendance %**
- Shows each student's overall attendance percentage for that unit
- Formatted as: e.g., "75.0%"

### 5. **Database Migrations** ✓
**Migration: `0003_alter_attendancesession_options_and_more`**

```
✓ All migrations applied successfully
✓ New columns: semester, session_number
✓ Constraints created and active
✓ Database schema updated
```

## How It Works Now

### Creating Sessions
1. Lecturer logs in and creates new session
2. Selects: Unit, **Semester (1 or 2)**, Date, Time, Venue
3. System auto-assigns Lec 1, Lec 2, ... up to Lec 13
4. Cannot create more than 13 lectures per unit per semester
5. Duplicate date/time sessions are rejected

### Session Display
```
Example: CS101 - S1 Lec 3
         └─ Semester 1, Lecture 3
```

### Attendance Records
When you view a session, the table shows:
```
# | Student Name  | Admission No. | Time Marked         | Attendance %
1 | John Doe      | ADM/2024/001  | 2025-12-04 10:15:30 | 83.3%
2 | Jane Smith    | ADM/2024/002  | 2025-12-04 10:16:45 | 66.7%
```

**Attendance % = (Lessons Attended / 12) × 100**
- Out of 12 lessons per semester
- Specific to each unit
- Shows student's current standing

## Key Features

✓ **Max 13 sessions per unit per semester** (configurable in models.py)
✓ **Unique session numbering**: Lec 1, Lec 2, ... Lec 13
✓ **Semester separation**: Lec numbers reset for each semester
✓ **No duplicate sessions**: Same date/time prevention
✓ **Auto-assignment**: Lecturers don't need to manually assign numbers
✓ **Attendance percentage**: Clear metrics out of 12 lessons
✓ **Database constraints**: Enforced at the model level

## Testing the System

### Step 1: Log In
- URL: `http://192.168.61.86:8000/login/`
- Username: `admin`
- Password: `Admin@123456`

### Step 2: Create a Unit (if needed)
- Go to Dashboard → Create Unit
- Add a new unit code and name

### Step 3: Create Sessions
- Go to Dashboard → Create Session
- Fill form:
  - **Unit**: Select a unit
  - **Semester**: Choose 1 or 2
  - **Date**: Pick a date
  - **Time**: Set start/end time
  - **Venue**: Enter room/location

Expected result:
- 1st session → "S1 Lec 1" (or S2 Lec 1 if semester 2)
- 2nd session → "S1 Lec 2"
- 13th session → "S1 Lec 13"
- 14th attempt → Error: "This unit already has 13 sessions..."

### Step 4: View Session Details
- Click "View" on any session
- Verify:
  - Title shows "CS101 - S1 Lec 3" format ✓
  - Attendance table has % column ✓
  - Percentages show as e.g., "75.0%" ✓

### Step 5: Mark Attendance (Mobile Test)
- From your phone (same Wi-Fi): `http://192.168.61.86:8000/`
- Scan QR code
- Mark attendance for a student
- Refresh session detail to see updated percentage

## Configuration & Customization

### Change Max Lessons (Currently 12)
File: `attendance/models.py`, method `get_attendance_percentage()`

```python
def get_attendance_percentage(self, unit=None, semester=1, max_lessons=12):  # ← Change here
```

### Change Max Sessions per Semester (Currently 13)
File: `attendance/models.py`, field `session_number`

```python
session_number = models.PositiveSmallIntegerField(
    blank=True, null=True, 
    validators=[MinValueValidator(1), MaxValueValidator(13)]  # ← Change 13 to desired max
)
```

And update the constraint message in `views.py` `create_session`.

## File Changes Summary

```
✓ attendance/models.py
  - Added semester field (choices: 1, 2)
  - Added session_number field (1-13)
  - Updated Meta.ordering and constraints
  - Updated __str__()

✓ attendance/forms.py
  - Added semester field to AttendanceSessionForm

✓ attendance/views.py
  - Updated create_session() with duplicate detection and auto-numbering
  - Updated session_detail() with attendance percentage calculation

✓ templates/attendance/session_detail.html
  - Updated unit display to show "S1 Lec 3" format
  - Added "Attendance %" column to table

✓ Database
  - Migration 0003 created and applied
  - New columns and constraints active
```

## Migration Details
```
Operations performed:
✓ attendance.0001_initial
✓ attendance.0002_student_attendance
✓ attendance.0003_alter_attendancesession_options_and_more
  - Change Meta options on attendancesession
  - Add field semester to attendancesession
  - Add field session_number to attendancesession
  - Create constraint unique_unit_semester_session
  - Create constraint unique_unit_semester_datetime
```

## Server Status
✓ Server running: `http://0.0.0.0:8000/`
✓ LAN access: `http://192.168.61.86:8000/`
✓ QR codes now use LAN IP
✓ Multi-device scanning enabled

## Next Steps
1. Test creating sessions with different semesters
2. Verify attendance percentages are calculated correctly
3. Test QR code from mobile device
4. Mark attendance and verify percentage updates
5. Try creating 14th session (should show error)

## Support Notes
- All old sessions default to Semester 1
- New sessions require explicit semester selection
- Session numbers are unique per (unit, semester) combination
- Percentages are recalculated on each view
- No data loss during migration (fresh database for testing)

---
**System Status**: ✓ Ready for Testing
**Admin Credentials**: admin / Admin@123456
**LAN IP**: 192.168.61.86:8000
