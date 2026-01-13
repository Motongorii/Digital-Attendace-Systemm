# Architecture & Data Flow Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Digital Attendance System                     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Student Interface                       │   │
│  │  QR Code Scanner → Attendance Form → Submit              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Django Views (attendance/views.py)            │   │
│  │  student_attend() → Validate → Create/Update Student     │   │
│  │                  → Call DualSyncService                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         DualSyncService (sync_service.py)                │   │
│  │  Orchestrates dual writes to Firebase + Portal           │   │
│  └──────────────────────────────────────────────────────────┘   │
│              ↙                                      ↘              │
│        ┌──────────────┐                    ┌──────────────────┐  │
│        │   Firebase   │                    │  Portal Service  │  │
│        │  (Firestore) │                    │   (REST API)     │  │
│        └──────────────┘                    └──────────────────┘  │
│              ↓                                      ↓               │
│        ┌──────────────┐                    ┌──────────────────┐  │
│        │ Cloud Store  │                    │ Lecturer Portal  │  │
│        │   Records    │                    │  Database        │  │
│        └──────────────┘                    └──────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Admin Interface (/admin/)                         │   │
│  │  View Students │ Manage Attendance │ Monitor Syncs       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Attendance Marking Flow

```
START
  ↓
Student Scans QR Code
  ↓
  ├─ QR Code Valid?
  │  ├─ YES → Continue
  │  └─ NO → Error Page
  ↓
Display Attendance Form
  ↓
Student Enters:
  ├─ Admission Number
  ├─ Full Name
  └─ Clicks Submit
  ↓
VALIDATION
  ├─ Admission number not empty?
  ├─ Student name not empty?
  └─ Session still active?
  ↓
CHECK DUPLICATE
  ├─ Already marked this session?
  │  ├─ YES → Already Marked Page
  │  └─ NO → Continue
  ↓
CREATE/UPDATE STUDENT
  ├─ Student exists?
  │  ├─ YES → Update if needed
  │  └─ NO → Create new Student record
  ├─ Add unit enrollment
  └─ Save to database
  ↓
DUAL-SYNC SERVICE
  ├─ Create Attendance Record (local DB)
  ├─ Calculate Attendance %
  │
  ├─→ Sync to Firebase
  │   ├─ Connected?
  │   │  ├─ YES → POST to Firestore
  │   │  │        ├─ Success? → Mark synced_to_firebase=True
  │   │  │        └─ Error? → Log error, continue
  │   │  └─ NO → Skip
  │
  ├─→ Sync to Portal (Parallel)
  │   ├─ Portal URL configured?
  │   │  ├─ YES → POST /api/attendance/record
  │   │  │        ├─ Success? → Mark synced_to_portal=True
  │   │  │        └─ Error? → Log error, continue
  │   │  └─ NO → Skip
  │
  └─ Return results
  ↓
DISPLAY SUCCESS
  ├─ Student name
  ├─ Unit code & name
  ├─ Session date/time
  ├─ Lecturer name
  └─ Attendance Percentage
  ↓
END
```

## Data Model Relationships

```
┌─────────────┐         ┌─────────────────┐
│   Lecturer  │◄────────│      Unit       │
│             │ created │                 │
│ ├─ user     │         │ ├─ code         │
│ ├─ staff_id │         │ ├─ name         │
│ └─ dept     │         │ └─ description  │
└─────────────┘         └─────────────────┘
                               ▲
                               │
                         many:many
                               │
                        ┌──────┴──────┐
                        │             │
                   ┌────────┐   ┌──────────┐
                   │Student │───│AttSess   │
                   └────────┘   └──────────┘
                        ▲
                        │ one:many
                        │
                   ┌─────────────┐
                   │ Attendance  │
                   │             │
                   │ ├─student   │
                   │ ├─session   │
                   │ ├─timestamp │
                   │ ├─synced_fb │
                   │ └─synced_pl │
                   └─────────────┘

Legend:
▼ = Foreign Key
◄─ = One-to-One
─► = Many-to-One
┼─ = Many-to-Many
```

## Sync Service Architecture

