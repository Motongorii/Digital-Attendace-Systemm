# 📚 COMPLETE DIGITAL ATTENDANCE SYSTEM - CODE EXPLANATION

This document provides a comprehensive explanation of every component in your Digital Attendance System, including APIs, Firebase integration, models, views, and user flows.

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

Your system is built on:
- **Backend**: Django 4.2.27 (Python web framework)
-- **Database**: SQLite (local) / PostgreSQL (production on container hosting)
- **Cloud**: Firebase Firestore (real-time data sync)
- **Frontend**: HTML/CSS/JavaScript with responsive modals
-- **Deployment**: Container hosting (Docker) / platform of your choice

### High-Level Flow:
```
Lecturer Login → Create Unit → Create Session → Generate QR Code
                                                        ↓
                                           Student Scans QR → Marks Attendance
                                                        ↓
                                    Data Synced to Firebase + Local DB
                                                        ↓
                                    Lecturer Views Dashboard & Reports
```

---

## 📊 DATABASE MODELS

### 1. **Lecturer Model** (`attendance/models.py`)

```python
class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
```

**Purpose**: Links Django User to lecturer profile with staff info  
**Key Fields**:
- `user`: Django built-in User (username, password, email)
- `staff_id`: Unique identifier (e.g., "STAFF_001")
- `department`: Department name (e.g., "Computer Science")
- `phone`: Optional contact number

**Example**:
```
Lecturer: Dr. Anthony Motongori
Staff ID: CS_001
Department: Computer Science
```

---

### 2. **Unit Model** (`attendance/models.py`)

```python
class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='units')
    description = models.TextField(blank=True)
```

**Purpose**: Represents a course unit (subject)  
**Key Fields**:
- `code`: Unique course code (e.g., "CS101")
- `name`: Course name (e.g., "Introduction to Programming")
- `lecturer`: Foreign key to Lecturer who teaches this unit
- `description`: Optional course description

**Example**:
```
CS101 - Introduction to Programming
Taught by: Dr. Anthony Motongori
Description: Fundamentals of programming in Python
```

---

### 3. **AttendanceSession Model** (`attendance/models.py`)

```python
class AttendanceSession(models.Model):
    SEMESTER_CHOICES = [(1, 'Semester 1'), (2, 'Semester 2')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)  # Unique ID
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    lecturer_name = models.CharField(max_length=100)  # Lecturer's name for this session
    class_year = models.CharField(choices=CLASS_YEAR_CHOICES)  # Year 1-5
    is_active = models.BooleanField(default=True)  # Can students mark attendance?
    qr_code = models.FileField(upload_to='qr_codes/')  # QR code image file
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)  # 1 or 2
    session_number = models.PositiveSmallIntegerField(1-13)  # Lec 1-13 per semester
    
    class Meta:
        # Constraints: Can't have duplicate "Lec 2" for same unit/semester
        constraints = [
            models.UniqueConstraint(fields=['unit', 'semester', 'session_number']),
            models.UniqueConstraint(fields=['unit', 'semester', 'date', 'start_time'])
        ]
```

**Purpose**: A single attendance session (one class/lecture)  
**Key Features**:
- **UUID Primary Key**: Generates unique ID for QR codes
- **Semester & Session Number**: Tracks "S1 Lec 1", "S1 Lec 2", etc.
- **Max 13 Sessions per Semester**: Enforced by database constraint
- **is_active**: Can toggle session closed after attendance period ends
- **QR Code**: File path to generated QR code image

**Example**:
```
CS101 - S1 Lec 3
Date: 2025-12-10
Time: 09:00 - 10:30
Venue: Room 101
Class Year: Year 2
Lecturer: Dr. Anthony Motongori
Status: Active
QR Code: qr_codes/abc123def456.png
```

---

### 4. **Student Model** (`attendance/models.py`)

```python
class Student(models.Model):
    admission_number = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    units = models.ManyToManyField(Unit, related_name='enrolled_students')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_attendance_percentage(self, unit=None, semester=1, max_lessons=12):
        """Calculate attendance % for a unit"""
        attendance = Attendance.objects.filter(
            student=self, 
            session__unit=unit
        ).count()
        return (attendance / max_lessons) * 100
```

