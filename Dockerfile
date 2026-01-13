# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .


# Expose port
EXPOSE 8080

# Run migrations, collectstatic, then start Gunicorn directly (Render pattern)
CMD bash -c 'python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && exec gunicorn attendance_system.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 2 --timeout 120'
