from functools import reduce

from django.apps.registry import apps

from django.conf.urls import url as conf_url, include
from django.core.exceptions import ImproperlyConfigured

from urlconf import urls
from . import views
from .registry import RegistryMixin


class LabeledURLs(urls.URLs):
    label = None
    verbose_name = None

    def __init__(self):
        self.label = self.get_label()
        self.verbose_name = self.get_verbose_name()
        super().__init__()

    def get_label(self):
        return self.label

    def get_verbose_name(self):
        return self.verbose_name

    def as_urls(self, extra_urls=None):
        extra_urls = [] if extra_urls is None else extra_urls
        # Prefix the urls with the label
        return [conf_url(
            r'^{label}/'.format(label=self.label),
            include(super().as_urls() + extra_urls)
        )]


#
# Sections
#

class AdminSection(RegistryMixin, LabeledURLs):
    index = urls.URL(r'^$', views.SectionIndexView, name='{section}_index')

    def __init__(self, site=None):
        self.site = site
        site.register(self)
        super().__init__()

    def register(self, admin_class):
        super().register(self.init_admin(admin_class))

    def update_url(self, name, url):
        url.update_instance(
            self.get_view_name(name, url),
            self.get_view(name, url),
            namespace=self.site.namespace
        )

    def init_admin(self, admin_class):
        return admin_class(section=self)

    @property
    def admins(self):
        return self.values()

    def admins_as_urls(self):
        return reduce(lambda a, b: a + b, [admin.as_urls() for admin in self.admins])

    def get_view_kwargs(self):
        return {
            'site': self.site
        }

    def get_view_name_kwargs(self):
        return {
            'section': self.label,
        }

    def as_urls(self, extra_urls=None):
        extra_urls = [] if extra_urls is None else extra_urls
        return super().as_urls(extra_urls=self.admins_as_urls() + extra_urls)


class AppAdminSection(AdminSection):
    app = None

    def __init__(self, app_label=None, **kwargs):
        self.app = apps.get_app_config(app_label)
        super().__init__(**kwargs)

    def get_label(self):
        return self.label or self.app.label

    def get_verbose_name(self):
        return self.verbose_name or self.app.verbose_name


#
# Admin within a Section
#

class Admin(LabeledURLs):
    def __init__(self, section=None):
        self.section = section
        super().__init__()

    @property
    def site(self):
        return self.section.site


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

    def get_verbose_name(self):
        return self.verbose_name or self.model._meta.verbose_name_plural

    #
    # Helpers
    #

    def get_model_name(self):
        return self.model._meta.model_name

    def get_view_name_kwargs(self):
        return {
            'app': self.section.label,
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
