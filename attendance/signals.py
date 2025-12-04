from django.db.models.signals import post_save
from django.dispatch import receiver
import threading

from .models import Attendance


@receiver(post_save, sender=Attendance)
def attendance_post_save(sender, instance, created, **kwargs):
    """When a new Attendance is saved, sync it to Firebase/Portal asynchronously.

    This ensures the web request that created the attendance is fast (returns immediately),
    while the heavy network sync happens in the background.
    """
    if not created:
        return

    def _sync(att_id):
        try:
            # Import here to avoid import cycles at module load
            from .models import Attendance as _Attendance
            from .sync_service import get_dual_sync_service
            att = _Attendance.objects.get(id=att_id)
            get_dual_sync_service().sync_attendance(att.student, att.session)
        except Exception:
            # Best-effort background sync; failures logged inside sync service
            pass

    t = threading.Thread(target=_sync, args=(instance.id,), daemon=True)
    t.start()
