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

# (Moved collectstatic to release-time to avoid needing runtime secrets during image build)
# Release script: make executable if present (some build contexts may exclude it)
RUN if [ -f /app/release.sh ]; then chmod +x /app/release.sh; fi

# Expose port
EXPOSE 8080

# Run the release script (which runs migrations then starts Gunicorn)
CMD ["/app/release.sh"]
