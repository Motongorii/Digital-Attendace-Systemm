"""
Performance optimization script for Django.
Adds caching, query optimization, and middleware improvements.
"""

# Add this to your settings.py

# 1. DATABASE QUERY OPTIMIZATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Keep database connections alive for 10 minutes
        'OPTIONS': {
            'timeout': 20,  # Database lock timeout in seconds
        }
    }
}

# 2. CACHING CONFIGURATION (In-Memory Cache for Speed)
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

# 3. SESSION CONFIGURATION
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 4. QUERY OPTIMIZATION
# Reduce database queries by selecting related data
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 5. STATIC FILES OPTIMIZATION
if not DEBUG:
    STATIC_URL = '/static/'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 6. LOGGING CONFIGURATION (Reduce logging overhead in production)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Only show warnings and errors
        },
    },
} if DEBUG else {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
}

# 7. TEMPLATE OPTIMIZATION
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
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ] if not DEBUG else None,
        },
    },
]

# 8. SECURITY MIDDLEWARE FOR PERFORMANCE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 9. FORM OPTIMIZATION
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# 10. EMAIL BACKEND (Use console in dev, SMTP in production)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
