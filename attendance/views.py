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

from .models import Lecturer, Unit, AttendanceSession
from .forms import AttendanceSessionForm, StudentAttendanceForm, UnitForm
from .firebase_service import firebase_service
from .qr_generator import generate_session_qr


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
            
            # Check if already marked
            if firebase_service.is_connected:
                if firebase_service.check_already_marked(str(session.id), admission_number):
                    messages.warning(request, 'You have already marked attendance for this session!')
                    return render(request, 'attendance/already_marked.html', {
                        'session': session
                    })
            
            # Prepare attendance data
            student_data = {
                'student_name': form.cleaned_data['student_name'],
                'admission_number': admission_number,
                'unit_code': session.unit.code,
                'unit_name': session.unit.name,
                'lecturer_name': session.lecturer.user.get_full_name(),
                'date': str(session.date),
                'time_slot': f"{session.start_time} - {session.end_time}",
                'venue': session.venue,
            }
            
            # Save to Firebase
            result = firebase_service.save_attendance(str(session.id), student_data)
            
            if result.get('success'):
                return render(request, 'attendance/success.html', {
                    'session': session,
                    'student_name': form.cleaned_data['student_name'],
                })
            else:
                messages.error(request, f"Error recording attendance: {result.get('error', 'Unknown error')}")
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
    
    sessions = AttendanceSession.objects.filter(lecturer=lecturer)
    units = Unit.objects.filter(lecturer=lecturer)
    
    return render(request, 'attendance/dashboard.html', {
        'lecturer': lecturer,
        'sessions': sessions,
        'units': units,
    })


@login_required
def create_session(request):
    """Create a new attendance session."""
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'You are not registered as a lecturer.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)
        form.fields['unit'].queryset = Unit.objects.filter(lecturer=lecturer)
        
        if form.is_valid():
            session = form.save(commit=False)
            session.lecturer = lecturer
            session.save()
            
            # Generate QR code
            base_url = request.build_absolute_uri('/')[:-1]
            qr_file = generate_session_qr(session, base_url)
            session.qr_code.save(qr_file.name, qr_file)
            
            messages.success(request, 'Session created successfully!')
            return redirect('session_detail', session_id=session.id)
    else:
        form = AttendanceSessionForm()
        form.fields['unit'].queryset = Unit.objects.filter(lecturer=lecturer)
    
    return render(request, 'attendance/create_session.html', {
        'form': form,
    })


@login_required
def session_detail(request, session_id):
    """View session details and QR code."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Get attendance records from Firebase
    attendance_records = firebase_service.get_session_attendance(str(session.id))
    
    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendance_records': attendance_records,
        'attendance_count': len(attendance_records),
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
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
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
        response = HttpResponse(session.qr_code.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="qr_{session.unit.code}_{session.date}.png"'
        return response
    
    messages.error(request, 'QR code not found.')
    return redirect('session_detail', session_id=session.id)


# API endpoint for checking Firebase status
def api_status(request):
    """Check system status."""
    return JsonResponse({
        'firebase_connected': firebase_service.is_connected,
        'timestamp': timezone.now().isoformat(),
    })




