# Apply Session Numbering and Semester Features

## Changes Applied ✓

1. **models.py** - DONE
   - Added `semester` field (choices: 1 or 2, default=1)
   - Added `session_number` field (1-13)
   - Updated Meta with two new unique constraints:
     - `unique_unit_semester_session` - ensures max 13 sessions per unit per semester
     - `unique_unit_semester_datetime` - prevents duplicate date/time sessions
   - Updated `__str__` to show "S{semester} Lec {session_number}"
   - Updated ordering to `['unit__code', 'semester', 'session_number', 'date', 'start_time']`

2. **forms.py** - DONE
   - Added `semester` field to `AttendanceSessionForm`

3. **views.py - create_session** - DONE
   - Added duplicate session detection for same unit/semester/date/time
   - Auto-assigns next available session_number (1..13) for unit/semester combo
   - Prevents creation if 13 sessions already exist for that unit/semester

## Changes Still Needed

### 1. Update `attendance/views.py` - session_detail function

Replace the entire `session_detail` function (around line 237) with:

```python
@login_required
def session_detail(request, session_id):
    """View session details and QR code."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Get attendance records from Firebase (fallback to local DB if empty)
    fb_service = get_firebase_service()
    attendance_records = []
    attendance_count = 0
    if fb_service.is_connected:
        try:
            attendance_records = fb_service.get_session_attendance(str(session.id)) or []
            attendance_count = len(attendance_records)
        except Exception:
            attendance_records = []
            attendance_count = 0

    # Supplement with local DB records (avoid duplicates) and compute attendance percentage
    local_qs = Attendance.objects.filter(session=session).select_related('student')
    existing_adms = {r.get('admission_number') for r in attendance_records if isinstance(r, dict)}
    
    for att in local_qs:
        if att.student.admission_number in existing_adms:
            continue
        # Compute attendance percentage out of 12 lessons for this unit
        pct = float(att.student.get_attendance_percentage(unit=session.unit, max_lessons=12))
        attendance_records.append({
            'session_id': str(session.id),
            'student_name': att.student.name,
            'admission_number': att.student.admission_number,
            'unit_code': session.unit.code,
            'unit_name': session.unit.name,
            'lecturer_name': session.lecturer.user.get_full_name(),
            'date': str(session.date),
            'time_slot': f"{session.start_time} - {session.end_time}",
            'venue': session.venue,
            'timestamp': att.timestamp.isoformat(),
            'attendance_percentage': pct,
        })
    
    attendance_count = len(attendance_records)

    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendance_records': attendance_records,
        'attendance_count': attendance_count,
    })
```

### 2. Update `templates/attendance/session_detail.html`

**A. Update the unit code display to show Semester and Lec number:**

Find this section (around line ~140):
```html
<div class="unit-code">{{ session.unit.code }}</div>
<div class="unit-name">{{ session.unit.name }}</div>
```

Replace with:
```html
<div class="unit-code">{{ session.unit.code }} {% if session.session_number %}- S{{ session.semester }} Lec {{ session.session_number }}{% endif %}</div>
<div class="unit-name">{{ session.unit.name }}</div>
```

**B. Add Attendance % column to the attendance table:**

Find the attendance table header (around line ~250):
```html
<thead>
    <tr>
        <th>#</th>
        <th>Student Name</th>
        <th>Admission No.</th>
        <th>Time Marked</th>
    </tr>
</thead>
```

Replace with:
```html
<thead>
    <tr>
        <th>#</th>
        <th>Student Name</th>
        <th>Admission No.</th>
        <th>Time Marked</th>
        <th>Attendance %</th>
    </tr>
</thead>
```

**C. Add attendance percentage cell in the table body:**

Find the tbody loop (around line ~257):
```html
<tbody>
    {% for record in attendance_records %}
    <tr>
        <td>{{ forloop.counter }}</td>
        <td>{{ record.student_name }}</td>
        <td>{{ record.admission_number }}</td>
        <td>{{ record.timestamp|slice:":19" }}</td>
    </tr>
    {% endfor %}
</tbody>
```

Replace with:
```html
<tbody>
    {% for record in attendance_records %}
    <tr>
        <td>{{ forloop.counter }}</td>
        <td>{{ record.student_name }}</td>
        <td>{{ record.admission_number }}</td>
        <td>{{ record.timestamp|slice:":19" }}</td>
        <td><strong>{{ record.attendance_percentage|floatformat:1 }}%</strong></td>
    </tr>
    {% endfor %}
</tbody>
```

### 3. Update `templates/attendance/create_session.html` (optional styling for semester field)

The form will automatically include the semester dropdown. You may want to add styling:

```html
<!-- After the form is rendered, add this CSS to make semester visible: -->
<style>
    .form-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--glass-border);
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.3);
        color: var(--text-primary);
        font-family: 'Share Tech Mono', monospace;
    }
</style>
```

## Run Migrations

After updating the files, run:

```powershell
cd c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main
python manage.py makemigrations attendance
python manage.py migrate
```

## Auto-Populate Session Numbers (Optional)

If you have existing sessions and want to auto-assign session numbers, run:

```powershell
python manage.py shell
```

Then paste:

```python
from attendance.models import AttendanceSession, Unit

for unit in Unit.objects.all():
    for semester in [1, 2]:
        sessions = AttendanceSession.objects.filter(
            unit=unit, 
            semester=semester
        ).order_by('date', 'start_time')
        num = 1
        for s in sessions:
            if not s.session_number:
                if num <= 13:
                    s.session_number = num
                    s.save()
                    num += 1
                else:
                    print(f"Unit {unit.code} S{semester} already has >13 sessions; manual cleanup required.")

print("✓ Session numbers assigned!")
exit()
```

## Test

1. Start server: `python manage.py runserver 0.0.0.0:8000`
2. Create a new unit and try creating sessions
3. Sessions should auto-assign Lec 1, Lec 2, etc. per semester
4. Max 13 sessions per unit per semester (error on 14th attempt)
5. View session details - attendance table should show % column with values out of 12 lessons
6. QR code should show "S1 Lec 3" format in the title

## Semester Behavior

- Default semester = 1
- When creating a new session, lecturer can select Semester 1 or 2
- Sessions are grouped by semester
- Lec numbering restarts for each semester (e.g., S1 Lec 1..13, then S2 Lec 1..13)
- Each (unit, semester, session_number) combination is unique
- Each (unit, semester, date, time) combination is unique (prevents duplicate timeslots)
