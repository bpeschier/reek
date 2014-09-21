from functools import reduce

from declarative_urlconf import URLs, URL
from .views import IndexView, LoginView, LogoutView
from .registry import RegistryMixin


class AdminSite(RegistryMixin, URLs):
    template_admin_base = 'admin/base.html'
    namespace = 'admin'
    app_name = 'admin'

    name = 'Django administration'

    index = URL(r'^$', IndexView, name='index')
    login = URL(r'^login/$', LoginView, name='login')
    logout = URL(r'^logout/$', LogoutView, name='logout')

    def get_view_kwargs(self, name):
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
