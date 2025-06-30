"""
Django settings for collabtasker project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load .env file
load_dotenv()

# ==============================
# BASE DIRECTORY
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# SECRET KEYS & DEBUG
# ==============================

SECRET_KEY = 'django-insecure-bcsqc7sj_!i&*_i-e#q(7xhb9r=ugu3w&=l^)%jyj!)-s0016t'

DEBUG = True
if os.getenv('RENDER'):
    DEBUG = False

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

# ==============================
# REDIS CONFIGURATION (Channels, Cache, Celery)
# ==============================

def force_db0(url):
    if url is None:
        return None
    if '/' in url.rsplit(':', 1)[-1]:
        base, _ = url.rsplit('/', 1)
        return base + '/0'
    else:
        return url + '/0'

CHANNEL_REDIS_URL = force_db0(os.getenv('REDIS_CHANNEL_URL')) or 'redis://127.0.0.1:6379/0'
REDIS_CACHE_URL = force_db0(os.getenv('REDIS_CACHE_URL')) or 'redis://127.0.0.1:6379/1'
REDIS_CELERY_URL = force_db0(os.getenv('REDIS_CELERY_URL')) or 'redis://127.0.0.1:6379/2'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [CHANNEL_REDIS_URL],
            "prefix": "channels",
        }
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "KEY_PREFIX": "cache",
        },
    }
}

CELERY_BROKER_URL = REDIS_CELERY_URL
CELERY_RESULT_BACKEND = REDIS_CELERY_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "queue_key_prefix": "celery",
}

# ==============================
# APPLICATION DEFINITION
# ==============================

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

# ==============================
# DATABASE CONFIGURATION
# ==============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set in environment variables")

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# ==============================
# AUTHENTICATION
# ==============================

AUTH_USER_MODEL = 'accounts.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# ==============================
# PASSWORD VALIDATORS
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================
# INTERNATIONALIZATION
# ==============================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================
# STATIC FILES (CSS, JS, Images)
# ==============================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================
# EMAIL SETTINGS
# ==============================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'spmacavity@gmail.com'
EMAIL_HOST_PASSWORD = 'siicktfvtluefkqm'  # Consider using env var
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==============================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
