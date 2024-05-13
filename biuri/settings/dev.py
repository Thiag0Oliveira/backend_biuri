from .base import *

ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'biuri',
        'USER': 'root',
        'PASSWORD': 'BnRLQGiWkBnRLQGiWk',
        'HOST': '198.74.62.126'
    # },
    # 'cepbr': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'cepbr',
    #     'USER': 'root',
    #     'PASSWORD': 'reduxredux',
    #     'HOST': ''
    }
}

INSTALLED_APPS += ('debug_toolbar',)

INTERNAL_IPS = ('127.0.0.1')
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

if DEBUG:
    MIDDLEWARE_CLASSES += ('django_stackoverflow_trace.DjangoStackoverTraceMiddleware', )
    DJANGO_STACKOVERFLOW_TRACE_SEARCH_SITE = "googlesearch"


# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions', ]

ACCOUNT_EMAIL_VERIFICATION = "none"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@biuri.com.br'
