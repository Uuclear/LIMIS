from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()
]

_cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]

# Align with Docker volume mount (nginx serves STATIC_URL from /app/static)
STATIC_ROOT = BASE_DIR / 'static'

_use_https = os.environ.get('USE_HTTPS', 'false').lower() in ('1', 'true', 'yes')
SECURE_SSL_REDIRECT = _use_https
SECURE_HSTS_SECONDS = 31536000 if _use_https else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = _use_https
SECURE_HSTS_PRELOAD = _use_https
SESSION_COOKIE_SECURE = _use_https
CSRF_COOKIE_SECURE = _use_https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
