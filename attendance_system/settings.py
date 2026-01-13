"""
Django settings for Digital Attendance System.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Database URL helper for production databases
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
import os
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF and security settings for production (platform hosting)
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
# Don't force secure cookies unless explicitly enabled via env var.
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
# Trust proxy header from your hosting platform (or other proxies) to detect HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'attendance.auth_debug.AuthDebugMiddleware',  # Must be after AuthenticationMiddleware so request.user is populated
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'attendance_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'attendance_system.wsgi.application'

# Caching Configuration (In-Memory Cache for Speed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'attendance-cache',
        'TIMEOUT': 300,  # Cache for 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Session Configuration
# Default to database-backed sessions in production so sessions persist
# across processes/instances (LocMemCache is per-process and will drop
# sessions when the process changes or is restarted — this can cause users to
# appear logged out immediately after logging in on some hosted environments).
if DEBUG:
    # For local development we keep the faster cache-backed sessions.
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # In production use DB-backed sessions unless overridden by env var.
    SESSION_ENGINE = os.getenv('SESSION_ENGINE', 'django.contrib.sessions.backends.db')

# Session expiry and cookie settings
# Increase session age to 30 days (2592000 seconds) so sessions don't expire during lecturer operations
SESSION_COOKIE_AGE = 2592000  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session open until explicitly logged out
SESSION_SAVE_EVERY_REQUEST = True  # Update session expiry on every request


# Database: prefer `DATABASE_URL` (Render/Postgres), fallback to local SQLite
import os

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Authentication
LOGIN_URL = 'login'  # Redirect to /login/ when @login_required fails, not /accounts/login/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
if os.path.exists(BASE_DIR / 'static'):
    STATICFILES_DIRS = [BASE_DIR / 'static']
else:
    STATICFILES_DIRS = []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Firebase Configuration
# Path to Firebase service account JSON. Prefer setting via env var for production.
_env_firebase_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
FIREBASE_CREDENTIALS_PATH = Path(_env_firebase_path) if _env_firebase_path else BASE_DIR / 'firebase-credentials.json'

# Support providing the entire service account JSON via env var:
# - FIREBASE_CREDENTIALS_JSON: raw JSON string
# - FIREBASE_CREDENTIALS_JSON_BASE64: base64-encoded JSON string
firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
if not firebase_json:
    firebase_b64 = os.getenv('FIREBASE_CREDENTIALS_JSON_BASE64')
    if firebase_b64:
        try:
            import base64
            firebase_json = base64.b64decode(firebase_b64).decode('utf-8')
        except Exception:
            firebase_json = None

if firebase_json:
    try:
        import json
        # Validate JSON before writing
        json.loads(firebase_json)
        # Write to file only if new or different to avoid unnecessary writes
        if not FIREBASE_CREDENTIALS_PATH.exists() or FIREBASE_CREDENTIALS_PATH.read_text() != firebase_json:
            FIREBASE_CREDENTIALS_PATH.write_text(firebase_json)
    except Exception:
        # Invalid JSON: do not overwrite existing file
        pass

# Optional: Firebase Realtime Database URL (only for RTDB). Leave blank for Firestore.
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL', '')

# Base URL for the site when running scripts or management commands outside a request
# Set via env var `SITE_BASE_URL` in production, otherwise default to localhost.
SITE_BASE_URL = os.getenv('SITE_BASE_URL', 'http://127.0.0.1:8000')

