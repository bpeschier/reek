from django.conf.urls import url as conf_url, include
from django.core.exceptions import ImproperlyConfigured

from urlconf import urls
from . import views


class Admin(urls.URLs):
    label = None

    def __init__(self, site=None):
        self.site = site
        super().__init__()

    def get_label(self):
        return self.label

    def as_urls(self):
        # Prefix the urls with the app and model-name
        return conf_url(r'^{label}/'.format(label=self.get_label()), include(super().as_urls()))


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
            namespace=self.site.namespace
        )

    def get_label(self):
        return self.label or '{app}/{model}'.format(**self.get_view_name_kwargs())

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
