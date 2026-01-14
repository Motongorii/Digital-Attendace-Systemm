# 🚀✨ Digital Attendance System ✨🚀

![Render](https://img.shields.io/badge/Hosted%20on-Render-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-4.2-green?style=for-the-badge)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

---

🎉 **This is my first complete project! Successfully hosted on [Render](https://render.com/)!** 🎉

---

## ✨ Features

- 🌌 **Cyberpunk/Futuristic Theme**: Dark background with cyan and magenta accents
- ✨ **Animated Background**: Moving grid lines and particles
- 🧊 **Glass Morphism**: Translucent card effects
- 📱 **Responsive Design**: Works on mobile and desktop
- 🕺 **Smooth Animations**: Loading states, success celebrations
- 🔒 **Real-time Storage**: Attendance data saved to Firebase Firestore
- 🔗 **Dual-Sync to Portal**: Automatically sync attendance to lecturer portal API + Firebase
- 📊 **Attendance Percentage**: Auto-calculated per student per unit (12 lessons/semester)
- 📝 **Automatic Student Registration**: Students auto-registered on first attendance
- 🧑‍🏫 **Session Management**: Open/close sessions, view attendance records
- 🚫 **Duplicate Prevention**: Students can only mark attendance once per session

---

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
   venv\Scripts\activate
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

---

## 🔥 Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a project and enable Firestore Database
3. Generate a Service Account Key and rename it to `firebase-credentials.json`
4. Place it in the project root directory (same level as manage.py)

---

## 👤 Test Lecturers for Demo

You can use these test lecturer accounts for testing:

| Name         | Staff ID | Department   | Phone        | Username   | Password   |
|--------------|----------|--------------|--------------|------------|------------|
| TestLecturer1| TL001    | Computer Sci | 0712345678   | lecturer1  | testpass1  |
| TestLecturer2| TL002    | IT           | 0798765432   | lecturer2  | testpass2  |

> _Login at:_ [Lecturer Portal](http://127.0.0.1:8000/login/)

---

## 📖 How It Works

### For Lecturers
1. Login to the lecturer portal
2. Create Units (courses) you're teaching
3. Create Sessions for each class (QR code auto-generated)
4. Share QR Code with students
5. View Attendance records in real-time
6. Close Sessions when class ends

### For Students
1. Scan the QR code displayed by the lecturer
2. Fill in your name and admission number
3. Submit to mark your attendance
4. Receive confirmation of successful attendance

---

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

---

## 🛡️ Security Notes
- Never commit `firebase-credentials.json` to version control
- Use environment variables for secrets in production
- Set `DEBUG=False` in production
- Update `ALLOWED_HOSTS` in production

---

## 🐛 Troubleshooting
- Ensure `firebase-credentials.json` is in the project root
- Check the file name is exactly `firebase-credentials.json`
- Verify the JSON file is valid
- Run migrations: `python manage.py migrate`
- Check `media/` directory permissions
- Create a Lecturer profile in Django admin for your user

---

## 🏁 Project Completion

> _This project is now fully complete and hosted on Render!_
>
> **Thank you for checking out my work!**
>
> ![Celebration](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

---

## 📄 License
MIT License - feel free to use and modify!

## 🤝 Contributing
Contributions are welcome! Please feel free to submit issues and pull requests.

---

Built with ❤️ using Django and Firebase


