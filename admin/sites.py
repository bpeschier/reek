from functools import reduce

from django.conf.urls import url, include

from .views import IndexView
from .registry import RegistryMixin


class AdminSite(RegistryMixin):
    template_admin_base = 'admin/base.html'
    namespace = 'admin'

    name = 'Django administration'

    index_view = IndexView

    def register(self, section):
        super().register(section)
        section.site = self  # Ensure we did this

    @property
    def sections(self):
        return self.values()

    @property
    def section_urls(self):
        return reduce(lambda a, b: a + b, [section.as_urls() for section in self.sections])

    def as_include(self):
        return include(
            [url(r'^$', self.index_view.as_view(site=self), name='index')] + self.section_urls,
            app_name='admin',
            namespace=self.namespace
        )
