from .base import *

INSTALLED_APPS += [

]

DEBUG = False
ALLOWED_HOSTS = []

# some security settings:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': ''
    }
}

