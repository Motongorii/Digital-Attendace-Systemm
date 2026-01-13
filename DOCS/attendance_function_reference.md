# Attendance App — Function & Class Reference 📚

Purpose: Single-file reference that documents functions, classes, and important behaviors in the `attendance` Django app — useful for developers and for explaining the codebase to stakeholders.



## Table of contents
- models.py
- firebase_service.py
- sync_service.py
- views.py
- forms.py
- qr_generator.py
- signals.py
- admin.py
- management/commands/firebase_cleanup.py
- tests

---

## models.py

### Lecturer (Model)
- Signature: `class Lecturer(models.Model)`
- Purpose: Link a `User` to lecturer metadata.
- Fields: `user`, `staff_id`, `department`, `phone`.
- Side effects: None.
- Called from: `Unit.lecturer` FK, views that fetch `request.user.lecturer`.
- One-liner: Stores lecturer identity and contact info.

### Unit (Model)
- Signature: `class Unit(models.Model)`
- Purpose: Represent a course unit taught by a Lecturer.
- Fields: `code`, `name`, `lecturer`, `description`.
- Note: `code` is unique.

### AttendanceSession (Model)
- Signature: `class AttendanceSession(models.Model)`
- Purpose: Represents a single scheduled session (date/time) for a Unit.
- Important methods:
  - `get_session_info() -> dict` — returns session metadata for QR payload.
- Important fields: UUID `id` (used as `session_id` across Firestore), `unit`, `lecturer`, `date`, `start_time`, `end_time`, `venue`, `qr_code`, `session_number`, `semester`, `is_active`.
- Constraints: Unique constraints prevent duplicate sessions for same unit/time and duplicate session numbers per semester.

### Student (Model)
- Signature: `class Student(models.Model)`
- Purpose: Stores student details and enrollments.
- Fields: `admission_number` (unique), `name`, `email`, `phone`, `units` (M2M)
- Important methods:
  - `get_attendance_percentage(unit=None, semester=1, max_lessons=12) -> Decimal` — computes percent; if `unit` None, computes overall.
- Side-effects: `units` M2M updated when a student is assigned to a session's unit.

### Attendance (Model)
- Signature: `class Attendance(models.Model)`
- Purpose: Record a student's attendance for a session.
- Fields: `student`, `session`, `timestamp`, `synced_to_firebase`, `synced_to_portal`, `firebase_doc_id`, `portal_response` (JSONField).
- Constraints: `unique_together = ('student', 'session')` — prevents DB duplicates.
- Important methods:
  - `get_attendance_percentage(max_lessons=12)` delegates to `Student.get_attendance_percentage(unit=...)`.
- Side-effects: Fields updated by `DualSyncService` after remote writes.

---

## firebase_service.py ☁️

### Module behavior
- Lazy imports `firebase_admin`, `credentials`, `firestore`. If not available, sets `FIREBASE_AVAILABLE=False` and `FirebaseService.is_connected` remains False.
- Credential sources (priority):
  1. `FIREBASE_CREDENTIALS_JSON` (env) — raw or base64-encoded
  2. `FIREBASE_CREDENTIALS_PATH` (env)
  3. `firebase-credentials.json` file in repo root
- Singleton accessor: `get_firebase_service()` and module alias `firebase_service`.

### FirebaseService (class)
- Signature: `class FirebaseService` (singleton)
- Important props:
  - `db` — Firestore client (initialized on first access)
  - `is_connected` — `bool(db is not None)`
- Methods:
  - `save_attendance(session_id: str, student_data: dict) -> dict`
    - Purpose: Write an attendance record to Firestore.
    - Behavior: Adds to `attendance_records` and sets doc at `sessions/{session_id}/students/{admission_number}`.
    - Returns: `{'success': True, 'document_id': <id>, 'message': ...}` on success; on failure returns `{'success': False, 'error': ...}`. If Firebase not connected, returns `{success: False, skipped: True, message: ...}` to indicate skipped remote sync.
  - `get_session_attendance(session_id: str) -> list` — returns list of docs from `sessions/{session_id}/students`.
  - `check_already_marked(session_id: str, admission_number: str) -> bool` — checks existence of student doc in session subcollection.
- Edge cases: All network operations wrapped in try/except to avoid crashing request threads; service tolerates missing credentials.

---

## sync_service.py 🔁

### PortalSyncService
- Signature: `class PortalSyncService`
- Purpose: POST attendance and students to an external Lecturer Portal API.
- Configuration: `LECTURER_PORTAL_API_URL`, `LECTURER_PORTAL_API_KEY`, `PORTAL_SYNC_TIMEOUT`.
- Methods:
  - `sync_attendance(attendance_record, student, session) -> dict`
    - Builds payload with student details and attendance metadata, posts to `{portal_url}/api/attendance/record`.
    - Returns structured result `{'success': bool, 'message'|'error': str, 'document_id': id}`.
  - `sync_student_bulk(students: list) -> dict` — used for bulk student syncs.

