from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

DATABASES['default']['HOST'] = os.environ.get('DB_HOST', 'localhost')

# 与 docker-compose 中 static_data:/app/static 一致，便于容器内 collectstatic
STATIC_ROOT = BASE_DIR / 'static'
