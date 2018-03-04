from .base import *
from .production_secret import *

INSTALLED_APPS += [

]

DEBUG = False

ALLOWED_HOSTS = ['81.31.168.207', 'aichallenge.sharif.edu', 'aichallenge.sharif.ir', 'aichallenge.sharif.ac.ir']
# CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.com'
EMAIL_HOST_USER = 'info@aichallenge.ir'
DEFAULT_FROM_EMAIL = 'info@aichallenge.ir'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'aic_db',
        'PORT': 5432,
    }
}

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
