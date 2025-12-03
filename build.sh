#!/bin/bash
# Vercel build script for Django

set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "WARNING: collectstatic failed (expected if no static files)"

echo "Running migrations..."
python manage.py migrate --noinput || echo "WARNING: Migrations failed or skipped (expected on Vercel first deploy)"

echo "Build completed!"
