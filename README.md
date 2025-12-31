# 📱 Digital Attendance System

A modern, futuristic Django-based attendance tracking system using QR codes and Firebase integration. Students scan QR codes to mark their attendance for class sessions.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange)

## ✨ Features

- **QR Code Generation**: Lecturers create sessions and generate unique QR codes
- **Mobile-Friendly**: Students scan QR codes to access attendance forms
- **Real-time Storage**: Attendance data saved to Firebase Firestore
- **Dual-Sync to Portal**: Automatically sync attendance to lecturer portal API + Firebase
- **Attendance Percentage**: Auto-calculated per student per unit (12 lessons/semester)
- **Automatic Student Registration**: Students auto-registered on first attendance
- **Futuristic UI**: Cyberpunk-inspired, responsive design
- **Session Management**: Open/close sessions, view attendance records
- **Duplicate Prevention**: Students can only mark attendance once per session

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Firebase project (for cloud storage)

### Installation

1. **Clone/Navigate to the project directory**
   ```bash
   cd "Digital Attendance System"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Firebase** (see Firebase Setup section below)

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Home: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Lecturer Login: http://127.0.0.1:8000/login/

## 🔥 Firebase Setup

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Enter a project name (e.g., "digital-attendance")
4. Disable Google Analytics (optional for this project)
5. Click "Create Project"

### Step 2: Enable Firestore Database

1. In your Firebase project, go to "Build" → "Firestore Database"
2. Click "Create Database"
3. Choose "Start in production mode" or "test mode"
4. Select a location close to your users
5. Click "Enable"

### Step 3: Generate Service Account Key

1. Go to Project Settings (gear icon) → "Service Accounts"
2. Click "Generate new private key"
3. Download the JSON file
4. **Rename it to `firebase-credentials.json`**
5. **Place it in the project root directory** (same level as manage.py)

### Step 4: Firestore Security Rules (Optional)

For production, update your Firestore rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to attendance records
    match /attendance_records/{document} {
      allow read, write: if true;
    }
    match /sessions/{sessionId}/{document=**} {
      allow read, write: if true;
    }
  }
}
```

## 👤 Setting Up a Lecturer Account

1. **Create a Django user** (via createsuperuser or admin panel)

2. **Access Django Admin**: http://127.0.0.1:8000/admin/

3. **Create a Lecturer profile**:
   - Go to "Attendance" → "Lecturers"
   - Click "Add Lecturer"
   - Select the user you created
   - Fill in Staff ID, Department, and Phone
   - Save

4. **Login as Lecturer**: http://127.0.0.1:8000/login/

## 📖 How It Works

### For Lecturers

1. **Login** to the lecturer portal
2. **Create Units** (courses) you're teaching
3. **Create Sessions** for each class:
   - Select a unit
   - Set date, time, and venue
   - A QR code is automatically generated
4. **Share QR Code** with students (display on screen or print)
5. **View Attendance** records in real-time
6. **Close Sessions** when class ends

### For Students

1. **Scan** the QR code displayed by the lecturer
2. **Fill in** your name and admission number
3. **Submit** to mark your attendance
4. Receive **confirmation** of successful attendance

## 📁 Project Structure

```
Digital Attendance System/
├── attendance/                 # Main Django app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── forms.py               # Django forms
│   ├── urls.py                # URL routing
│   ├── firebase_service.py    # Firebase integration
│   └── qr_generator.py        # QR code generation
├── attendance_system/          # Django project settings
│   ├── settings.py
│   └── urls.py
├── templates/                  # HTML templates
│   ├── base.html
│   └── attendance/
├── static/                     # Static files
├── media/                      # Uploaded files (QR codes)
├── firebase-credentials.json   # Firebase config (add this!)
├── requirements.txt
└── manage.py
```

## 🎨 UI Features

- **Cyberpunk/Futuristic Theme**: Dark background with cyan and magenta accents
- **Animated Background**: Moving grid lines and particles
- **Glass Morphism**: Translucent card effects
- **Responsive Design**: Works on mobile and desktop
- **Smooth Animations**: Loading states, success celebrations

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secure-secret-key
DEBUG=True
```

### Timezone

Default timezone is set to `Africa/Nairobi`. Change in `settings.py`:

```python
TIME_ZONE = 'Your/Timezone'
```

## 📱 Mobile Access

For students to scan QR codes from their phones:

1. **Local Network**: Use your computer's local IP
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   Access via: `http://YOUR_IP:8000/attend/SESSION_ID/`

2. **Production**: Deploy to a cloud hosting service (Heroku, etc.)

## 🛡️ Security Notes

- Never commit `firebase-credentials.json` to version control
- Use environment variables for secrets in production
- Set `DEBUG=False` in production
- Update `ALLOWED_HOSTS` in production

## 🐛 Troubleshooting

### "Firebase not connected"
- Ensure `firebase-credentials.json` is in the project root
- Check the file name is exactly `firebase-credentials.json`
- Verify the JSON file is valid

### "QR code not displaying"
- Run migrations: `python manage.py migrate`
- Check `media/` directory permissions

### "Lecturer profile not found"
- Create a Lecturer profile in Django admin for your user

## 🔗 Linking Firebase to Your Code

### 1. Place Your Service Account JSON
- Download your Firebase service account key (see above).
- Rename it to `firebase-credentials.json`.
- Place it in your project root (same folder as `manage.py`).

### 2. Set Up Environment Variable
- Create a `.env` file in your project root (or use `.env.example`):
  ```env
  DJANGO_SECRET_KEY=your-django-secret-key
  FIREBASE_CREDENTIALS_PATH=c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\firebase-credentials.json
  ```
- The code will automatically use this path to initialize Firebase.

### 3. Test Firebase Integration
- Run the server:
  ```powershell
  python manage.py migrate
  python manage.py runserver
  ```
- Open a Django shell:
  ```powershell
  python manage.py shell
  ```
- In the shell, test the connection:
  ```python
  from attendance.firebase_service import firebase_service
  print(firebase_service.is_connected)  # Should print True if connected
  ```
- If `True`, your code is now linked to Firebase!

### 4. Troubleshooting
- If not connected, check:
  - The JSON file path and name
  - That `firebase-admin` is installed (`pip install firebase-admin`)
  - That your `.env` is loaded (restart server after changes)

## 📄 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

Built with ❤️ using Django and Firebase


