"""
View Optimization Guide for Digital Attendance System
Apply these optimizations to improve performance
"""

# OPTIMIZATION 1: Use select_related() and prefetch_related()
# BEFORE (Slow - causes N+1 queries):
sessions = AttendanceSession.objects.all()
for session in sessions:
    lecturer_name = session.lecturer.user.get_full_name()  # Extra query per session

# AFTER (Fast - single query):
from django.db.models import Prefetch
sessions = AttendanceSession.objects.select_related(
    'lecturer',
    'lecturer__user',
    'unit'
).all()

# OPTIMIZATION 2: Use only() to select specific fields
# BEFORE (Loads all fields):
students = Student.objects.all()

# AFTER (Loads only needed fields):
students = Student.objects.only('id', 'name', 'admission_number')

# OPTIMIZATION 3: Use values() for simple lists
# BEFORE (Creates full model objects):
admission_numbers = [s.admission_number for s in Student.objects.all()]

# AFTER (Returns just the values):
admission_numbers = Student.objects.values_list('admission_number', flat=True)

# OPTIMIZATION 4: Use .count() with count(*) not len()
# BEFORE (Loads all objects then counts):
count = len(Attendance.objects.all())

# AFTER (Uses database COUNT):
count = Attendance.objects.count()

# OPTIMIZATION 5: Batch database operations
# BEFORE (Multiple queries):
for student in students:
    Attendance.objects.create(student=student, session=session)

# AFTER (Single batch operation):
attendance_records = [
    Attendance(student=student, session=session)
    for student in students
]
Attendance.objects.bulk_create(attendance_records)

# OPTIMIZATION 6: Use cache for frequently accessed data
from django.core.cache import cache

# In views.py:
def lecturer_dashboard(request):
    lecturer = request.user.lecturer
    
    # Try to get from cache
    cache_key = f'sessions_{lecturer.id}'
    sessions = cache.get(cache_key)
    
    if sessions is None:
        # If not in cache, query database
        sessions = AttendanceSession.objects.filter(
            lecturer=lecturer
        ).select_related('unit').prefetch_related('attendance_records')
        # Store in cache for 5 minutes
        cache.set(cache_key, sessions, 300)
    
    return render(request, 'dashboard.html', {'sessions': sessions})

# OPTIMIZATION 7: Use Django Debug Toolbar in development
# Add to INSTALLED_APPS:
INSTALLED_APPS = [
    # ... other apps ...
    'debug_toolbar',
]

# Add to MIDDLEWARE:
MIDDLEWARE = [
    # ... other middleware ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# OPTIMIZATION 8: Async views for long operations
from asgiref.sync import sync_to_async
import asyncio

async def async_attendance_sync(attendance_record):
    """Asynchronously sync attendance to Firebase"""
    def sync_to_firebase():
        get_dual_sync_service().sync_attendance(
            attendance_record.student,
            attendance_record.session
        )
    
    await sync_to_async(sync_to_firebase)()

# OPTIMIZATION 9: Connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# OPTIMIZATION 10: Lazy loading for templates
# Use lazy evaluation in templates to defer computations
# {{ session.attendance_records.count }}  # Lazy counted by template tag

# SUMMARY OF QUICK WINS:
# 1. Add select_related() and prefetch_related() to querysets ⚡
# 2. Use cache.get/cache.set for repeated queries ⚡
# 3. Use .count() instead of len() ⚡
# 4. Use bulk_create() for batch operations ⚡
# 5. Add database connection pooling ⚡
# 6. Use only() to select specific fields ⚡
# 7. Add caching to settings.py ⚡
# 8. Enable WhiteNoise for static files ⚡
# 9. Use Django Debug Toolbar to find slow queries ⚡
# 10. Minimize database queries in templates ⚡
