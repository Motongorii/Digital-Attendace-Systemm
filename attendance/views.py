"""
Views for Digital Attendance System.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import json
import threading
from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)

from .models import Lecturer, Unit, AttendanceSession, Student, Attendance
from .forms import AttendanceSessionForm, StudentAttendanceForm, UnitForm
from .firebase_service import get_firebase_service
from .sync_service import get_dual_sync_service
from .qr_generator import generate_session_qr


# bootstrap_admin endpoint removed — use management commands or `create_admin.py`.


def home(request):
    """Landing page."""
    return render(request, 'attendance/home.html')


def student_attend(request, session_id):
    """
    Student attendance page - accessed via QR code scan.
    Shows session info and form to input student details.
    """
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Check if session is still active
    if not session.is_active:
        return render(request, 'attendance/session_closed.html', {
            'session': session
        })
    
    if request.method == 'POST':
        form = StudentAttendanceForm(request.POST)
        if form.is_valid():
            admission_number = form.cleaned_data['admission_number']
            student_name = form.cleaned_data['student_name']
            
            # Check if already marked (Firebase first, then local DB fallback)
            already_marked = False
            fb_service = get_firebase_service()
            if fb_service.is_connected:
                try:
                    already_marked = fb_service.check_already_marked(str(session.id), admission_number)
                except Exception:
                    already_marked = False
            # Local DB fallback to prevent duplicates when Firebase is unavailable
            if not already_marked:
                already_marked = Attendance.objects.filter(session=session, student__admission_number=admission_number).exists()

            if already_marked:
                messages.warning(request, 'You have already marked attendance for this session!')
                return render(request, 'attendance/already_marked.html', {
                    'session': session
                })
            
            # Get or create student
            student, created = Student.objects.get_or_create(
                admission_number=admission_number,
                defaults={
                    'name': student_name,
                }
            )
            
            # Update student name if provided and different
            if student_name and student.name != student_name:
                student.name = student_name
                student.save()
            
            # Ensure student is enrolled in the unit
            if session.unit not in student.units.all():
                student.units.add(session.unit)
            
            # Create or get local attendance record immediately (fast response)
            from .models import Attendance as _Attendance
            attendance, created = _Attendance.objects.get_or_create(student=student, session=session)
            attendance_percentage = attendance.get_attendance_percentage()

            # Background sync to Firebase and Portal (non-blocking)
            import threading
            def _bg_sync(att_id):
                try:
                    from .models import Attendance as __Attendance
                    from .sync_service import get_dual_sync_service
                    att = __Attendance.objects.get(id=att_id)
                    get_dual_sync_service().sync_attendance(att.student, att.session)
                except Exception:
                    pass
            threading.Thread(target=_bg_sync, args=(attendance.id,), daemon=True).start()

            return render(request, 'attendance/success.html', {
                'session': session,
                'student_name': student_name,
                'attendance_percentage': attendance_percentage,
            })
    else:
        form = StudentAttendanceForm()
    
    return render(request, 'attendance/attend.html', {
        'session': session,
        'form': form,
    })


@login_required
def lecturer_dashboard(request):
    """Lecturer dashboard - manage sessions and view attendance."""
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'You are not registered as a lecturer.')
        return redirect('home')
    
    # Optimize queries with select_related to avoid N+1 problem
    sessions = AttendanceSession.objects.filter(lecturer=lecturer).select_related(
        'unit', 'lecturer'
    ).order_by('-created_at')
    units = Unit.objects.filter(lecturer=lecturer)
    
    return render(request, 'attendance/dashboard.html', {
        'lecturer': lecturer,
        'sessions': sessions,
        'units': units,
    })


@login_required
def create_session(request):
    """Create a new attendance session."""
    # Debug logging for diagnosing auth/session issues
    session_key = request.session.session_key
    is_authenticated = request.user.is_authenticated
    print(f'[CREATE_SESSION] session_key={session_key}, auth={is_authenticated}, method={request.method}')
    logger.info(f'[CREATE_SESSION] session_key={session_key}, auth={is_authenticated}, method={request.method}')
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'You are not registered as a lecturer.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)
        form.fields['unit'].queryset = Unit.objects.filter(lecturer=lecturer)
        
        if form.is_valid():
            try:
                session = form.save(commit=False)
                session.lecturer = lecturer
                
                # Check if a duplicate session already exists (same unit, semester, date, time)
                existing_same_time = AttendanceSession.objects.filter(
                    unit=session.unit,
                    semester=session.semester,
                    date=session.date,
                    start_time=session.start_time
                ).exists()
                if existing_same_time:
                    messages.error(request, 'A session for this unit and semester at the same date/time already exists.')
                    form.add_error(None, 'Duplicate session time detected.')
                    return render(request, 'attendance/create_session.html', {'form': form})
                
                # Assign the next available session_number (1..13) for this unit and semester
                used_numbers = set(
                    AttendanceSession.objects.filter(
                        unit=session.unit,
                        semester=session.semester
                    ).exclude(session_number__isnull=True).values_list('session_number', flat=True)
                )
                next_num = None
                for n in range(1, 14):
                    if n not in used_numbers:
                        next_num = n
                        break
                
                if not next_num:
                    messages.error(request, f'This unit already has 13 sessions for Semester {session.semester}. Cannot add more.')
                    form.add_error(None, 'Maximum sessions (13) reached for this semester.')
                    return render(request, 'attendance/create_session.html', {'form': form})
                
                session.session_number = next_num
                session.save()
                
                # Generate QR code
                # Build a base URL that is reachable from other devices on the same network.
                # Detect the actual LAN IP from the request if available
                base_url = request.build_absolute_uri('/')[:-1]
                try:
                    host = request.get_host().split(':')[0]
                except Exception:
                    host = ''

                # If running on localhost or 0.0.0.0, detect the actual LAN IP
                if host in ('127.0.0.1', 'localhost', '0.0.0.0') or host == '' or settings.DEBUG:
                    try:
                        import socket
                        import subprocess
                        
                        # First, try to get the LAN IP by parsing ipconfig output (Windows)
                        local_ip = None
                        try:
                            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
                            # Look for Wi-Fi adapter's IPv4 Address
                            for line in result.stdout.split('\n'):
                                if 'IPv4 Address' in line and '192.168' in line:
                                    parts = line.split(':')
                                    if len(parts) > 1:
                                        local_ip = parts[1].strip()
                                        break
                        except Exception:
                            pass
                        
                        # Fallback: use socket method
                        if not local_ip:
                            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            try:
                                # Connect to a remote host (doesn't need to be reachable)
                                s.connect(('1.1.1.1', 80))
                                local_ip = s.getsockname()[0]
                            finally:
                                s.close()
                        
                        if local_ip and local_ip != '127.0.0.1':
                            port = request.get_port()
                            base_url = f"http://{local_ip}:{port}"
                    except Exception:
                        # If all detection fails, use the original URL
                        base_url = request.build_absolute_uri('/')[:-1]

                # Generate and save QR code
                qr_file = generate_session_qr(session, base_url)
                session.qr_code.save(qr_file.name, qr_file)
                
                # Add success message and redirect to session detail
                messages.success(request, 'Session created successfully! QR code generated.')
                return redirect('session_detail', session_id=session.id)
            
            except Exception as e:
                messages.error(request, f'Error creating session: {str(e)}')
                import traceback
                traceback.print_exc()
                return render(request, 'attendance/create_session.html', {'form': form})
        else:
            # Form is not valid
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttendanceSessionForm()
        form.fields['unit'].queryset = Unit.objects.filter(lecturer=lecturer)
    
    return render(request, 'attendance/create_session.html', {
        'form': form,
    })


@login_required
def session_detail(request, session_id):
    """View session details and QR code."""
    # Optimize with select_related to avoid N+1 queries
    session = get_object_or_404(
        AttendanceSession.objects.select_related('unit', 'lecturer', 'lecturer__user'),
        id=session_id
    )
    
    # Get attendance records from Firebase (fallback to local DB if empty)
    fb_service = get_firebase_service()
    attendance_records = []
    attendance_count = 0
    
    # Check cache first
    cache_key = f"session_attendance_{session.id}"
    cached_records = cache.get(cache_key)
    
    if cached_records is None and fb_service.is_connected:
        # Fetch from Firebase with timeout
        def fetch_firebase():
            try:
                records = fb_service.get_session_attendance(str(session.id)) or []
                cache.set(cache_key, records, 5)  # Cache for 5 seconds
                return records
            except Exception:
                return []
        
        thread = threading.Thread(target=fetch_firebase, daemon=True)
        thread.start()
        thread.join(timeout=2)  # Wait max 2 seconds for Firebase
        
        attendance_records = cached_records or []
    else:
        attendance_records = cached_records or []
    
    attendance_count = len(attendance_records)

    # Load from local DB (fastest)

    local_qs = Attendance.objects.filter(session=session).select_related('student').only(
        'id', 'student__name', 'student__admission_number', 'timestamp'
    ).order_by('-timestamp')[:100]  # Limit to last 100 for performance
    
    attendance_records = []
    for att in local_qs:
        attendance_pct = att.student.get_attendance_percentage(unit=session.unit)
        attendance_records.append({
            'session_id': str(session.id),
            'student_name': att.student.name,
            'admission_number': att.student.admission_number,
            'unit_code': session.unit.code,
            'unit_name': session.unit.name,
            'lecturer_name': session.lecturer.user.get_full_name(),
            'date': str(session.date),
            'time_slot': f"{session.start_time} - {session.end_time}",
            'venue': session.venue,
            'timestamp': att.timestamp.isoformat(),
            'attendance_percentage': float(attendance_pct) if attendance_pct else 0,
        })
    attendance_count = len(attendance_records)
    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendance_records': attendance_records,
        'attendance_count': attendance_count,
    })


@login_required
def toggle_session(request, session_id):
    """Toggle session active status."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    if session.lecturer.user != request.user:
        messages.error(request, 'You do not have permission to modify this session.')
        return redirect('dashboard')
    
    session.is_active = not session.is_active
    session.save()
    
    status = 'activated' if session.is_active else 'deactivated'
    messages.success(request, f'Session {status} successfully!')
    return redirect('session_detail', session_id=session.id)


