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

echo "[smoke] python manage.py check"
/opt/limis/venv/bin/python manage.py check

echo "[smoke] critical api checks"
/opt/limis/venv/bin/python manage.py shell -c "
from rest_framework.test import APIClient
from apps.system.models import User
u = User.objects.filter(is_superuser=True).first() or User.objects.first()
c = APIClient()
c.force_authenticate(user=u)
urls = [
  '/api/v1/projects/',
  '/api/v1/projects/025/',
  '/api/v1/commissions/',
  '/api/v1/samples/samples/',
  '/api/v1/testing/tasks/',
  '/api/v1/reports/',
  '/api/v1/system/permissions/grouped/',
]
for url in urls:
    r = c.get(url)
    print(url, r.status_code)
    assert r.status_code == 200, f'{url} -> {r.status_code}'
print('smoke ok')
"

echo "[smoke] done"