```
DualSyncService
│
├─ firebase: FirebaseService
│  └─ Singleton Firebase connection
│     └─ Lazy initialization
│
├─ portal: PortalSyncService
│  └─ Environment-based configuration
│     ├─ portal_url
│     ├─ portal_api_key
│     └─ timeout
│
└─ sync_attendance(student, session)
   │
   ├─ Step 1: Create Attendance Record
   │  └─ Student + Session → Unique together
   │
   ├─ Step 2: Calculate Percentage
   │  └─ Count attendances / Max lessons
   │
   ├─ Step 3: Parallel Sync ┐
   │  │                      ├─ Independent (no blocking)
   │  ├─→ Firebase          │  ├─ One failure doesn't block other
   │  │   ├─ Connect        │  └─ Both should complete
   │  │   ├─ Add attendance │
   │  │   └─ Return result  │
   │  │                     │
   │  └─→ Portal            │
   │      ├─ Build payload   │
   │      ├─ POST request    │
   │      └─ Return result   │
   │                        ┘
   │
   └─ Step 4: Update Attendance Record
      ├─ Mark Firebase sync status
      ├─ Mark Portal sync status
      ├─ Store portal response
      └─ Return combined result
```

## Attendance Percentage Calculation

```
Formula:
┌─────────────────────────────────────┐
│  Attendance % = (Attended / Max) × 100  │
│                                         │
│  Where:                                 │
│  - Attended = Count of unique sessions  │
│  - Max = 12 (default, configurable)     │
│  - Result = Float percentage (0-100)    │
└─────────────────────────────────────┘

Examples:
┌──────┬──────────┬──────────┐
│ Mark │ Attended │ Percent  │
├──────┼──────────┼──────────┤
│  1/1 │    1     │  8.33%   │
│  2/2 │    2     │ 16.67%   │
│  6/6 │    6     │ 50.00%   │
│  9/9 │    9     │ 75.00%   │
│12/12 │   12     │ 100.0%   │
└──────┴──────────┴──────────┘

Semester = 12 lessons (configurable)
Percentage calculated per unit
```

## Database Schema (Simplified)

```
┌─────────────────────┐
│      Student        │
├─────────────────────┤
│ id (PK)             │
│ admission_number (U)│  ← Unique, indexed for fast lookup
│ name                │
│ email               │
│ phone               │
│ created_at          │
│ updated_at          │
└─────────────────────┘
         ▲
         │ (one:many)
         │
┌─────────────────────┐
│    Attendance       │
├─────────────────────┤
│ id (PK)             │
│ student_id (FK)     │
│ session_id (FK)     │
│ timestamp           │
│ synced_to_firebase  │  ← Boolean, indexed
│ synced_to_portal    │  ← Boolean, indexed
│ firebase_doc_id     │
│ portal_response     │  ← JSONField
│ UQ(student, session)│  ← Unique constraint (no duplicates)
└─────────────────────┘
         ▲
         │ (many:one)
         │
┌──────────────────────┐
│  AttendanceSession   │
├──────────────────────┤
│ id (PK, UUID)        │
│ unit_id (FK)         │
│ lecturer_id (FK)     │
│ date                 │
│ start_time           │
│ end_time             │
│ venue                │
│ is_active            │
│ qr_code (FileField)  │
│ created_at           │
└──────────────────────┘
```

## Error Handling Flow

```
sync_attendance() called
  ↓
TRY
  ├─ Create/Get Attendance
  ├─ Calculate percentage
  │
  ├─→ Firebase Sync
  │   ├─ Timeout? → Log, return {success: false}
  │   ├─ Connection? → Log, return {success: false}
  │   ├─ Exception? → Log, return {success: false}
  │   └─ Success? → Mark record, return {success: true}
  │
  ├─→ Portal Sync (independent of Firebase)
  │   ├─ Not configured? → return {success: true, message: "disabled"}
  │   ├─ Timeout? → Log, return {success: false}
  │   ├─ Connection? → Log, return {success: false}
  │   ├─ HTTP error? → Log, return {success: false, error: msg}
  │   └─ Success? → Mark record, return {success: true}
  │
  └─ Return combined results
  
CATCH Exception
  ├─ Log full stack trace
  └─ Return {success: false, error: "..."}

Result Structure:
{
  'success': bool (true if firebase OR portal succeeded),
  'firebase': {result},
  'portal': {result},
  'attendance_percentage': float,
  'attendance_id': str,
  'created': bool
}
```

## Environment Configuration Flow

```
.env file
  ↓
django.conf.settings
  ↓
os.getenv() calls
  ↓
┌────────────────────────────────┐
│   Configuration Variables      │
├────────────────────────────────┤
│                                │
│ FIREBASE_CREDENTIALS_PATH      │
│  → FirebaseService             │
│  → Initialize Firestore        │
│                                │
│ LECTURER_PORTAL_API_URL        │
│  → PortalSyncService           │
│  → Enable/disable portal sync  │
│                                │
│ LECTURER_PORTAL_API_KEY        │
│  → PortalSyncService           │
│  → Authorization header        │
│                                │
│ PORTAL_SYNC_TIMEOUT (default:10│
│  → PortalSyncService           │
│  → Request timeout in seconds  │
│                                │
└────────────────────────────────┘
```

