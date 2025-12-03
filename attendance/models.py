"""
Models for Digital Attendance System.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class Lecturer(models.Model):
    """Lecturer model linked to Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"


class Unit(models.Model):
    """Course unit model."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='units')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AttendanceSession(models.Model):
    """A single attendance session for a unit."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='sessions')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.FileField(upload_to='qr_codes/', blank=True, null=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.unit.code} - {self.date} ({self.start_time})"
    
    def get_session_info(self):
        """Return session info for QR code."""
        return {
            'session_id': str(self.id),
            'unit_code': self.unit.code,
            'unit_name': self.unit.name,
            'lecturer_name': self.lecturer.user.get_full_name(),
            'date': str(self.date),
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'venue': self.venue,
        }


