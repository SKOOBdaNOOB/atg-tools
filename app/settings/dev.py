from .base import *
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DEV_DJANGO_SECRET_KEY', default='django-insecure-x=h&fz^cjry2!o7!fg*6n8wg@4&%&mt+yez=hnldzi%4+xb7x-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
# Using PostgreSQL in development
DATABASES = {
    'default': dj_database_url.parse(
        config('DEV_PGSQL_DB_URL')
    )
}

# Email backend (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Additional development settings
INTERNAL_IPS = ['127.0.0.1']  # For Django Debug Toolbar, if used

# Any other development-specific settings