## Deployment Topology

```
Production Server
│
├─ Django Application
│  ├─ Views (attendance/views.py)
│  ├─ Models (attendance/models.py)
│  ├─ Services (attendance/sync_service.py)
│  └─ Database (PostgreSQL/MySQL)
│
├─ External Services (over HTTPS)
│  │
│  ├─ Firebase Firestore
│  │  └─ POST auth + data
│  │  └─ Response: document_id
│  │
│  └─ Lecturer Portal API
│     └─ POST /api/attendance/record
│     └─ Response: JSON status
│
└─ Admin Interface
   └─ View/manage Attendance & Student records
```

---

These diagrams illustrate:
1. How data flows through the system
2. Service relationships and responsibilities
3. Database structure and relationships
4. Attendance percentage calculation
5. Error handling strategies
6. Environmental configuration
7. Production deployment topology

---

## Firebase & Database Deep Dive 🔍

### Quick summary
- The app uses a **local relational DB** (Django models) for authoritative student/session/attendance data and **Firestore** (Firebase) as a realtime/remote store for attendance synchronization and cross-device deduplication.
- Writes are performed locally first (fast response), then propagated asynchronously to Firebase and the Lecturer Portal via the DualSyncService.

### Firestore structure (what to explain)
- Top-level collection: `attendance_records` (flat timeline of attendance writes)
- Session-scoped collection: `sessions/{session_id}/students/{admission_number}` — used to check "already marked" across devices
- Each student doc contains: session_id, student_name, admission_number, unit_code, unit_name, lecturer_name, date, time_slot, venue, timestamp

### Key components & responsibilities
- `FirebaseService` (attendance/firebase_service.py)
  - Lazy initialization from `FIREBASE_CREDENTIALS_JSON` or `FIREBASE_CREDENTIALS_PATH` or bundled `firebase-credentials.json`
  - `save_attendance(session_id, student_data)` → writes to `attendance_records` and session subcollection and returns {success, document_id, message/error}
  - `check_already_marked(session_id, admission_number)` → prevents duplicates

- `DualSyncService` (attendance/sync_service.py)
  - Orchestrates local DB write → Firebase → Portal
  - Updates `Attendance` model fields: `synced_to_firebase`, `firebase_doc_id`, `synced_to_portal`, `portal_response`

- Views & Signals
  - `student_attend()` creates local `Attendance` immediately and spawns a background thread for `get_dual_sync_service().sync_attendance(...)`
  - `post_save` signal on `Attendance` is another background sync safety-net (best-effort)

### Sync semantics & idempotency
- Local DB enforces uniqueness with `unique_together=(student, session)` to avoid duplicates at DB level.
- Firestore checks use deterministic document IDs by admission number under a session subcollection — reads are used to dedupe cross-device marks.
- If Firebase write fails, the local `Attendance` remains (and is not marked `synced_to_firebase`). The `firebase_doc_id` may still be set if an ID was returned.

### Failure modes & how to explain them
- Missing/invalid Firebase credentials → FirebaseService sets `.db=None` and `is_connected=False` (the app continues to function locally).
- Network timeout / portal failure → PortalSyncService returns structured error in `portal_response` and `synced_to_portal` remains False.
- Partial success (Firebase ok, Portal fail) → The `Attendance` record holds precise status for each target so operators can retry.

### Operational commands & debugging
- `python manage.py firebase_cleanup --session-id <id> --confirm` → backup and delete Firebase content safely (use `--dry-run` first)
- Admin UI shows `firebase_doc_id` and `portal_response` (readonly) for auditing
- Test connection: `test_app.py` includes a simple Firebase import & connection sanity check

### Quick talking points (one-paragraph cheat sheet) ✨
- "We write attendance locally first, then asynchronously sync to Firestore and our Lecturer Portal. Firestore is used for cross-device deduplication using `sessions/{id}/students/{admission_number}`, while the relational DB is the authoritative record and includes sync status fields so we can audit and retry failed syncs. Credentials come from env vars or the repo file; missing credentials do not break marking." 

For detailed implementation, see `DUAL_SYNC_DOCUMENTATION.md` and `PORTAL_INTEGRATION_GUIDE.md`.
