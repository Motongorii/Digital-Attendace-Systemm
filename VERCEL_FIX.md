"""
VERCEL DEPLOYMENT FIX

The white screen/500 error is likely caused by:
1. Firebase credentials not being loaded on Vercel
2. STATICFILES_DIRS pointing to non-existent directories
3. Unicode print statements causing encoding errors

QUICK FIX - Follow these steps:
"""

# STEP 1: Update your Django settings.py

# Change this:
# STATICFILES_DIRS = [BASE_DIR / 'static']

# To this:
# STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# STEP 2: Update firebase_service.py

# Replace the bottom of the file:
# OLD:
# firebase_service = FirebaseService()

# NEW:
# firebase_service = None  # Initialize on first use instead of at import time

# Then in views.py, before using firebase_service:
# if firebase_service is None:
#     from attendance.firebase_service import FirebaseService
#     firebase_service = FirebaseService()

# STEP 3: Set Vercel Environment Variables

# In Vercel Dashboard → Settings → Environment Variables, add:
# DEBUG: False
# DJANGO_SECRET_KEY: (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# ALLOWED_HOSTS: .vercel.app
# FIREBASE_CREDENTIALS_JSON: (paste entire firebase-credentials.json content)

# STEP 4: Update settings.py to read Firebase from env var

# Add this to settings.py:
"""
import json
import base64

# Firebase from environment variable
FIREBASE_CREDS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON')
if FIREBASE_CREDS_JSON:
    # If env var is base64 encoded
    try:
        FIREBASE_CREDS_JSON = base64.b64decode(FIREBASE_CREDS_JSON).decode('utf-8')
    except:
        pass
    
    # Write to temp file for firebase_admin to use
    with open('/tmp/firebase-credentials.json', 'w') as f:
        f.write(FIREBASE_CREDS_JSON)
    FIREBASE_CREDENTIALS_PATH = '/tmp/firebase-credentials.json'
else:
    FIREBASE_CREDENTIALS_PATH = BASE_DIR / 'firebase-credentials.json'
"""

# STEP 5: Commit and redeploy

# git add .
# git commit -m "Fix Vercel deployment issues"
# git push origin main

print("""
If you still get a white screen after these fixes:

1. Check Vercel logs: vercel logs --tail
2. Look for Python errors or traceback
3. Share the error here for targeted fix

Common issues:
- Missing DJANGO_SECRET_KEY env var
- ALLOWED_HOSTS not set correctly
- Firebase credentials not found
- Static files directory doesn't exist
""")
