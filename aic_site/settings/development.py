from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [

]
TESTING = True

INTERNAL_IPS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING['handlers'] = {
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
    },
    'logfile': {
        'level': 'INFO',
        'class': 'logging.NullHandler',
    },
}

INFRA_AUTH_TOKEN = 'test_token'
