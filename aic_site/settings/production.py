from .base import *

INSTALLED_APPS += [

]

DEBUG = False

ALLOWED_HOSTS = ['81.31.168.207', 'aichallenge.sharif.edu', 'aichallenge.sharif.ir', 'aichallenge.sharif.ac.ir']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.com'
EMAIL_HOST_USER = 'info@aichallenge.ir'
EMAIL_HOST_PASSWORD = 'xxxxxx'
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

