#!/bin/sh
#!/bin/sh
set -e
set -x

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn
PORT=${PORT:-8080}
echo "Starting Gunicorn on port $PORT"
# Use a single worker to fit smaller instance memory (adjust if you scale the machine size)
exec gunicorn attendance_system.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
