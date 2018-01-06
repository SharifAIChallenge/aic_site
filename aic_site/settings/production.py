from .base import *

INSTALLED_APPS += [

]

DEBUG = False

ALLOWED_HOSTS = ['81.31.168.207', 'aichallenge.sharif.edu', 'aichallenge.sharif.ir', 'aichallenge.sharif.ac.ir']

print('AA')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'aic_db',
        'PORT': 5432,
    }
}

print('BB')
