#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/backend"

export DB_HOST="${DB_HOST:-127.0.0.1}"
export DB_PORT="${DB_PORT:-5432}"
export DB_NAME="${DB_NAME:-limis}"
export DB_USER="${DB_USER:-limis}"
export DB_PASSWORD="${DB_PASSWORD:-limis123}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-limis.settings.dev}"

echo "[migrate-check] showmigrations (pending marked [ ])"
/opt/limis/venv/bin/python manage.py showmigrations

echo "[migrate-check] dry validation: migrate --plan"
/opt/limis/venv/bin/python manage.py migrate --plan

