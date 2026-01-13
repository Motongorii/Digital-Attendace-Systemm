"""
Firebase integration service for attendance records.

Features:
- Lazy initialization of Firebase
- Reads credentials from `FIREBASE_CREDENTIALS_JSON` (env) or `FIREBASE_CREDENTIALS_PATH`
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

        # Try to get credentials from env var
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
        """
        Record lecturer usage in Firebase instead of storing individual student records.

        This method will:
        - Ensure we **do not** write student-identifying records to Firebase.
        - Increment a per-lecturer usage counter and set `last_active`.
        - Store only minimal **session metadata** (no student list) under the lecturer's `sessions` subcollection.
        """
        if not self.is_connected:
            # Firebase not available — indicate skipped remote sync so callers don't mark record as synced
            return {
                "success": False,
                "skipped": True,
                "message": "Firebase not connected; lecturer usage not recorded remotely",
                "document_id": None,
            }
        try:
            # Use a stable lecturer identifier when available (lecturer_id). Fall back to normalized lecturer_name.
            lecturer_id = student_data.get("lecturer_id") or (student_data.get("lecturer_name") or "unknown").lower().replace(" ", "_")
            lecturer_name = student_data.get("lecturer_name") or "Unknown Lecturer"

            # Update lecturer usage doc
            lecturer_ref = self._db.collection("lecturer_usage").document(lecturer_id)
            lecturer_ref.set({
                "lecturer_name": lecturer_name,
                "last_active": firestore.SERVER_TIMESTAMP,
            }, merge=True)

            # atomically increment usage_count
            try:
                lecturer_ref.update({"usage_count": firestore.Increment(1)})
            except Exception:
                # If update failed (e.g., doc did not exist in some older Firestore SDKs), set the field
                lecturer_ref.set({"usage_count": 1}, merge=True)

            # Store session metadata (no student details)
            session_meta = {
                "session_id": session_id,
                "unit_code": student_data.get("unit_code"),
                "unit_name": student_data.get("unit_name"),
                "venue": student_data.get("venue"),
                "timestamp": datetime.now().isoformat(),
            }
            lecturer_ref.collection("sessions").document(str(session_id)).set(session_meta, merge=True)

            return {"success": True, "document_id": lecturer_id, "message": "Lecturer usage recorded"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_session_attendance(self, session_id: str) -> list:
        """
        For privacy, Firebase does not store student lists. This returns an empty list.
        Use local DB / portal API to view per-session student attendance.
        """
        return []

    def check_already_marked(self, session_id: str, admission_number: str) -> bool:
        """
        We do not track per-student marks in Firebase — this check should be done locally.
        """
        return False

    def diagnose(self) -> dict:
        """Return a small diagnostic summary about Firebase connectivity.

        Useful keys:
            - available: bool (is firebase_admin installed)
            - connected: bool (is Firestore client available)
            - collections_count: int (if readable)
            - error: str (error message when a call failed)
        """
        res = {"available": FIREBASE_AVAILABLE, "connected": self.is_connected}
        if not self.is_connected:
            return res
        try:
            cols = [c.id for c in self._db.collections()]
            res['collections_count'] = len(cols)
            return res
        except Exception as e:
            res['error'] = str(e)
            return res


# Lazy singleton accessor
_firebase_service_singleton: Optional[FirebaseService] = None

def get_firebase_service() -> FirebaseService:
    global _firebase_service_singleton
    if _firebase_service_singleton is None:
        _firebase_service_singleton = FirebaseService()
    return _firebase_service_singleton


# Backwards-compatible module-level instance
# Older code/tests import `firebase_service` from this module, so expose
# a singleton instance named `firebase_service` to avoid import errors.
firebase_service = get_firebase_service()
