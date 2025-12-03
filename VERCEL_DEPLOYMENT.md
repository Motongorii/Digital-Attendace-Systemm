# Vercel Deployment Guide for Digital Attendance System

## Prerequisites
- GitHub account (to push your code)
- Vercel account (free at vercel.com)
- Firebase project (already created)
- PostgreSQL database (optional, can use Vercel's PostgreSQL)

## Step 1: Initialize Git Repository

```powershell
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Digital Attendance System"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `digital-attendance-system`
3. **DO NOT** initialize with README, .gitignore, or license
4. Copy the commands shown and run them in PowerShell:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/digital-attendance-system.git
git branch -M main
git push -u origin main
```

## Step 3: Update Environment Variables for Production

Create a `.env.production` file (add to .gitignore):

```env
DEBUG=False
DJANGO_SECRET_KEY=your-secure-random-secret-key-generate-one
ALLOWED_HOSTS=your-app-name.vercel.app
FIREBASE_CREDENTIALS_PATH=/tmp/firebase-credentials.json
FIREBASE_DATABASE_URL=

# PostgreSQL (if using Vercel Postgres)
POSTGRES_DATABASE=your_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host.postgres.vercel-storage.com
POSTGRES_PORT=5432
```

## Step 4: Deploy to Vercel

### Option A: Using Vercel CLI

```powershell
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project directory
cd "c:\Users\antom\Desktop\DIGITAL-ATTENDANCE-SYSTEM-main"
vercel
```

### Option B: Connect GitHub to Vercel (Recommended)

1. Go to https://vercel.com
2. Click "New Project"
3. Select "Import Git Repository"
4. Connect your GitHub account
5. Select the `digital-attendance-system` repository
6. Configure project settings:
   - Framework: Django
   - Environment Variables: Add all from `.env.production`
   - Build Command: (leave empty or use custom)
7. Click "Deploy"

## Step 5: Configure Environment Variables in Vercel

In Vercel Dashboard:
1. Go to your project settings
2. Click "Environment Variables"
3. Add all variables from `.env.production`:
   - DEBUG
   - DJANGO_SECRET_KEY
   - ALLOWED_HOSTS
   - FIREBASE_CREDENTIALS_PATH
   - FIREBASE_DATABASE_URL
   - POSTGRES_* (if using)

## Step 6: Add Firebase Credentials

### Option 1: Upload JSON as Environment Variable
1. Read your `firebase-credentials.json` content
2. Copy entire JSON as one long string
3. In Vercel, create env var `FIREBASE_CREDENTIALS_JSON`
4. Update settings.py to read from this

### Option 2: Use Firebase Admin SDK with Environment Variables
Create a new env var with your Firebase project details:
```
FIREBASE_PROJECT_ID=digital-attendance-syste-798b5
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@digital-attendance-syste-798b5.iam.gserviceaccount.com
```

## Step 7: Set Up Database

### Option A: Use Vercel PostgreSQL (Recommended)
1. In Vercel Dashboard, go to Storage
2. Click "Create Database" → PostgreSQL
3. Vercel will provide connection strings automatically
4. Set POSTGRES_* env vars

### Option B: Use External PostgreSQL (e.g., AWS RDS, Google Cloud SQL)

## Step 8: Run Migrations on Vercel

After first deployment:

```powershell
vercel env pull  # Pull env vars locally
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

## Step 9: Test Live URL

Your app will be live at:
```
https://your-project-name.vercel.app/
```

Access:
- Home: https://your-project-name.vercel.app/
- Admin: https://your-project-name.vercel.app/admin/
- Login: https://your-project-name.vercel.app/login/

## Step 10: Enable Custom Domain (Optional)

1. In Vercel Dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

## Troubleshooting

### Issue: "Serverless Function Timeout"
- Reduce image processing
- Use CDN for static files
- Optimize database queries

### Issue: "Firebase Connection Failed"
- Verify FIREBASE_CREDENTIALS_PATH env var
- Ensure Firebase service account JSON is properly set
- Check Firebase security rules allow your service account

### Issue: "Database Connection Error"
- Verify POSTGRES_* env vars are correct
- Check database credentials
- Ensure whitelist includes Vercel IPs

### Issue: "Static Files Not Loading"
- Run: `python manage.py collectstatic --noinput`
- Check STATIC_ROOT and STATIC_URL settings
- Verify files exist in staticfiles/ directory

## Continuous Deployment

Every push to main branch will automatically deploy:
```powershell
git push origin main
```

## Monitor Logs

```powershell
vercel logs
```

## Rollback to Previous Deployment

In Vercel Dashboard → Deployments → Click on previous deployment

---

**Next Steps:**
1. Install Git if not already: https://git-scm.com/download/win
2. Run Step 1-2 to initialize Git
3. Create GitHub account and repository
4. Deploy to Vercel
5. Test the live URL!

