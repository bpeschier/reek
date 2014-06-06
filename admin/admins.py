from functools import reduce
from django.apps.registry import apps

from django.conf.urls import url as conf_url, include, patterns

from django.core.exceptions import ImproperlyConfigured

from django.utils.translation import ugettext_lazy as _

from urlconf import urls

from . import views

from .sites import AlreadyRegistered, NotRegistered


class Admin(urls.URLs):
    label = None

    def __init__(self, section=None):
        self.section = section
        super().__init__()

    def get_label(self):
        return self.label

    def as_urls(self):
        # Prefix the urls with the label
        return patterns('', conf_url(r'^{label}/'.format(label=self.get_label()), include(super().as_urls())))


class AdminSection(Admin):
    index = urls.URL(r'^$', views.SectionIndexView, name='{section}_index')

    def __init__(self, site=None):
        self._registry = {}
        site.register(self)
        super().__init__()

    def register(self, admin_class):
        if admin_class.label in self._registry:
            raise AlreadyRegistered(
                _('Admin %s is already registered') % admin_class.label,
            )
        else:
            self._registry[admin_class.label] = self.init_admin(admin_class)

    def update_url(self, name, url):
        url.update_instance(
            self.get_view_name(name, url),
            self.get_view(name, url),
            namespace=self.site.namespace
        )

    @property
    def admins(self):
        return list(self._registry.values())

    def init_admin(self, admin_class):
        return admin_class(section=self)

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('Admin %s is not registered') % label)
        return self._registry[label]

    @property
    def admin_urls(self):
        return reduce(lambda a, b: a + b, [admin.as_urls() for admin in self.admins])

    def get_view_name_kwargs(self):
        return {
            'section': self.get_label()
        }


class AppAdminSection(AdminSection):
    app = None

    def __init__(self, app_label=None, **kwargs):
        self.app = apps.get_app_config(app_label)
        super().__init__(**kwargs)

    def get_label(self):
        return self.label or self.app.label


class ModelAdmin(Admin):
    model = None
    fields = '__all__'

    index = urls.URL(r'^$', views.ListView, name='{app}_{model}_index')
    create = urls.URL(r'^add/$', views.CreateView, name='{app}_{model}_create')
    detail = urls.URL(r'^(?P<pk>.+)/preview/$', views.DetailView, name='{app}_{model}_detail')
    update = urls.URL(r'^(?P<pk>.+)/edit/$', views.UpdateView, name='{app}_{model}_update')
    delete = urls.URL(r'^(?P<pk>.+)/delete/$', views.DeleteView, name='{app}_{model}_delete')

    def __init__(self, model=None, **kwargs):
        super().__init__(**kwargs)
        self.model = self.model if model is None else model
        if self.model is None:
            raise ImproperlyConfigured('Model class is not set on ModelAdmin')

    def update_url(self, name, url):
        url.update_instance(
            self.get_view_name(name, url),
            self.get_view(name, url),
            namespace=self.section.site.namespace
        )

    def get_label(self):
        return self.label or self.get_model_name()

    #
    # Helpers
    #

    def get_app_label(self):
        return self.model._meta.app_label

    def get_model_name(self):
        return self.model._meta.model_name

    def get_view_name_kwargs(self):
        return {
            'app': self.get_app_label(),
            'model': self.get_model_name(),
        }

    def get_view_kwargs(self):
        return {
            'model': self.model,
        }

    def get_form_view_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs['fields'] = self.fields
        return kwargs

    def get_update_view_kwargs(self):
        return self.get_form_view_kwargs()

    def get_create_view_kwargs(self):
        return self.get_form_view_kwargs()
