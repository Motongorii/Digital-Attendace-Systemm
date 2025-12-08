#!/bin/bash
set -e

echo "[Release] Running Django migrations..."
python manage.py migrate --noinput
echo "[Release] Migrations complete. Starting Gunicorn..."

exec gunicorn attendance_system.wsgi:application --bind 0.0.0.0:8080 --workers 3
