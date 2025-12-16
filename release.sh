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

# Convenience: allow creating/updating a superuser from environment variables
# Set CREATE_SUPERUSER_USERNAME and CREATE_SUPERUSER_PASSWORD (and optional CREATE_SUPERUSER_EMAIL)
# in Render dashboard as temporary env vars to create an admin without shell access.
if [ -n "${CREATE_SUPERUSER_USERNAME:-}" ]; then
  if [ -z "${CREATE_SUPERUSER_PASSWORD:-}" ]; then
    echo "CREATE_SUPERUSER_USERNAME is set but CREATE_SUPERUSER_PASSWORD is empty — skipping superuser creation"
  else
    echo "Creating/updating superuser '${CREATE_SUPERUSER_USERNAME}' from env..."
    python manage.py ensure_superuser --username "${CREATE_SUPERUSER_USERNAME}" --password "${CREATE_SUPERUSER_PASSWORD}" --email "${CREATE_SUPERUSER_EMAIL:-admin@example.com}"
    echo "Superuser '${CREATE_SUPERUSER_USERNAME}' created/updated. Please remove CREATE_SUPERUSER_* env vars from your Render settings after use."
  fi
fi

PORT=${PORT:-8080}
echo "Starting Gunicorn on 0.0.0.0:$PORT"
exec gunicorn attendance_system.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --log-level info
