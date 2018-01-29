from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.87', '192.168.1.115']

INSTALLED_APPS += [

]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
