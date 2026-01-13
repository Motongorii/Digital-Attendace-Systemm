#!/usr/bin/env bash
# Simple script to guide Fly app creation and attach a managed Postgres.
# Usage: ./scripts/fly_deploy.sh <app-name> <region>

set -euo pipefail
APP_NAME=${1:-digital-attendance}
REGION=${2:-iad}

echo "This script will:
 - run 'flyctl launch --name $APP_NAME --dockerfile Dockerfile --no-deploy --region $REGION'
 - optionally create & attach a managed Postgres
 - remind you to set secrets using scripts/fly_secrets.sh
"

read -p "Proceed with launch (y/N)? " PROCEED
if [[ "$PROCEED" != "y" && "$PROCEED" != "Y" ]]; then
  echo "Aborted by user."
  exit 0
fi

flyctl launch --name "$APP_NAME" --dockerfile Dockerfile --no-deploy --region "$REGION"

read -p "Create Fly-managed Postgres and attach it to $APP_NAME (y/N)? " CREATE_DB
if [[ "$CREATE_DB" == "y" || "$CREATE_DB" == "Y" ]]; then
  DB_NAME="$APP_NAME-db"
  fly postgres create --name "$DB_NAME" --region "$REGION"
  fly postgres attach "$DB_NAME" --app "$APP_NAME"
  echo "Postgres created and attached. Fly sets DATABASE_URL as a secret automatically."
fi

echo "Run: ./scripts/fly_secrets.sh $APP_NAME"
echo "Then run: flyctl deploy --app $APP_NAME"
