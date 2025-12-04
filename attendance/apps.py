"""
App configuration for attendance app.
"""
from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    verbose_name = 'Digital Attendance System'

    def ready(self):
        # Import signals to ensure post_save handlers are connected
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass

