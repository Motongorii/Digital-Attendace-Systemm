# Firebase Setup and Python Environment - Quick Fix Guide

## Problem Summary
Your system has Python 3.11 installed, but package installation is being cancelled.

## Solution: Manual Installation Steps

### Step 1: Verify Virtual Environment
Open PowerShell and run:
```powershell
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"
.\venv\Scripts\python.exe --version
```
You should see: `Python 3.11.9`

### Step 2: Install Packages One-by-One (if automated fails)

Try installing each package individually with a pause between them:

```powershell
.\venv\Scripts\pip install Django==4.2
.\venv\Scripts\pip install firebase-admin
.\venv\Scripts\pip install qrcode[pil]
.\venv\Scripts\pip install Pillow
.\venv\Scripts\pip install python-dotenv
.\venv\Scripts\pip install gunicorn
```

### Step 3: Verify Installation

```powershell
.\venv\Scripts\python.exe -c "import firebase_admin, django, qrcode, dotenv; print('✓ All packages installed!')"
```

### Step 4: Run Django Migrations

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

### Step 5: Run Development Server

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

### Step 6: Test Firebase Connection

Open another PowerShell terminal and run:
```powershell
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"
.\venv\Scripts\python.exe manage.py shell
```

Then in the Django shell:
```python
from attendance.firebase_service import firebase_service
print(f"Firebase Connected: {firebase_service.is_connected}")
```

## If Installation Still Fails

Try using Python's built-in `ensurepip` to upgrade pip:
```powershell
.\venv\Scripts\python.exe -m ensurepip --upgrade
```

Or try installing with `--no-binary` flag:
```powershell
.\venv\Scripts\pip install --no-binary :all: firebase-admin
```

## What to do next:

1. Follow the steps above manually
2. Once all packages are installed, you can test the application
3. Contact system administrator if antivirus is blocking pip installations

## Files Ready:
- ✓ Firebase credentials: Ready to be placed at `c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main\firebase-credentials.json`
- ✓ Django settings configured
- ✓ Firebase service properly set up
- ✓ `.env` file created with correct paths
