#!/bin/sh
set -e

echo "Waiting for database (brief pause)"
sleep 2

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn attendance_system.wsgi:application --bind 0.0.0.0:8080 --workers 2
