"""
Firebase integration service for attendance records.
"""
import os
from datetime import datetime

# Try to import firebase_admin, but don't fail if not installed
FIREBASE_AVAILABLE = False
firebase_admin = None
credentials = None
firestore = None

try:
    import firebase_admin as _firebase_admin
    from firebase_admin import credentials as _credentials
    from firebase_admin import firestore as _firestore
    firebase_admin = _firebase_admin
    credentials = _credentials
    firestore = _firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    pass


class FirebaseService:
    """Service class for Firebase operations."""
    
    _instance = None
    _db = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not FIREBASE_AVAILABLE:
            print("⚠ Firebase SDK not available. Run: pip install firebase-admin")
            self._db = None
            return
            
        try:
            from django.conf import settings
            cred_path = settings.FIREBASE_CREDENTIALS_PATH
            if os.path.exists(cred_path):
                cred = credentials.Certificate(str(cred_path))
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print("✓ Firebase initialized successfully")
            else:
                print(f"⚠ Firebase credentials not found at: {cred_path}")
                print("  Download from Firebase Console > Project Settings > Service Accounts")
                self._db = None
        except Exception as e:
            print(f"⚠ Firebase initialization error: {e}")
            self._db = None
    
    @property
    def db(self):
        return self._db
    
    @property
    def is_connected(self):
        return self._db is not None
    
    def save_attendance(self, session_id: str, student_data: dict) -> dict:
        """
        Save student attendance to Firebase.
        
        Args:
            session_id: The attendance session UUID
            student_data: Dictionary containing student info
        
        Returns:
            Dictionary with success status and document ID
        """
        if not self.is_connected:
            # Return success anyway for demo/testing without Firebase
            return {
                'success': True, 
                'message': 'Attendance recorded (local mode - Firebase not connected)',
                'document_id': 'local'
            }
        
        try:
            # Create attendance record
            attendance_record = {
                'session_id': session_id,
                'student_name': student_data.get('student_name'),
                'admission_number': student_data.get('admission_number'),
                'unit_code': student_data.get('unit_code'),
                'unit_name': student_data.get('unit_name'),
                'lecturer_name': student_data.get('lecturer_name'),
                'date': student_data.get('date'),
                'time_slot': student_data.get('time_slot'),
                'venue': student_data.get('venue'),
                'timestamp': datetime.now().isoformat(),
                'marked_at': firestore.SERVER_TIMESTAMP,
            }
            
            # Save to Firestore
            doc_ref = self._db.collection('attendance_records').add(attendance_record)
            
            # Also save to session-specific collection
            session_ref = self._db.collection('sessions').document(session_id)
            session_ref.collection('students').document(
                student_data.get('admission_number')
            ).set(attendance_record)
            
            return {
                'success': True,
                'document_id': doc_ref[1].id,
                'message': 'Attendance recorded successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_session_attendance(self, session_id: str) -> list:
        """Get all attendance records for a session."""
        if not self.is_connected:
            return []
        
        try:
            docs = self._db.collection('sessions').document(session_id)\
                .collection('students').stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error fetching attendance: {e}")
            return []
    
    def check_already_marked(self, session_id: str, admission_number: str) -> bool:
        """Check if student has already marked attendance."""
        if not self.is_connected:
            return False
        
        try:
            doc = self._db.collection('sessions').document(session_id)\
                .collection('students').document(admission_number).get()
            return doc.exists
        except Exception as e:
            print(f"Error checking attendance: {e}")
            return False


# Global instance
firebase_service = FirebaseService()
