#!/usr/bin/env bash
set -euo pipefail

# Small release script expected by Dockerfile / PaaS deploys.
# It runs migrations, collects static files, then execs Gunicorn bound to $PORT.

echo "Running release tasks..."

if [ -n "${DATABASE_URL:-}" ]; then
  echo "Migrating database..."
  python manage.py migrate --noinput
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

PORT=${PORT:-8080}
echo "Starting Gunicorn on 0.0.0.0:$PORT"
exec gunicorn attendance_system.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --log-level info
