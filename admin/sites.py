from functools import reduce

from django.conf.urls import patterns, url, include

from django.utils.translation import ugettext_lazy as _

from .views import IndexView


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class AdminSite:
    template_admin_base = 'admin/base.html'
    namespace = 'admin'

    name = 'Django administration'

    index_view = IndexView

    def __init__(self):
        self._registry = {}

    def register(self, section):
        if section.label in self._registry:
            raise AlreadyRegistered(
                _('Section %s is already registered') % section.label,
            )
        else:
            self._registry[section.label] = section
            section.site = self  # Ensure we did this

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('Section %s is not registered') % label)
        return self._registry[label]

    @property
    def sections(self):
        return list(self._registry.values())

    @property
    def section_urls(self):
        return reduce(lambda a, b: a + b, [section.as_urls() for section in self.sections])

    @property
    def urls(self):
        return include(
            patterns(
                '',
                url(r'^$', self.index_view.as_view(site=self), name='index'),
                self.section_urls
            ),
            app_name='admin',
            namespace=self.namespace
        )
