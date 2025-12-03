"""
Admin configuration for attendance app.
"""
from django.contrib import admin
from .models import Lecturer, Unit, AttendanceSession


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