@login_required
def create_unit(request):
    """Create a new unit."""
    # Debug logging for diagnosing auth/session issues
    session_key = request.session.session_key
    is_authenticated = request.user.is_authenticated
    print(f'[CREATE_UNIT] session_key={session_key}, auth={is_authenticated}, method={request.method}')
    logger.info(f'[CREATE_UNIT] session_key={session_key}, auth={is_authenticated}, method={request.method}')
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'You are not registered as a lecturer.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.lecturer = lecturer
            unit.save()
            messages.success(request, 'Unit created successfully!')
            return redirect('dashboard')
    else:
        form = UnitForm()
    
    return render(request, 'attendance/create_unit.html', {
        'form': form,
    })


def lecturer_login(request):
    """Lecturer login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(f'[LOGIN DEBUG] username={username}, auth_result={bool(user)}')
        logger.info(f'[LOGIN DEBUG] username={username}, auth_result={bool(user)}')
        
        if user is not None:
            login(request, user)
            session_key = request.session.session_key
            print(f'[LOGIN SUCCESS] username={username}, session_key={session_key}')
            logger.info(f'[LOGIN SUCCESS] username={username}, session_key={session_key}')
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            print(f'[LOGIN FAILED] username={username}, invalid credentials')
            logger.warning(f'[LOGIN FAILED] username={username}, invalid credentials')
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'attendance/login.html')


def lecturer_logout(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def download_qr(request, session_id):
    """Download QR code image."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    if session.qr_code:
        img_bytes = session.qr_code.read()
        response = HttpResponse(img_bytes, content_type='image/png')
        # By default serve the image inline so it can be embedded in <img> tags even
        # when MEDIA files are not served by the platform. Add `?download=1` to force
        # an attachment download when needed.
        if request.GET.get('download'):
            response['Content-Disposition'] = f'attachment; filename="qr_{session.unit.code}_{session.date}.png"'
        else:
            response['Content-Disposition'] = 'inline'
        return response
    
    messages.error(request, 'QR code not found.')
    return redirect('session_detail', session_id=session.id)


