from pathlib import Path

# Patch apps.py to add ready() import for signals
apps_path = Path(r"c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\attendance\apps.py")
apps_text = apps_path.read_text()
old = "    verbose_name = 'Digital Attendance System'\n"
if old in apps_text:
    new = old + "\n    def ready(self):\n        # Import signals to ensure post_save handlers are connected\n        try:\n            from . import signals  # noqa: F401\n        except Exception:\n            pass\n"
    apps_text = apps_text.replace(old, new)
    apps_path.write_text(apps_text)
    print('apps.py updated')
else:
    print('apps.py pattern not found; no change')

# Run patcher for views
views_path = Path(r"c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\attendance\views.py")
views_text = views_path.read_text()
import re
pattern=re.compile(r"\n\s*# Sync to both Firebase and Portal\n\s*sync_result = get_dual_sync_service\(\)\.sync_attendance\(student, session\)\n\n\s*if sync_result.get\('success'\):[\s\S]*?else:[\s\S]*?messages.error\(request, f\"Error recording attendance: \{sync_result.get\('error'\) or \'Failed to sync attendance. Please try again.\'\}\"\)\n", re.M)
if pattern.search(views_text):
    new='''\n            # Create or get local attendance record immediately (fast response)\n            from .models import Attendance as _Attendance\n            attendance, created = _Attendance.objects.get_or_create(student=student, session=session)\n            attendance_percentage = attendance.get_attendance_percentage()\n\n            # Background sync to Firebase and Portal (non-blocking)\n            import threading\n            def _bg_sync(att_id):\n                try:\n                    from .models import Attendance as __Attendance\n                    from .sync_service import get_dual_sync_service\n                    att = __Attendance.objects.get(id=att_id)\n                    get_dual_sync_service().sync_attendance(att.student, att.session)\n                except Exception:\n                    pass\n            threading.Thread(target=_bg_sync, args=(attendance.id,), daemon=True).start()\n\n            return render(request, 'attendance/success.html', {\n                'session': session,\n                'student_name': student_name,\n                'attendance_percentage': attendance_percentage,\n            })\n'''
    views_text=pattern.sub(new, views_text)
    views_path.write_text(views_text)
    print('views.py patched')
else:
    print('views.py pattern not found; no change')
