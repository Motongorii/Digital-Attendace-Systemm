"""
Temporary debug views for troubleshooting authentication issues.
"""
from django.http import JsonResponse
from .models import Lecturer


def debug_auth_check(request):
    """Temporary debug endpoint to check authentication and lecturer profile status."""
    is_authenticated = request.user.is_authenticated
    username = request.user.username if is_authenticated else None
    session_key = request.session.session_key
    has_lecturer = False
    lecturer_staff_id = None
    
    if is_authenticated:
        try:
            lecturer = request.user.lecturer
            has_lecturer = True
            lecturer_staff_id = lecturer.staff_id
        except Lecturer.DoesNotExist:
            has_lecturer = False
    
    return JsonResponse({
        'authenticated': is_authenticated,
        'username': username,
        'session_key': session_key,
        'has_lecturer_profile': has_lecturer,
        'lecturer_staff_id': lecturer_staff_id,
        'message': 'Debug endpoint — if authenticated is True and has_lecturer_profile is True, you are logged in as a lecturer.',
    })
