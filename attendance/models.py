"""
Models for Digital Attendance System.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from decimal import Decimal


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
    SEMESTER_CHOICES = [(1, 'Semester 1'), (2, 'Semester 2')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='sessions')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    lecturer_name = models.CharField(max_length=100, help_text="Lecturer's name as entered for this session", blank=True)
    CLASS_YEAR_CHOICES = [
        ("Year 1", "Year 1"),
        ("Year 2", "Year 2"),
        ("Year 3", "Year 3"),
        ("Year 4", "Year 4"),
        ("Year 5", "Year 5"),
    ]
    class_year = models.CharField(max_length=20, choices=CLASS_YEAR_CHOICES, default="Year 1")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.FileField(upload_to='qr_codes/', blank=True, null=True)
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, default=1)
    session_number = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(13)])
    
    class Meta:
        ordering = ['unit__code', 'semester', 'session_number', 'date', 'start_time']
        constraints = [
            models.UniqueConstraint(fields=['unit', 'semester', 'session_number'], name='unique_unit_semester_session'),
            models.UniqueConstraint(fields=['unit', 'semester', 'date', 'start_time'], name='unique_unit_semester_datetime')
        ]
    
    def __str__(self):
        if self.session_number:
            return f"{self.unit.code} - S{self.semester} Lec {self.session_number} - {self.date} ({self.start_time})"
        return f"{self.unit.code} - S{self.semester} - {self.date} ({self.start_time})"
    
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


class Student(models.Model):
    """Student model - tracks student enrollment and attendance."""
    admission_number = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    units = models.ManyToManyField(Unit, related_name='enrolled_students')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.admission_number})"
    
    def get_attendance_percentage(self, unit=None, semester=1, max_lessons=12):
        """
        Calculate attendance percentage for a unit or all units.
        Default: 12 lessons per semester.
        """
        if unit:
            attendance = Attendance.objects.filter(
                student=self, 
                session__unit=unit
            ).count()
            return Decimal(attendance) / Decimal(max_lessons) * 100 if max_lessons > 0 else 0
        else:
            # Overall attendance across all units
            attendance = Attendance.objects.filter(student=self).count()
            total_sessions = AttendanceSession.objects.count()
            return Decimal(attendance) / Decimal(total_sessions) * 100 if total_sessions > 0 else 0


class Attendance(models.Model):
    """Attendance record - links student to attendance session."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    synced_to_firebase = models.BooleanField(default=False)
    synced_to_portal = models.BooleanField(default=False)
    firebase_doc_id = models.CharField(max_length=200, blank=True, null=True)
    portal_response = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ('student', 'session')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.student.name} - {self.session.unit.code} ({self.session.date})"
    
    def get_attendance_percentage(self, max_lessons=12):
        """Get attendance percentage for the student in this session's unit."""
        return self.student.get_attendance_percentage(unit=self.session.unit, max_lessons=max_lessons)


