"""
URL patterns for attendance app.
"""
from django.urls import path
from . import views
from .debug_views import debug_auth_check

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('attend/<uuid:session_id>/', views.student_attend, name='student_attend'),
    
    # Auth
    path('login/', views.lecturer_login, name='login'),
    path('logout/', views.lecturer_logout, name='logout'),
    
    # Lecturer dashboard
    path('dashboard/', views.lecturer_dashboard, name='dashboard'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('session/<uuid:session_id>/toggle/', views.toggle_session, name='toggle_session'),
    path('session/<uuid:session_id>/download-qr/', views.download_qr, name='download_qr'),
    path('unit/create/', views.create_unit, name='create_unit'),
    
    # API
    path('api/status/', views.api_status, name='api_status'),
    
    # Debug (temporary)
    path('debug/auth-check/', debug_auth_check, name='debug_auth_check'),

    # (bootstrap admin endpoint removed for security)
]
