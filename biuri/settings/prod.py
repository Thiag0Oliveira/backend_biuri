import logging

import raven

from .base import *


STATIC_ROOT = '/var/django/www/static'
MEDIA_ROOT = '/var/django/www/media'
DEBUG = False

ADMINS = (
    ('3Y', 'contato@3ysoftwarehouse.com.br'),
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@biuri.com.br'

MANAGERS = ADMINS

ALLOWED_HOSTS = ['www.biuri.com.br', '167.71.103.27', 'biuri.com.br', '127.0.0.1']

SESSION_COOKIE_AGE = 28800

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'biuri',
        'USER': 'postgres',
        'PASSWORD': 'askbasd098123nasd',
        'HOST': ''
    }
}

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
#SECURE_HSTS_SECONDS = 60
#SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
#SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#    'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
#SECURE_BROWSER_XSS_FILTER = True
#SESSION_COOKIE_SECURE = True
#SESSION_COOKIE_HTTPONLY = True
#SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
#CSRF_COOKIE_SECURE = True
#CSRF_COOKIE_HTTPONLY = True
#X_FRAME_OPTIONS = 'DENY'

INTERNAL_IPS = ('127.0.0.1')

INSTALLED_APPS += ['gunicorn']

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
#TEMPLATES[0]['OPTIONS']['loaders'] = [
#    ('django.template.loaders.cached.Loader', [
#        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
#]

INSTALLED_APPS += ('raven.contrib.django.raven_compat', )
SENTRY_DSN = 'https://fe6bfa890aa246beb30f0b0288f9c593:10440f2be12a4984a39a261c408b341f@o177229.ingest.sentry.io/1262485'
SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
    },
}
SENTRY_CELERY_LOGLEVEL = logging.INFO
RAVEN_CONFIG = {
    'CELERY_LOGLEVEL': logging.INFO,
    'DSN': SENTRY_DSN
}
