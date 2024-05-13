from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'biuri',
        'USER': 'postgres',
        'PASSWORD': 'manohacker',
        'HOST': ''
    }
}

INSTALLED_APPS += ('debug_toolbar',)

INTERNAL_IPS = ('127.0.0.1')
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
