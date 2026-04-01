from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

# 使用SQLite作为开发数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 与 docker-compose 中 static_data:/app/static 一致，便于容器内 collectstatic
STATIC_ROOT = BASE_DIR / 'static'
