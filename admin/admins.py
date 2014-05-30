from django.core.exceptions import ImproperlyConfigured

from admin.viewsets import ModelViewSet


class AdminSection:
    label = None
    viewset_class = None

    def __init__(self):
        self.viewset = self.viewset_class(**self.get_viewset_kwargs())

    def get_viewset_kwargs(self):
        return {}

    @property
    def urls(self):
        if self.viewset is None:
            raise ImproperlyConfigured('AdminSection has no viewset')

        return self.viewset.urls


class ModelAdminSection(AdminSection):
    label = None
    model = None
    viewset_class = ModelViewSet

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.model is None:
            raise ImproperlyConfigured('Model class is not set on ModelAdminSection')

    def get_viewset_kwargs(self):
        return {
            'model': self.model
        }

