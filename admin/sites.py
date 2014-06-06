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

    def register(self, admin_class):
        if admin_class.label in self._registry:
            raise AlreadyRegistered(
                _('Section %s is already registered') % admin_class.label,
            )
        else:
            self._registry[admin_class.label] = admin_class(site=self)  # TODO: instance or class?

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('Section %s is not registered') % label)
        return self._registry[label]

    @property
    def admins(self):
        return list(self._registry.values())

    @property
    def admin_urls(self):
        return reduce(lambda a, b: a + b, [admin.as_urls() for admin in self.admins])

    def as_urls(self):
        return include(
            patterns(
                '',
                url(r'^$', self.index_view.as_view(site=self), name='index'),
                self.admin_urls
            ),
            app_name='admin',
            namespace=self.namespace
        )