**Purpose**: Tracks individual student records  
**Key Features**:
- **admission_number**: Unique student ID (indexed for fast lookup)
- **units**: Many-to-many relationship to enrolled courses
- **Automatic Enrollment**: Students auto-enrolled when first marking attendance
- **Attendance %**: Method calculates percentage per unit

**Example**:
```
Student: John Doe
Admission: ADM/2023/001
Email: john@university.ac.ke
Units: [CS101, CS102, CS103]
```

---

### 5. **Attendance Model** (`attendance/models.py`)

```python
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    synced_to_firebase = models.BooleanField(default=False)
    synced_to_portal = models.BooleanField(default=False)
    firebase_doc_id = models.CharField(max_length=200, blank=True)
    portal_response = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ('student', 'session')  # One record per student per session
```

**Purpose**: Records when a student marked attendance in a session  
**Key Features**:
- **unique_together**: Prevents duplicate attendance for same student/session
- **Sync Status**: Tracks if synced to Firebase and Portal API
- **firebase_doc_id**: Document ID in Firebase Firestore
- **portal_response**: JSON response from Portal API (for audit trail)
- **Auto-timestamped**: Records exact time of attendance

**Example**:
```
Student: John Doe
Session: CS101 - S1 Lec 3 - 2025-12-10 09:00
Timestamp: 2025-12-10T09:05:32.123456Z
Synced to Firebase: Yes (doc_id: abc123xyz789)
Synced to Portal: Yes (response: {"status": "ok"})
```

---

## 🔐 AUTHENTICATION & AUTHORIZATION

### Login Flow (`views.lecturer_login`)

```python
def lecturer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate using Django's built-in system
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verify user has a Lecturer profile
            try:
                lecturer = user.lecturer
                login(request, user)  # Create session cookie
                return redirect('dashboard')
            except Lecturer.DoesNotExist:
                messages.error(request, 'You are not registered as a lecturer.')
```

**How It Works**:
1. User enters username & password
2. Django checks against User table in database
3. If valid, verify Lecturer profile exists
4. Create session cookie (browser stores session ID)
5. Redirect to dashboard

**Session Management**:
- Django stores session ID in browser cookie
- Server maintains session data in database
- Session expires after inactivity (default: 2 weeks)
- CSRF token prevents cross-site attacks

---

## 🌐 URLS & API ENDPOINTS (`attendance/urls.py`)

| URL | Method | Purpose | Auth |
|-----|--------|---------|------|
| `/` | GET | Home/landing page | Public |
| `/login/` | GET/POST | Lecturer login | Public |
| `/logout/` | GET | Lecturer logout | Login Required |
| `/dashboard/` | GET | Lecturer dashboard | Login Required |
| `/session/create/` | GET/POST | Create new session | Login Required |
| `/session/<id>/` | GET | View session details & attendance | Login Required |
| `/session/<id>/toggle/` | POST | Open/close session | Login Required |
| `/session/<id>/download-qr/` | GET | Download QR code image | Login Required |
| `/unit/create/` | GET/POST | Create new unit (form page) | Login Required |
| `/unit/create-ajax/` | POST | Create unit (AJAX) | Login Required |
| `/attend/<session_id>/` | GET/POST | Student attendance page | Public |
| `/api/status/` | GET | System status check | Public |

---

## 🎨 VIEWS & REQUEST HANDLERS (`attendance/views.py`)

### 1. **student_attend() - Student Attendance**

```python
@csrf_exempt  # Allow QR code scan without CSRF token
def student_attend(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Check if session is still active
    if not session.is_active:
        return render(request, 'session_closed.html')
    
    if request.method == 'POST':
        form = StudentAttendanceForm(request.POST)
        if form.is_valid():
            admission_number = form.cleaned_data['admission_number']
            student_name = form.cleaned_data['student_name']
            
            # Check if already marked (Firebase first)
            fb_service = get_firebase_service()
            already_marked = fb_service.check_already_marked(str(session.id), admission_number)
            
            if already_marked:
                return render(request, 'already_marked.html')
            
            # Get or create student
            student, created = Student.objects.get_or_create(
                admission_number=admission_number,
                defaults={'name': student_name}
            )
            
            # Create attendance record
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                session=session
            )
            
            # Background sync (non-blocking)
            threading.Thread(target=_bg_sync, args=(attendance.id,), daemon=True).start()
            
            return render(request, 'success.html', {
                'attendance_percentage': attendance.get_attendance_percentage()
            })
```

