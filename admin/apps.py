from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class AdminAppConfig(AppConfig):
    name = 'admin'

    def ready(self):
        # Walk over all views-modules to discover admins
        autodiscover_modules('admin')
