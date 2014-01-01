from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from .views import registered_views


class URLConfAppConfig(AppConfig):
    name = 'reek.urlconf'

    def ready(self):
        # Walk over all views-modules to discover views
        autodiscover_modules('views')
