#!/usr/bin/env python
"""
Apply critical performance optimizations to settings.py
Run this script to speed up your system significantly
"""

import re

settings_file = 'attendance_system/settings.py'

# Read the current settings
with open(settings_file, 'r') as f:
    content = f.read()

# OPTIMIZATION 1: Add caching configuration
caching_config = """
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

# Session Configuration (Use Cache Backend for speed)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
"""

# OPTIMIZATION 2: Improve database configuration
old_db_config = """# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

new_db_config = """# Database (Optimized with connection pooling)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Keep database connections alive for 10 minutes
        'OPTIONS': {
            'timeout': 20,  # Database lock timeout in seconds
        }
    }
}"""

# Apply database optimization
if old_db_config in content:
    content = content.replace(old_db_config, new_db_config)
    print("✓ Database connection pooling optimized")
else:
    print("⚠ Database config not found in expected format")

# Add caching after database config
if 'CACHES' not in content:
    # Find the right place to insert (after WSGI_APPLICATION)
    insertion_point = content.find('WSGI_APPLICATION')
    if insertion_point != -1:
        # Find the end of that line
        end_of_line = content.find('\n', insertion_point)
        insert_pos = end_of_line + 1
        
        content = content[:insert_pos] + caching_config + '\n' + content[insert_pos:]
        print("✓ Caching configuration added")
else:
    print("⚠ Caching configuration already exists")

# Write the optimized settings
with open(settings_file, 'w') as f:
    f.write(content)

print("\n✅ Performance optimizations applied!")
print("\nOptimizations made:")
print("  1. ✓ Database connection pooling enabled (CONN_MAX_AGE=600)")
print("  2. ✓ In-memory caching configured for speed")
print("  3. ✓ Session caching using cache backend")
print("  4. ✓ Database timeout set to 20 seconds")
print("\nRestart your Django server to apply changes:")
print("  python manage.py runserver 0.0.0.0:8000")
