import re
from pathlib import Path
p=Path(r"c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\attendance\views.py")
s=p.read_text()
# Replace synchronous sync block in student_attend
pattern=re.compile(r"\n\s*# Sync to both Firebase and Portal\n\s*sync_result = get_dual_sync_service\(\)\.sync_attendance\(student, session\)\n\n\s*if sync_result.get\('success'\):[\s\S]*?else:[\s\S]*?messages.error\(request, f\"Error recording attendance: \{sync_result.get\('error'\) or \'Failed to sync attendance. Please try again.\'\}\"\)\n", re.M)
if pattern.search(s):
    new='''\n            # Create or get local attendance record immediately (fast response)\n            from .models import Attendance as _Attendance\n            attendance, created = _Attendance.objects.get_or_create(student=student, session=session)\n            attendance_percentage = attendance.get_attendance_percentage()\n\n            # Background sync to Firebase and Portal (non-blocking)\n            import threading\n            def _bg_sync(att_id):\n                try:\n                    from .models import Attendance as __Attendance\n                    from .sync_service import get_dual_sync_service\n                    att = __Attendance.objects.get(id=att_id)\n                    get_dual_sync_service().sync_attendance(att.student, att.session)\n                except Exception:\n                    pass\n            threading.Thread(target=_bg_sync, args=(attendance.id,), daemon=True).start()\n\n            return render(request, 'attendance/success.html', {\n                'session': session,\n                'student_name': student_name,\n                'attendance_percentage': attendance_percentage,\n            })\n'''
    s=pattern.sub(new, s)
    p.write_text(s)
    print('views.py patched')
else:
    print('pattern not found; no change')
