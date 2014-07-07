from functools import reduce

from django.conf.urls import include
from urlconf.urls import URLs, URL

from .views import IndexView, LoginView, LogoutView
from .registry import RegistryMixin


class AdminSite(RegistryMixin, URLs):
    template_admin_base = 'admin/base.html'
    namespace = 'admin'

    name = 'Django administration'

    index = URL(r'^$', IndexView, name='index')
    login = URL(r'^login/$', LoginView, name='login')
    logout = URL(r'^logout/$', LogoutView, name='logout')

    def update_url(self, name, url):
        url.update_instance(
            self.get_view_name(name, url),
            self.get_view(name, url),
            namespace=self.namespace
        )

    def get_view_kwargs(self):
        return {
            'site': self,
        }

    def register(self, section):
        super().register(section)
        section.site = self  # Ensure we did this

    @property
    def sections(self):
        return self.values()

    @property
    def section_urls(self):
        return reduce(lambda a, b: a + b, [section.as_urls() for section in self.sections])

    def as_urls(self):
        return super().as_urls() + self.section_urls

    def as_include(self):
        return include(
            self.as_urls(),
            app_name='admin',
            namespace=self.namespace
        )
