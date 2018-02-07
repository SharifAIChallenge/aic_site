"""
Django settings for AIC18_Site project.
"""

import os
import sys

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = 'r=2mdcuth+5g8o6)s*z7c61bss)%0ku2b9w72d3ph^x&)^gx$t'

TESTING = sys.argv[1:2] == ['test']

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',

    'mptt',
    'tagging',
    'zinnia',
    'zinnia_tinymce',
    'sorl.thumbnail',
    'tinymce',
    'captcha',

    'apps.intro',
    'apps.accounts',
    'apps.billing',
    'apps.game',
    'apps.modir',
    'apps.utils'
]

INSTALLED_APPS += (
    'threadedcomments',
    'django_comments',
    'django.contrib.sites',
)

# comments
COMMENTS_APP = 'threadedcomments'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'aic_site.force_default_language_middleware.force_default_language_middleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aic_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'aic_site.context_processors.menu'
            ],
        },
    },
]

WSGI_APPLICATION = 'aic_site.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGES = (
    ('en', _('English')),
    ('fa', _('Persian'))
)
LANGUAGE_CODE = 'fa'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    # '/var/www/static/',
    os.path.join(BASE_DIR, "static/files/"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static/root/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'locale_extra'),
    os.path.join(BASE_DIR, 'apps', 'accounts', 'locale'),
    os.path.join(BASE_DIR, 'apps', 'accounts', 'templates', 'email', 'locale')
)

NOCAPTCHA = True

LOGGING = {
    'version': 1,
    # 'disable_existing_loggers': True,
    # 'formatters': {
    #     'standard': {
    #         'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    #         'datefmt': "%d/%b/%Y %H:%M:%S"
    #     },
    # },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "/var/log/aic_site/aic_web.log",
            'maxBytes': 50000,
            'backupCount': 2,
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'propagate': True,
            'level': 'INFO',
        },
        '': {
            'handlers': ['logfile'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
