#!/usr/bin/env python
"""Patch views.py to include attendance percentage calculation"""

views_file = r'c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\attendance\views.py'

# Read the current file
with open(views_file, 'r') as f:
    content = f.read()

# Find and replace the session_detail function
old_session_detail = '''@login_required
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

    # Supplement with local DB records (avoid duplicates)
    local_qs = Attendance.objects.filter(session=session).select_related('student')
    if local_qs.exists():
        existing_adms = {r.get('admission_number') for r in attendance_records if isinstance(r, dict)}
        for att in local_qs:
            if att.student.admission_number in existing_adms:
                continue
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
                'attendance_percentage': float(att.get_attendance_percentage()),
            })
        attendance_count = len(attendance_records)

    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendance_records': attendance_records,
        'attendance_count': attendance_count,
    })'''

new_session_detail = '''@login_required
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
    })'''

if old_session_detail in content:
    content = content.replace(old_session_detail, new_session_detail)
    with open(views_file, 'w') as f:
        f.write(content)
    print("✓ views.py patched successfully")
else:
    print("⚠ Could not find exact session_detail function to patch")
    print("  Please manually update as per APPLY_CHANGES.md")
