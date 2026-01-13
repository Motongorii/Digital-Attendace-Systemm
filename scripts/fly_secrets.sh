#!/usr/bin/env bash
# Helper script to set Fly secrets for this Django app.
# Usage: ./scripts/fly_secrets.sh <app-name>

set -euo pipefail
APP_NAME=${1:-}
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <fly-app-name>"
  exit 1
fi

# Prompt for values if not provided via env
read -s -p "Django SECRET_KEY (leave blank to generate random): " DJANGO_SECRET_KEY
echo
if [ -z "$DJANGO_SECRET_KEY" ]; then
  DJANGO_SECRET_KEY=$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(50))
PY
)
fi

read -p "DEBUG (True/False) [False]: " DEBUG
DEBUG=${DEBUG:-False}

read -p "SITE_BASE_URL (e.g. https://<app>.fly.dev): " SITE_BASE_URL

# Firestore credentials: prefer base64 env or read file
if [ -f firebase-credentials.json ]; then
  FIREBASE_B64=$(base64 -w0 firebase-credentials.json)
else
  read -p "Path to firebase-credentials.json (or press Enter to skip): " FBPATH
  if [ -n "$FBPATH" ] && [ -f "$FBPATH" ]; then
    FIREBASE_B64=$(base64 -w0 "$FBPATH")
  else
    FIREBASE_B64=""
  fi
fi

# Set secrets with flyctl (non-echoing)
if [ -n "$FIREBASE_B64" ]; then
  flyctl secrets set --app "$APP_NAME" \
    DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
    DEBUG="$DEBUG" \
    SITE_BASE_URL="$SITE_BASE_URL" \
    FIREBASE_CREDENTIALS_JSON_BASE64="$FIREBASE_B64"
else
  flyctl secrets set --app "$APP_NAME" \
    DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
    DEBUG="$DEBUG" \
    SITE_BASE_URL="$SITE_BASE_URL"
fi

echo "Secrets set for app $APP_NAME"