# API endpoint for checking Firebase status
def api_status(request):
    """Check system status."""

    session_id = request.GET.get('session_id')
    attendance_count = None
    if session_id:
        try:
            session = AttendanceSession.objects.get(id=session_id)
            fb_service = get_firebase_service()
            count = 0
            if fb_service.is_connected:
                try:
                    records = fb_service.get_session_attendance(str(session.id)) or []
                    count = len(records)
                except Exception:
                    count = 0
            # Supplement with local DB records
            local_count = Attendance.objects.filter(session=session).count()
            attendance_count = max(count, local_count)
        except AttendanceSession.DoesNotExist:
            attendance_count = None
    return JsonResponse({
        'firebase_connected': get_firebase_service().is_connected,
        'timestamp': timezone.now().isoformat(),
        'attendance_count': attendance_count,
    })








@login_required
@require_http_methods(["POST"])
def create_unit_ajax(request):
    """AJAX endpoint to create a Unit and return JSON. Used by dashboard modal."""
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not_a_lecturer'}, status=403)

    form = UnitForm(request.POST)
    if form.is_valid():
        unit = form.save(commit=False)
        unit.lecturer = lecturer
        unit.save()
        return JsonResponse({'success': True, 'unit': {'id': unit.id, 'code': unit.code, 'name': unit.name}}, status=201)
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
