import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import ssl

# Load .env variables (locally or if .env file exists)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY & DEBUG
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [
    'collabtasker.onrender.com',
    'localhost',
    '127.0.0.1',
    'web-production-755f5.up.railway.app',
    '.railway.app',
]

CSRF_TRUSTED_ORIGINS = [
    'https://collabtasker.onrender.com',
    'https://web-production-755f5.up.railway.app',
]

# DATABASE
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise Exception("DATABASE_URL env var is missing")

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
}

# Redis URLs for Channels, Cache, Celery
CHANNEL_REDIS_URL = os.getenv('REDIS_CHANNEL_URL', 'redis://127.0.0.1:6379/0')
REDIS_CACHE_URL = os.getenv('REDIS_CACHE_URL', 'redis://127.0.0.1:6379/1')
REDIS_CELERY_URL = os.getenv('REDIS_CELERY_URL', 'redis://127.0.0.1:6379/2')

# SSL config for Redis URLs (Upstash requires rediss:// with ssl)
def redis_ssl_config(redis_url: str):
    return redis_url.startswith('rediss://')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [{
                "address": CHANNEL_REDIS_URL,
                "ssl": redis_ssl_config(CHANNEL_REDIS_URL),
                "ssl_cert_reqs": ssl.CERT_NONE,
            }],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "ssl": redis_ssl_config(REDIS_CACHE_URL),
                "ssl_cert_reqs": ssl.CERT_NONE,
            },
        },
    }
}

CELERY_BROKER_URL = REDIS_CELERY_URL
CELERY_RESULT_BACKEND = REDIS_CELERY_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'django_celery_beat',

    'accounts',
    'projects',
    'chat',
    'notifications',
    'logs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'collabtasker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'collabtasker.asgi.application'

# Authentication and REST Framework
AUTH_USER_MODEL = 'accounts.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