### DualSyncService
- Signature: `class DualSyncService`
- Purpose: Orchestrate local DB `Attendance` creation and dual writes to Firebase and Portal.
- Important method:
  - `sync_attendance(student: Student, session: AttendanceSession) -> dict`
    - Steps:
      1. Get or create local `Attendance` (DB authoritative).
      2. Compute `attendance_percentage`.
      3. Call `firebase.save_attendance(session_id, attendance_data)` → on success set `synced_to_firebase=True`, store `firebase_doc_id`.
      4. Call `portal.sync_attendance(...)` → on success set `synced_to_portal=True`, store `portal_response`.
      5. Save DB changes and return combined result with `firebase` and `portal` statuses and `attendance_id`.
- Error handling: Exceptions are caught and returned as failure results; partial success is handled by leaving the corresponding sync flags/fields set appropriately.
- Accessor: `get_dual_sync_service()` returns a singleton instance.

---

## views.py 🖥️

All views are located in `attendance/views.py`; notable functions and their responsibilities:

### `student_attend(request, session_id)`
- Purpose: Flow for students who scan QR and submit admission number and full name.
- GET: Render `StudentAttendanceForm`.
- POST:
  - Validate form data.
  - Check duplicate marking in Firestore using `get_firebase_service().check_already_marked(session_id, admission_number)` when available; fallback to local DB check `Attendance.objects.filter(...).exists()`.
  - Get or create `Student` and update name if different.
  - Add the `Unit` to student's `units` M2M if not already present.
  - Create/get local `Attendance` immediately (fast response) and start background thread to call `get_dual_sync_service().sync_attendance(att.student, att.session)` (daemon thread).
  - Return `success.html` with `attendance_percentage`.
- Side effects: Updates student model and may spawn background thread that modifies `Attendance` sync fields later.

### `lecturer_dashboard(request)`
- Authenticated view showing lecturer units and sessions; uses `select_related` to reduce DB queries.

### `create_session(request)`
- Purpose: Save a new `AttendanceSession` using `AttendanceSessionForm`.
- Validations: Prevent duplicate times and ensure `session_number` assigned 1..13 per unit/semester.
- QR generation: Resolves `base_url` (attempts to detect LAN IP if running locally), generates QR via `generate_session_qr()` and saves to `session.qr_code`.

### `session_detail(request, session_id)`
- Purpose: Present session info and attendance list.
- Behavior:
  - Attempts to fetch attendance records from Firebase in a short background thread (join timeout 2s), caching results for 5s.
  - Fallback: Load from local DB (latest 100 records) when Firebase unavailable or for display.
  - Computes per-student `attendance_percentage` and returns `session_detail.html`.

### `api_status(request)`
- Purpose: API to get system status; returns `firebase_connected`, current `timestamp`, and `attendance_count` for a given `session_id` (max of Firebase or local DB counts).

Additional views: `toggle_session`, `create_unit`, `create_unit_ajax`, `lecturer_login`, `lecturer_logout`, `download_qr` — documented inline in the code and used in templates/admin.

---

## forms.py 📝

- `AttendanceSessionForm` (ModelForm) — used to validate and save session creation input.
- `StudentAttendanceForm` (Form) — fields: `student_name`, `admission_number`; includes cleaning helpers `clean_admission_number()` and `clean_student_name()` which normalize input.
- `UnitForm` (ModelForm) — unit create/edit form.

---

## qr_generator.py 🔳

- `generate_session_qr(session, base_url) -> ContentFile`
  - Purpose: Produce a PNG QR image linking to `"{base_url}/attend/{session.id}/"`.
  - Behavior: Uses `qrcode` and styled image support if available; falls back to a 1×1 PNG placeholder if `qrcode` missing.
- `generate_simple_qr(data: str) -> bytes` — returns QR bytes or empty bytes if dependency missing.

---

## signals.py 🔔

- `attendance_post_save(sender, instance, created, **kwargs)`
  - Receiver on `post_save` for `Attendance`.
  - If `created`, starts a daemon thread to call `get_dual_sync_service().sync_attendance(att.student, att.session)` — a safety-net that ensures background sync happens even when record created outside the `student_attend` view.

---

## admin.py 

- Django admin configured with helpful read-only fields:
  - `AttendanceAdmin` shows `synced_to_firebase`, `firebase_doc_id`, `synced_to_portal`, `portal_response` for auditing.

---

## management/commands/firebase_cleanup.py 

- CLI to backup and optionally delete Firestore data.
- Key flags: `--dry-run`, `--session-id <id>`, `--all`, `--confirm`.
- Behavior: Reads `sessions` and `attendance_records`, writes a backup JSON, and deletes when `--confirm` provided.

---

## tests

- `attendance/tests/test_firebase_service_import.py` verifies `firebase_service` importability and its `is_connected`/`db` attributes (smoke test).
- `attendance/tests/test_qr_view.py` validates QR-related endpoints.

---

## Quick cheat-sheet (for verbal explanation) 
- "We save attendance locally first for reliability, then asynchronously sync to Firestore (for real-time cross-device dedupe) and to the Lecturer Portal (for central data ingestion). Sync results are recorded on the `Attendance` model (`synced_to_firebase`, `firebase_doc_id`, `synced_to_portal`, `portal_response`) so staff can audit or retry failures." 

---


