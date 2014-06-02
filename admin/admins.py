from django.core.exceptions import ImproperlyConfigured

from urlconf import urls

from . import views


class Admin(urls.URLs):
    label = None


class ModelAdmin(Admin):
    model = None

    list = urls.URL(r'^$', views.ListView.as_view(), '{app}_{model}_list')
    create = urls.URL(r'^add/$', views.CreateView.as_view(), '{app}_{model}_create')
    detail = urls.URL(r'^(?P<pk>.+)/preview/$', views.DetailView.as_view(), '{app}_{model}_detail')
    update = urls.URL(r'^(?P<pk>.+)/edit/$', views.UpdateView.as_view(), '{app}_{model}_update')
    delete = urls.URL(r'^(?P<pk>.+)/delete/$', views.DeleteView.as_view(), '{app}_{model}_delete')

    def __init__(self, model=None):
        self.model = self.model if model is None else model
        if self.model is None:
            raise ImproperlyConfigured('Model class is not set on ModelAdmin')

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
