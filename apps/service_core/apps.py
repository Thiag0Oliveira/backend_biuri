from django.apps import AppConfig


class ServiceCoreConfig(AppConfig):
    name = 'apps.service_core'

    def ready(self):
        from . import signals