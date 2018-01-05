from .base import *

##################################################################

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'travisci',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

##################################################################

INSTALLED_APPS += [

]

DEBUG = False

ALLOWED_HOSTS = ['81.31.168.207', 'aichallenge.sharif.edu', 'aichallenge.sharif.ir']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'aic_db',
        'PORT': 5432,
    }
}
