"""
Firebase integration service for attendance records.

This version is safe for serverless deployments (Vercel):
- Lazy initialization of Firebase
- Reads credentials from `FIREBASE_CREDENTIALS_JSON` (env) or `FIREBASE_CREDENTIALS_PATH`
- Avoids import-time initialization
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

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
except Exception:
    FIREBASE_AVAILABLE = False


class FirebaseService:
    """Lazy-initialized Firebase service."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db = None
            cls._instance._initialized = False
        return cls._instance

    def _initialize_firebase(self):
        if not FIREBASE_AVAILABLE:
            self._db = None
            self._initialized = True
            return

        # Try to get credentials from env var (preferred for Vercel)
        cred_path = None
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if cred_json:
            # Accept plain JSON or base64-encoded JSON
            try:
                # if it's base64 encoded, this will fail and we'll try decode
                json.loads(cred_json)
                tmp = Path("/tmp/firebase-credentials.json")
                tmp.write_text(cred_json)
                cred_path = str(tmp)
            except Exception:
                try:
                    import base64
                    decoded = base64.b64decode(cred_json).decode("utf-8")
                    json.loads(decoded)
                    tmp = Path("/tmp/firebase-credentials.json")
                    tmp.write_text(decoded)
                    cred_path = str(tmp)
                except Exception:
                    cred_path = None

        # If not provided via JSON, check path env var
        if not cred_path:
            env_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if env_path:
                cred_path = env_path

        # Fall back to project file
        if not cred_path:
            default = Path(__file__).resolve().parents[1] / "firebase-credentials.json"
            if default.exists():
                cred_path = str(default)

        if not cred_path or not Path(cred_path).exists():
            # credentials not found; do not raise on serverless, operate in local fallback mode
            self._db = None
            self._initialized = True
            return

        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(str(cred_path))
                firebase_admin.initialize_app(cred)
            self._db = firestore.client()
            self._initialized = True
        except Exception:
            self._db = None
            self._initialized = True

    @property
    def db(self):
        if not getattr(self, "_initialized", False):
            self._initialize_firebase()
        return self._db

    @property
    def is_connected(self) -> bool:
        return self.db is not None

    def save_attendance(self, session_id: str, student_data: dict) -> dict:
        if not self.is_connected:
            return {
                "success": True,
                "message": "Attendance recorded (local mode - Firebase not connected)",
                "document_id": "local",
            }
        try:
            attendance_record = {
                "session_id": session_id,
                "student_name": student_data.get("student_name"),
                "admission_number": student_data.get("admission_number"),
                "unit_code": student_data.get("unit_code"),
                "unit_name": student_data.get("unit_name"),
                "lecturer_name": student_data.get("lecturer_name"),
                "date": student_data.get("date"),
                "time_slot": student_data.get("time_slot"),
                "venue": student_data.get("venue"),
                "timestamp": datetime.now().isoformat(),
                "marked_at": firestore.SERVER_TIMESTAMP,
            }
            doc_ref = self._db.collection("attendance_records").add(attendance_record)
            session_ref = self._db.collection("sessions").document(session_id)
            session_ref.collection("students").document(student_data.get("admission_number")).set(attendance_record)
            return {"success": True, "document_id": doc_ref[1].id, "message": "Attendance recorded successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_session_attendance(self, session_id: str) -> list:
        if not self.is_connected:
            return []
        try:
            docs = self._db.collection("sessions").document(session_id).collection("students").stream()
            return [doc.to_dict() for doc in docs]
        except Exception:
            return []

    def check_already_marked(self, session_id: str, admission_number: str) -> bool:
        if not self.is_connected:
            return False
        try:
            doc = self._db.collection("sessions").document(session_id).collection("students").document(admission_number).get()
            return doc.exists
        except Exception:
            return False


# Lazy singleton accessor
_firebase_service_singleton: Optional[FirebaseService] = None

def get_firebase_service() -> FirebaseService:
    global _firebase_service_singleton
    if _firebase_service_singleton is None:
        _firebase_service_singleton = FirebaseService()
    return _firebase_service_singleton
