# 🚀 DEPLOY TO VERCEL - COMPLETE GUIDE

Your Digital Attendance System can now run live on Vercel (free tier available)!

## **Quick Summary**
- ✅ Django app ready for production
- ✅ Firebase integration working
- ✅ Vercel configuration created
- ✅ Build scripts ready

## **What You Need:**
1. **GitHub Account** (free at github.com)
2. **Vercel Account** (free at vercel.com)
3. **Your Firebase Credentials** (you already have this)

---

## **DEPLOYMENT STEPS (Copy-Paste)**

### **Step 1: Install Git** (if not already installed)
Download from: https://git-scm.com/download/win

### **Step 2: Initialize Git Repository**
Open PowerShell in your project folder and run:

```powershell
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
git add .
git commit -m "Initial commit: Digital Attendance System"
```

### **Step 3: Create GitHub Repository**

1. Go to https://github.com/new
2. Create repository named: `digital-attendance-system`
3. **UNCHECK** "Initialize with README"
4. Click "Create Repository"
5. Copy the commands from GitHub and run in PowerShell:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/digital-attendance-system.git
git branch -M main
git push -u origin main
```

(Replace YOUR-USERNAME with your actual GitHub username)

### **Step 4: Push Your Code**

```powershell
git push origin main
```

### **Step 5: Deploy to Vercel**

**Option A: Using Vercel Website (Easiest)**

1. Go to https://vercel.com/new
2. Click "Continue with GitHub"
3. Authorize Vercel
4. Select your `digital-attendance-system` repo
5. Click "Import"
6. Configure:
   - **Framework**: Django
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: Keep empty
   - **Output Directory**: Keep empty
7. Add **Environment Variables**:
   ```
   DEBUG = False
   DJANGO_SECRET_KEY = (generate a random key)
   ALLOWED_HOSTS = .vercel.app
   FIREBASE_CREDENTIALS_PATH = /tmp/firebase-credentials.json
   ```
8. Click "Deploy"

**Option B: Using Vercel CLI**

```powershell
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"
vercel
```

### **Step 6: Add Firebase Credentials to Vercel**

After deployment:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add new environment variable:
   - **Name**: `FIREBASE_CREDENTIALS_JSON`
   - **Value**: Paste the entire content of your `firebase-credentials.json` file (the whole JSON)
3. Redeploy

### **Step 7: Generate Django Secret Key**

Generate a strong secret key:

```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and add to Vercel Environment Variables as `DJANGO_SECRET_KEY`

### **Step 8: Test Your Live App**

Your app will be live at:
```
https://digital-attendance-system.vercel.app/
```

Or your custom domain if configured.

Access:
- **Home**: https://your-app.vercel.app/
- **Admin**: https://your-app.vercel.app/admin/
- **Login**: https://your-app.vercel.app/login/
- **Create Session**: https://your-app.vercel.app/dashboard/

---

## **AFTER DEPLOYMENT**

### **Create Admin User on Live Site**

You need to create the admin user on the live database:

```powershell
vercel env pull
.\venv\Scripts\python.exe manage.py createsuperuser
```

### **QR Code Scanning on Live Site**

When you create a new session, the QR code will contain your Vercel URL:
```
https://your-app.vercel.app/attend/{session-id}/
```

Students can scan this from anywhere in the world!

---

## **UPDATE YOUR APP**

After making changes locally:

```powershell
git add .
git commit -m "Update: [description of changes]"
git push origin main
```

Vercel will automatically redeploy!

---

## **DATABASE**

Vercel supports:
- **SQLite** (works for small projects)
- **PostgreSQL** (recommended for production)
- **MongoDB** (optional)

For production, I recommend connecting a PostgreSQL database to Vercel Storage.

---

## **TROUBLESHOOTING**

### ❌ "Firebase Connection Failed"
- Ensure `FIREBASE_CREDENTIALS_JSON` env var is set correctly
- Verify the JSON is valid (paste entire file content)

### ❌ "Static Files Not Loading"
- Run: `vercel logs` to check build logs
- Ensure `collectstatic` ran successfully

### ❌ "502 Bad Gateway"
- Check Vercel logs: `vercel logs`
- Verify environment variables are set
- Check settings.py DEBUG and ALLOWED_HOSTS

### ❌ "Admin Page Redirects to Login"
- Create superuser first (see "After Deployment" section)
- Or use Vercel CLI to run management commands

---

## **COSTS**

- **Vercel**: Free tier includes 100GB bandwidth, serverless functions, etc.
- **Firebase**: Free tier includes 1GB storage, reads/writes
- **Domain**: Optional ($12-15/year if you buy a custom domain)

---

## **NEXT STEPS**

1. ✅ Install Git
2. ✅ Create GitHub account & repo
3. ✅ Deploy to Vercel
4. ✅ Test live URL
5. ✅ Create admin user on live site
6. ✅ Share link with lecturers and students!

---

**Your app will be live and accessible from anywhere! 🎉**

Need help? Check Vercel docs: https://vercel.com/docs
