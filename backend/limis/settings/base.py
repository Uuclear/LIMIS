import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'django_filters',
    'corsheaders',
    'django_extensions',
    # Local apps
    'apps.system',
    'apps.projects',
    'apps.commissions',
    'apps.samples',
    'apps.testing',
    'apps.reports',
    'apps.equipment',
    'apps.staff',
    'apps.environment',
    'apps.standards',
    'apps.quality',
    'apps.consumables',
    'apps.statistics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.IdempotencyMiddleware',
    'core.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'limis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'limis.wsgi.application'

AUTH_USER_MODEL = 'system.User'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'limis'),
        'USER': os.environ.get('DB_USER', 'limis'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 已登录用户自助修改密码接口限流（DRF UserRateThrottle scope，如 "5/hour"）
PASSWORD_CHANGE_THROTTLE_RATE = os.environ.get(
    'PASSWORD_CHANGE_THROTTLE_RATE', '5/hour',
)

# 登录失败限次（按 username + 客户端 IP，缓存计数；成功登录清零）
# LOGIN_FAILURE_MAX_ATTEMPTS=0 表示关闭该功能
LOGIN_FAILURE_MAX_ATTEMPTS = int(os.environ.get('LOGIN_FAILURE_MAX_ATTEMPTS', '5'))
LOGIN_FAILURE_LOCKOUT_SECONDS = int(os.environ.get('LOGIN_FAILURE_LOCKOUT_SECONDS', '300'))
LOGIN_FAILURE_WINDOW_SECONDS = int(os.environ.get('LOGIN_FAILURE_WINDOW_SECONDS', '900'))

# Cache
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

# 已登录用户权限列表短时缓存（秒）；与 JWT session_version 组合键，踢下线会自然失效
USER_PERMISSIONS_CACHE_SECONDS = int(os.environ.get('USER_PERMISSIONS_CACHE_SECONDS', '120'))

# 报告 PDF 二维码中的防伪查询链接前缀（需与前端路由 /verify/report/<id> 一致；生产请改为 HTTPS 公网地址）
REPORT_VERIFICATION_URL = os.environ.get(
    'REPORT_VERIFICATION_URL',
    'http://127.0.0.1:3000/verify/report/',
)

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.system.authentication.SessionVersionJWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_RATES': {
        'password_change': PASSWORD_CHANGE_THROTTLE_RATE,
    },
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_TOKEN_CLASSES': ('apps.system.tokens.SessionVersionAccessToken',),
    'TOKEN_REFRESH_SERIALIZER': 'apps.system.jwt_serializers.SessionVersionTokenRefreshSerializer',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'LIMIS API',
    'VERSION': 'v1',
    'SERVE_INCLUDE_SCHEMA': False,
}

# MinIO
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', '')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', '')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'limis')
