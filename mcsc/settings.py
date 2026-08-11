"""
Django settings for mcsc project.
"""

import os
import sys
import copy
from pathlib import Path
from decouple import config
import dj_database_url
import django.template.context

# Python 3.14 compatibility patch for Django 4.2 BaseContext.__copy__
if sys.version_info >= (3, 14):
    def _safe_context_copy(self):
        new_obj = self.__class__.__new__(self.__class__)
        new_obj.__dict__.update(self.__dict__)
        new_obj.dicts = self.dicts.copy()
        return new_obj
    django.template.context.BaseContext.__copy__ = _safe_context_copy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-mcsc-production-key-fallback-2026-secure')
DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='*').split(',') if h.strip()]

RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

_csrf_trusted = config('CSRF_TRUSTED_ORIGINS', default='')
if _csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted.split(',') if o.strip()]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'social_django',
    'storages',
    'crispy_forms',
    
    # Custom MCSC apps
    'accounts',
    'core',
    'representatives',
    'news',
    'events',
    'grievances',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.ActiveUserCheckMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.MCSCSocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'mcsc.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'core.context_processors.portal_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'mcsc.wsgi.application'

# Database configuration: uses Supabase pooler (PgBouncer) via DATABASE_URL; fallback to SQLite
_database_url = config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
db_config = dj_database_url.parse(_database_url, conn_max_age=0)
if 'postgresql' in db_config.get('ENGINE', ''):
    db_config['DISABLE_SERVER_SIDE_CURSORS'] = True
    db_config['CONN_HEALTH_CHECKS'] = True
DATABASES = {
    'default': db_config
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Auth Backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Google OAuth2 settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_OAUTH2_KEY', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_OAUTH2_SECRET', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['mariancollege.org']

# Social Auth Pipeline
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    # Custom pipeline step for domain verification
    'accounts.pipeline.verify_marian_college_domain',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'accounts.pipeline.set_clean_user_name',
)

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Consistent with Indian Standard Time
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True

# Media files & Storage configuration
USE_SUPABASE_STORAGE = config('USE_SUPABASE_STORAGE', default=False, cast=bool)
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_KEY', default='')
SUPABASE_STORAGE_BUCKET_NAME = config('SUPABASE_STORAGE_BUCKET_NAME', default='')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SUPABASE_ACCESS_KEY_ID = config('SUPABASE_ACCESS_KEY_ID', default=config('AWS_ACCESS_KEY_ID', default=''))
SUPABASE_SECRET_ACCESS_KEY = config('SUPABASE_SECRET_ACCESS_KEY', default=config('AWS_SECRET_ACCESS_KEY', default=''))

if USE_SUPABASE_STORAGE and SUPABASE_URL and SUPABASE_ACCESS_KEY_ID and SUPABASE_SECRET_ACCESS_KEY and SUPABASE_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'core.storage.SupabaseS3Storage'
    AWS_ACCESS_KEY_ID = SUPABASE_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = SUPABASE_SECRET_ACCESS_KEY
    # Supabase uses S3 compatible interface via endpoint
    AWS_S3_ENDPOINT_URL = f"{SUPABASE_URL}/storage/v1/s3"
    AWS_STORAGE_BUCKET_NAME = SUPABASE_STORAGE_BUCKET_NAME
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='ap-northeast-2')
    AWS_S3_ADDRESSING_STYLE = 'path'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_QUERYSTRING_EXPIRE = config('AWS_QUERYSTRING_EXPIRE', default=604800, cast=int)
else:
    # Local fallback
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'  # Using standard HTML styles in templates

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=1025, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='MCSC Students Council <no-reply@mariancollege.org>')

# Resend Transactional Email
RESEND_API_KEY = config('RESEND_API_KEY', default='')
RESEND_FROM_EMAIL = config('RESEND_FROM_EMAIL', default='MCSC Students Council <onboarding@resend.dev>')

# Authentication Redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'grievance_portal'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# In-Memory Caching & Fast Cached-DB Sessions for instant login/logout
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mcsc-fast-cache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Security Hardening Settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Protected Admin Accounts that cannot be deleted (strictly loaded from .env)
_protected_admins_str = config('PROTECTED_ADMIN_USERNAMES', default='')
PROTECTED_ADMIN_USERNAMES = {u.strip() for u in _protected_admins_str.split(',') if u.strip()}

# External Portal Links (strictly loaded from .env)
PYQ_PORTAL_URL = config('PYQ_PORTAL_URL')

