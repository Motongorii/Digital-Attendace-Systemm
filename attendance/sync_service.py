"""
Sync service for dual-synchronization to Firebase and Lecturer Portal API.
Handles pushing attendance and student data to both systems.
"""
import os
import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class PortalSyncService:
    """Handles synchronization with Lecturer Portal API."""
    
    def __init__(self):
        self.portal_url = os.getenv('LECTURER_PORTAL_API_URL', '')
        self.portal_api_key = os.getenv('LECTURER_PORTAL_API_KEY', '')
        self.timeout = int(os.getenv('PORTAL_SYNC_TIMEOUT', '10'))
        self.enabled = bool(self.portal_url)
    
    def sync_attendance(self, attendance_record: 'Attendance', student: 'Student', session: 'AttendanceSession') -> Dict[str, Any]:
        """
        Sync a single attendance record to the lecturer portal.
        
        Args:
            attendance_record: Attendance model instance
            student: Student model instance
            session: AttendanceSession model instance
        
        Returns:
            {
                'success': bool,
                'message': str,
                'document_id': str (if success),
                'error': str (if failure)
            }
        """
        if not self.enabled:
            # Portal not configured — indicate skipped so caller doesn't mark as synced
            return {
                'success': False,
                'skipped': True,
                'message': 'Portal sync disabled (no API URL configured)',
                'document_id': None,
            }
        
        try:
            attendance_percentage = Decimal(attendance_record.get_attendance_percentage()) if attendance_record else Decimal(0)
            
            payload = {
                'action': 'record_attendance',
                'student': {
                    'admission_number': student.admission_number,
                    'name': student.name,
                    'email': student.email,
                    'phone': student.phone,
                },
                'attendance': {
                    'unit_code': session.unit.code,
                    'unit_name': session.unit.name,
                    'date': str(session.date),
                    'time_slot': f"{session.start_time} - {session.end_time}",
                    'venue': session.venue,
                    'lecturer_name': session.lecturer.user.get_full_name(),
                    'timestamp': datetime.now().isoformat(),
                    'attendance_percentage': float(attendance_percentage),
                },
                'api_key': self.portal_api_key,
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.portal_api_key}',
            }
            
            response = requests.post(
                f"{self.portal_url}/api/attendance/record",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                return {
                    'success': True,
                    'message': 'Attendance synced to portal successfully',
                    'document_id': result.get('id', str(attendance_record.id)),
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Portal returned error'),
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'Portal sync timeout (>{self.timeout}s)',
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'success': False,
                'error': f'Failed to connect to portal: {str(e)}',
            }
        except Exception as e:
            logger.error(f"Portal sync error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def sync_student_bulk(self, students: list) -> Dict[str, Any]:
        """
        Sync multiple students to the portal.
        Useful for bulk imports/updates.
        """
        if not self.enabled:
            return {
                'success': False,
                'skipped': True,
                'message': 'Portal bulk sync disabled',
                'synced_count': 0,
            }
        
        try:
            payload = {
                'action': 'bulk_sync_students',
                'students': [
                    {
                        'admission_number': s.admission_number,
                        'name': s.name,
                        'email': s.email,
                        'phone': s.phone,
                    }
                    for s in students
                ],
                'api_key': self.portal_api_key,
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.portal_api_key}',
            }
            
            response = requests.post(
                f"{self.portal_url}/api/students/bulk-sync",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': result.get('success', True),
                'message': result.get('message', 'Bulk sync completed'),
                'synced_count': result.get('synced_count', len(students)),
            }
        
        except Exception as e:
            logger.error(f"Portal bulk sync error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'synced_count': 0,
            }


class DualSyncService:
    """
    Orchestrates dual-sync to Firebase and Lecturer Portal.
    Ensures attendance data is persisted to both systems.
    """
    
    def __init__(self):
        from .firebase_service import get_firebase_service
        self.firebase = get_firebase_service()
        self.portal = PortalSyncService()
    
    def sync_attendance(self, student: 'Student', session: 'AttendanceSession') -> Dict[str, Any]:
        """
        Record attendance and sync to both Firebase and Portal.
        
        Returns:
            {
                'success': bool,
                'firebase': {'success': bool, 'document_id': str, 'error': str},
                'portal': {'success': bool, 'document_id': str, 'error': str},
                'attendance_percentage': float,
            }
        """
        from .models import Attendance
        
        try:
            # Create or get attendance record
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                session=session,
            )
            
            attendance_percentage = attendance.get_attendance_percentage()
            
            # Build attendance payload
            attendance_data = {
                'student_name': student.name,
                'admission_number': student.admission_number,
                'unit_code': session.unit.code,
                'unit_name': session.unit.name,
                'lecturer_name': session.lecturer.user.get_full_name(),
                'lecturer_id': getattr(session.lecturer, 'staff_id', None),
                'date': str(session.date),
                'time_slot': f"{session.start_time} - {session.end_time}",
                'venue': session.venue,
                'attendance_percentage': float(attendance_percentage),
            }
            
            # Sync to Firebase
            firebase_result = self.firebase.save_attendance(str(session.id), attendance_data)
            if firebase_result.get('success') and firebase_result.get('document_id'):
                attendance.synced_to_firebase = True
                attendance.firebase_doc_id = firebase_result.get('document_id', '')
                attendance.save(update_fields=['synced_to_firebase', 'firebase_doc_id'])
            else:
                # store any returned id/message for troubleshooting but don't mark as synced
                attendance.firebase_doc_id = firebase_result.get('document_id', '') or attendance.firebase_doc_id
                attendance.save(update_fields=['firebase_doc_id'])
            
            # Sync to Portal
            portal_result = self.portal.sync_attendance(attendance, student, session)
            if portal_result.get('success') and portal_result.get('document_id'):
                attendance.synced_to_portal = True
                attendance.portal_response = portal_result
                attendance.save(update_fields=['synced_to_portal', 'portal_response'])
            else:
                # Save portal response for debugging (do not flip synced flag)
                attendance.portal_response = portal_result
                attendance.save(update_fields=['portal_response'])
            
            result = {
                'success': firebase_result.get('success') or portal_result.get('success'),
                'firebase': firebase_result,
                'portal': portal_result,
                'attendance_percentage': float(attendance_percentage),
                'attendance_id': str(attendance.id),
                'created': created,
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Dual sync error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'firebase': {'success': False, 'error': str(e)},
                'portal': {'success': False, 'error': str(e)},
                'attendance_percentage': 0.0,
            }


def get_dual_sync_service() -> DualSyncService:
    """Lazy singleton accessor for DualSyncService."""
    if not hasattr(get_dual_sync_service, '_instance'):
        get_dual_sync_service._instance = DualSyncService()
    return get_dual_sync_service._instance
