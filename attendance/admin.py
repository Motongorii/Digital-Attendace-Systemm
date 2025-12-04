"""
Admin configuration for attendance app.
"""
from django.contrib import admin
from .models import Lecturer, Unit, AttendanceSession, Student, Attendance


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ['user', 'staff_id', 'department', 'phone']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'staff_id']
    list_filter = ['department']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'lecturer']
    search_fields = ['code', 'name']
    list_filter = ['lecturer']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['unit', 'lecturer', 'date', 'start_time', 'venue', 'is_active']
    list_filter = ['is_active', 'date', 'lecturer']
    search_fields = ['unit__code', 'unit__name', 'venue']
    date_hierarchy = 'date'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'admission_number', 'email', 'phone', 'created_at']
    search_fields = ['name', 'admission_number', 'email']
    list_filter = ['created_at', 'units']
    filter_horizontal = ['units']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'timestamp', 'synced_to_firebase', 'synced_to_portal']
    list_filter = ['timestamp', 'synced_to_firebase', 'synced_to_portal', 'session__unit']
    search_fields = ['student__name', 'student__admission_number', 'session__unit__code']
    readonly_fields = ['timestamp', 'firebase_doc_id', 'portal_response']
    date_hierarchy = 'timestamp'