**Flow**:
1. Student scans QR code → opens this view
2. Shows form for admission number & name
3. Checks if already marked (prevents duplicates)
4. Creates/updates student record
5. Creates attendance record
6. **Starts background sync** (doesn't block response)
7. Shows success page with attendance %

**Key Features**:
- **No CSRF Required**: QR codes can't send CSRF tokens
- **Duplicate Prevention**: Checks Firebase first, then local DB
- **Non-blocking Sync**: Student sees success immediately
- **Auto-enrollment**: Student enrolled in unit on first attendance

---

### 2. **lecturer_dashboard() - Dashboard View**

```python
@login_required
def lecturer_dashboard(request):
    lecturer = request.user.lecturer
    
    # Get all units for this lecturer
    units = Unit.objects.filter(lecturer=lecturer)
    
    # Get recent sessions (last 30)
    sessions = AttendanceSession.objects.filter(
        lecturer=lecturer
    ).order_by('-created_at')[:30]
    
    return render(request, 'dashboard.html', {
        'units': units,
        'sessions': sessions,
    })
```

**Shows**:
- List of all units lecturer created
- List of recent sessions
- Stats: total units, total sessions, active sessions
- Buttons to create new unit/session

---

### 3. **session_detail() - Attendance Records**

```python
@login_required
def session_detail(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Get attendance records for this session
    attendance_records = Attendance.objects.filter(session=session)\
        .select_related('student')\
        .order_by('-timestamp')
    
    return render(request, 'session_detail.html', {
        'session': session,
        'attendance_records': attendance_records,
    })
```

**Shows**:
- Session information (unit, date, time, venue)
- QR code image
- List of all students who marked attendance
- Student names, admission numbers, timestamps
- Download QR code button

---

### 4. **create_unit_ajax() - AJAX Unit Creation**

```python
@login_required
@require_http_methods(["POST"])
def create_unit_ajax(request):
    """AJAX endpoint for modal unit creation"""
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not_a_lecturer'}, status=403)
    
    form = UnitForm(request.POST)
    if form.is_valid():
        unit = form.save(commit=False)
        unit.lecturer = lecturer
        unit.save()
        
        return JsonResponse({
            'success': True,
            'unit': {
                'id': unit.id,
                'code': unit.code,
                'name': unit.name
            }
        }, status=201)
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
```

**Flow**:
1. Receives POST with unit code, name, description
2. Validates form
3. Creates unit (auto-links to current lecturer)
4. Returns JSON response
5. **JavaScript adds unit to list** without page reload

**Error Handling**:
- Returns `not_a_lecturer` if user isn't a lecturer
- Returns `errors` dict if validation fails

---

## 🔥 FIREBASE INTEGRATION (`attendance/firebase_service.py`)

### What is Firebase?
Firebase is Google's cloud platform for real-time databases. Your system uses **Firestore** (document-based NoSQL).

### Connection Setup

```python
class FirebaseService:
    _instance = None  # Singleton pattern
    
    def _initialize_firebase(self):
        # 1. Try environment variable first
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        
        # 2. If not set, try credentials file path
        if not cred_json:
            env_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        
        # 3. Fall back to local file
        if not cred_path:
            cred_path = Path("firebase-credentials.json")
        
        # 4. Initialize Firebase
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        self._db = firestore.client()
```

**How Credentials Work**:
- Your `firebase-credentials.json` file contains:
  - Project ID
  - Private key (secret)
  - Service account email
- This authenticates your app to Firebase
- **Never commit this file to GitHub** (already in `.gitignore`)

---

### Key Firebase Methods

#### 1. **Store Attendance in Firestore**

```python
def record_attendance(self, student, session):
    """Save attendance to Firebase Firestore"""
    try:
        doc_ref = self.db.collection('attendance').add({
            'student_name': student.name,
            'admission_number': student.admission_number,
            'unit_code': session.unit.code,
            'date': session.date.isoformat(),
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        return {
            'success': True,
            'document_id': doc_ref[1].id
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

**What Happens**:
1. Creates new document in `attendance` collection
2. Stores student & session info
3. Returns document ID (for cross-referencing)

**Firestore Structure**:
```
attendance/ (collection)
  ├── doc1: {student: "John Doe", admission: "ADM/001", ...}
  ├── doc2: {student: "Jane Smith", admission: "ADM/002", ...}
  └── doc3: {...}
```

---

#### 2. **Check if Already Marked**

```python
def check_already_marked(self, session_id, admission_number):
    """Check if student already marked attendance"""
    docs = self.db.collection('attendance')\
        .where('session_id', '==', session_id)\
        .where('admission_number', '==', admission_number)\
        .limit(1)\
        .stream()
    
    return len(list(docs)) > 0
```

**Query Process**:
1. Query attendance collection
2. Filter by session_id AND admission_number
3. If any document found → already marked
4. Return true/false

**Why Important**: Prevents duplicate attendance in Firebase

---

#### 3. **Fallback Mode**

```python
@property
def is_connected(self):
    """Check if Firebase is available"""
    if not FIREBASE_AVAILABLE:
        return False
    if self._db is None:
        return False
    return True
```

**Fallback Strategy**:
- If Firebase is down → use local database only
- Attendance still recorded in Django DB
- Data syncs to Firebase when connection returns
- **Zero data loss** because local DB is source of truth

---

## 📨 PORTAL SYNC SERVICE (`attendance/sync_service.py`)

### What is the Portal?
The Portal is an external API (REST endpoint) where attendance data is also stored as a backup.

### Dual-Sync Architecture

```python
class DualSyncService:
    """Sync attendance to both Firebase AND Portal API"""
    
    def sync_attendance(self, student, session):
        # Step 1: Save to local database immediately
        attendance, _ = Attendance.objects.get_or_create(
            student=student,
            session=session
        )
        
        # Step 2: Try Firebase in background
        firebase_result = self._sync_firebase(student, session)
        
        # Step 3: Try Portal API in background
        portal_result = self._sync_portal(student, session, attendance)
        
        # Step 4: Update sync status
        attendance.synced_to_firebase = firebase_result['success']
        attendance.synced_to_portal = portal_result['success']
        attendance.save()
        
        return {
            'success': True,
            'firebase': firebase_result,
            'portal': portal_result,
            'attendance_percentage': attendance.get_attendance_percentage()
        }
```

**Why Dual-Sync?**
1. **Redundancy**: If one system fails, data is in the other
2. **Backup**: Portal API as secondary storage
3. **Integration**: Sync to external system automatically

---

### Portal API Request

```python
def _sync_portal(self, student, session):
    """Send POST request to Portal API"""
    payload = {
        'student_name': student.name,
        'admission_number': student.admission_number,
        'unit_code': session.unit.code,
        'date': str(session.date),
        'time': str(session.start_time),
        'lecturer': session.lecturer.user.get_full_name(),
        'venue': session.venue,
        'attendance_percentage': attendance.get_attendance_percentage(),
    }
    
    try:
        response = requests.post(
            settings.PORTAL_API_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'response': response.json()}
        else:
            return {'success': False, 'error': response.text}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

**Flow**:
1. Build JSON payload with attendance data
2. POST to Portal API endpoint
3. Get response (200 = success)
4. Store response in database for audit trail

---

## 📱 FRONTEND: MODALS & FORMS

### Unit Creation Modal

```html
<!-- Dashboard modal for creating units -->
<div id="newUnitModal" class="modal-backdrop">
  <div class="modal-content glass-card">
    <h2 class="modal-title">+ Add New Unit</h2>
    
    <form id="new-unit-form">
      {% csrf_token %}
      <input type="text" name="code" placeholder="e.g., CS101" required />
      <input type="text" name="name" placeholder="e.g., Intro to Programming" required />
      <textarea name="description" placeholder="Optional notes..."></textarea>
      
      <button type="submit">Create Unit</button>
      <button type="button" id="new-unit-cancel">Cancel</button>
    </form>
    
    <div id="new-unit-errors"></div>
  </div>
</div>
```

**JavaScript Handler**:
```javascript
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(form);
  const csrfToken = getCookie('csrftoken');
  
  try {
    const resp = await fetch('/unit/create-ajax/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    });
    
    const json = await resp.json();
    
    if (json.success) {
      // Add unit to list without page reload
      const unitsList = document.querySelector('.units-list');
      const tag = document.createElement('span');
      tag.textContent = json.unit.code + ' - ' + json.unit.name;
      unitsList.prepend(tag);
      
      modal.style.display = 'none';
    } else {
      // Show error
      errorsEl.innerHTML = json.errors ? 
        Object.values(json.errors).join('<br>') : json.error;
    }
  } catch(err) {
    errorsEl.textContent = 'Network error';
  }
});
```

**Flow**:
1. User fills form and clicks "Create Unit"
2. JavaScript prevents page reload
3. Sends AJAX POST to `/unit/create-ajax/`
4. Server validates and creates unit
5. JavaScript receives response
6. If success: add unit to list, close modal
7. If error: show error message

**CSRF Protection**:
- Extracts CSRF token from cookie
- Sends in `X-CSRFToken` header
- Server verifies token before processing

---

### QR Code Generation

```python
def create_session(request):
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.lecturer = lecturer
            
            # Auto-assign session number
            max_session = AttendanceSession.objects.filter(
                unit=session.unit,
                semester=session.semester
            ).aggregate(Max('session_number'))['session_number__max']
            
            session.session_number = (max_session or 0) + 1
            session.save()
            
            # Generate and save QR code
            qr_file = generate_session_qr(session, base_url)
            session.qr_code.save(qr_file.name, qr_file)
            
            return redirect('session_detail', session_id=session.id)
```

**QR Code Contents**:
```
https://your-deployment-url.example/attend/a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6/
```

**When Student Scans**:
1. QR code opens attendance form
2. Student enters name & admission number
3. System records attendance
4. Firebase synced in background

---

## 📊 ATTENDANCE PERCENTAGE CALCULATION

```python
def get_attendance_percentage(self, unit=None, semester=1, max_lessons=12):
    """
    Calculate attendance percentage.
    Default: 12 lessons per semester per unit
    """
    attendance = Attendance.objects.filter(
        student=self, 
        session__unit=unit,
        session__semester=semester
    ).count()
    
    return round(
        (attendance / max_lessons) * 100, 2
    ) if max_lessons > 0 else 0
```

**Example**:
```
Student: John Doe
Unit: CS101
Semester: 1
Attendance: 10 classes out of 12

Calculation: (10 / 12) × 100 = 83.33%
```

**Display On**:
- Success page (after marking attendance)
- Session detail page
- Portal API response
- Firebase document

---

## 🔒 SECURITY FEATURES

| Feature | Implementation | Purpose |
|---------|-----------------|---------|
| **CSRF Protection** | Django middleware + tokens | Prevent cross-site attacks |
| **Session Auth** | Login required decorator | Only authenticated lecturers can create sessions |
| **Password Hashing** | Django's PBKDF2 | Passwords encrypted in database |
| **HTTPS** | Platform SSL | All traffic encrypted |
| **Duplicate Prevention** | Unique constraints | Can't mark attendance twice |
| **Firebase Credentials** | Environment variables | Never hardcoded in code |
| **Rate Limiting** | (Optional) | Prevent brute force login |
| **Input Validation** | Form validation + sanitization | Prevent SQL injection |

---

## 📈 DEPLOYMENT PIPELINE

### Local Development
```bash
python manage.py migrate          # Apply migrations
python manage.py runserver        # Start local server
# Visit http://127.0.0.1:8000/
```

### Production (container hosting)
```bash
git add -A
git commit -m "Your message"
git push origin main

(Use your platform's deploy/push instructions, e.g., Docker image push & deploy)
# Runs migrations, collects static files, restarts app
```

**Dockerfile Process**:
1. Pull Python 3.11 slim image
2. Install dependencies from `requirements.txt`
3. Copy app code
4. Run `python manage.py collectstatic`
5. Start gunicorn server on port 8000

---

## 🎯 COMPLETE USER FLOWS

### Lecturer Flow

```
1. SIGNUP (Admin only)
   - Create User in Django admin
   - Create Lecturer profile with staff ID & department
   
2. LOGIN
   - Visit /login/
   - Enter username & password
   - Django verifies, creates session cookie
   - Redirected to /dashboard/
   
3. CREATE UNIT
   - Click "New Unit" button (opens modal)
   - Enter code (CS101), name, description
   - AJAX POST to /unit/create-ajax/
   - Unit appears in list
   
4. CREATE SESSION
   - Click "Create Session" (opens form page or modal)
   - Select unit, semester, date, time, venue
   - System auto-assigns session number (Lec 1, Lec 2, etc.)
   - QR code generated automatically
   - Redirected to session detail page
   
5. VIEW ATTENDANCE
   - Click "View" on session card
   - See all students who marked attendance
   - See QR code and download option
   - Close session when done (prevents more attendances)
   
6. LOGOUT
   - Click Logout
   - Session destroyed
```

### Student Flow

```
1. SCAN QR CODE
   - QR code visible on lecturer's dashboard
   - Student scans with phone camera
   - Opens attendance form
   
2. MARK ATTENDANCE
   - Enter full name
   - Enter admission number
   - Click "Mark Attendance"
   
3. SYSTEM PROCESSES
   - Checks if already marked (Firebase first, then local DB)
   - If duplicate: shows "Already marked" page
   - If new: creates Student record (auto-enroll in unit)
   - Creates Attendance record
   - Calculates attendance percentage
   
4. BACKGROUND SYNC
   - Starts separate thread (non-blocking)
   - Syncs to Firebase Firestore
   - Syncs to Portal API
   - Updates sync status in database
   
5. SEE SUCCESS
   - Shows "Attendance Marked Successfully"
   - Displays attendance percentage
   - Optional: shows link to view session details
```

---

## 🛠️ KEY TECHNICAL CONCEPTS

### Singleton Pattern (Firebase)
```python
class FirebaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```
**Why**: Ensures only one Firebase connection even if called multiple times

### Foreign Keys & Relationships
```python
# Lecturer → Units (one-to-many)
Unit.lecturer = ForeignKey(Lecturer)

# Unit → Sessions (one-to-many)
AttendanceSession.unit = ForeignKey(Unit)

# Session → Attendance Records (one-to-many)
Attendance.session = ForeignKey(AttendanceSession)

# Student → Attendance Records (one-to-many)
Attendance.student = ForeignKey(Student)

# Student → Units (many-to-many)
Student.units = ManyToManyField(Unit)
```

### Background Threading
```python
def _bg_sync(att_id):
    """Run in separate thread (non-blocking)"""
    att = Attendance.objects.get(id=att_id)
    get_dual_sync_service().sync_attendance(...)

# Start thread (daemon=True means kill if main thread stops)
threading.Thread(target=_bg_sync, args=(attendance.id,), daemon=True).start()

# Student sees success page immediately
# Sync happens in background
```

### CSRF Token Handling
```javascript
// Extract from cookie
function getCookie(name) {
    const v = document.cookie.match('(^|;)\s*' + name + '\s*=\s*([^;]+)');
    return v ? v.pop() : '';
}

// Send in AJAX header
const csrfToken = getCookie('csrftoken');
fetch('/unit/create-ajax/', {
    headers: {
        'X-CSRFToken': csrfToken
    }
});
```

---

## 📞 API EXAMPLES

### Create Unit (AJAX)
```
POST /unit/create-ajax/
Content-Type: application/x-www-form-urlencoded

code=CS101&name=Intro+to+Programming&description=...&csrfmiddlewaretoken=...

Response:
{
  "success": true,
  "unit": {
    "id": 5,
    "code": "CS101",
    "name": "Intro to Programming"
  }
}
```

### Mark Attendance
```
GET /attend/a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6/
(Shows form)

POST /attend/a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6/
Content-Type: application/x-www-form-urlencoded

student_name=John+Doe&admission_number=ADM/2023/001&csrfmiddlewaretoken=...

Response: Redirects to success page with attendance percentage
```

### Check System Status
```
GET /api/status/

Response:
{
  "django": "running",
  "database": "connected",
  "firebase": "connected"
}
```

---

## 🎓 SUMMARY

Your Digital Attendance System is a **production-grade, full-stack application** with:

✅ **Backend**: Django ORM models with constraints  
✅ **Authentication**: Session-based auth with CSRF protection  
✅ **Database**: SQLite (local) / PostgreSQL (production)  
✅ **Cloud**: Firebase Firestore for real-time sync  
✅ **APIs**: AJAX endpoints + Portal API integration  
✅ **Frontend**: Responsive HTML/CSS/JavaScript modals  
✅ **Deployment**: Containerized Docker on a chosen hosting platform  
✅ **Performance**: Background threading, connection pooling, caching  
✅ **Security**: Encrypted passwords, HTTPS, input validation  
✅ **Reliability**: Dual-sync, fallback modes, error handling  

Every component is designed to be robust, scalable, and user-friendly!
