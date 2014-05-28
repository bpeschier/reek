from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from .views import IndexView


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class AdminSite:
    template_admin_base = 'admin/base.html'

    name = 'Django administration'

    def __init__(self):
        self._registry = {}

    def register(self, section_class):
        if section_class.label in self._registry:
            raise AlreadyRegistered(
                _('Section %s is already registered') % section_class.label,
            )
        else:
            self._registry[section_class.label] = section_class

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('Section %s is not registered') % label)
        return self._registry[label]

    @property
    def sections(self):
        return self._registry.values()

    @property
    def urls(self):
        return patterns(
            '',
            url(r'^$', IndexView.as_view(site=self), name='index')
        )
