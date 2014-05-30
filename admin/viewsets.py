from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView


class ViewSet:
    """
    ViewSets are collections of views.

    They expose a single urls property which returns the patterns for
    the underlying views.
    """

    @property
    def urls(self):
        raise NotImplemented


class ModelViewSet(ViewSet):
    model = None

    operations = ('list', 'create', 'detail', 'update', 'delete', )

    base_template_name = "{app}/{model}_{operation}.html"

    list_pattern = r'^$'
    create_pattern = r'^add/$'
    detail_pattern = r'^(?P<pk>.+)/preview/$'
    update_pattern = r'^(?P<pk>.+)/edit/$'
    delete_pattern = r'^(?P<pk>.+)/delete/$'

    list_view = ListView
    create_view = CreateView
    detail_view = DetailView
    update_view = UpdateView
    delete_view = DeleteView

    def __init__(self, model=None):
        if model is not None:
            self.model = model

    #
    # Views
    #

    def list(self):
        return self.get_operation_view(self.list_view)

    def create(self):
        return self.get_operation_view(self.create_view)

    def detail(self):
        return self.get_operation_view(self.detail_view)

    def update(self):
        return self.get_operation_view(self.update_view)

    def delete(self):
        return self.get_operation_view(self.delete_view)

    def get_operation_view(self, view):
        # Use the template_name_suffix to generate a new template_name for this operation
        # This mimics the template mixins, but we want to be able to override the entire group
        return view.as_view(template_name=self.get_template_name_for(view.template_name_suffix))

    #
    # Helpers
    #

    def get_app_label(self):
        return self.model._meta.app_label

    def get_model_name(self):
        return self.model._meta.model_name

    #
    # Templates
    #

    def get_template_name_for(self, operation):
        # This just applies the information to the format in base_template_name,
        # but can be overwritten to have more control
        return self.base_template_name.format(
            app=self.get_app_label(),
            model=self.get_model_name(),
            operation=operation
        )

    def get_view_name_kwargs(self):
        return {
            'app': self.get_app_label(),
            'model': self.get_model_name(),
        }

    #
    # URLs
    #

    @property
    def urls(self):
        view_kwargs = self.get_view_name_kwargs()

        # Generate operation patterns
        try:
            operation_patterns = [
                url(getattr(self, '{}_pattern'.format(operation)), getattr(self, operation)(),
                    name='{app}_{model}_{operation}'.format(operation=operation, **view_kwargs))
                for operation in self.operations
            ]
        except AttributeError:
            raise ImproperlyConfigured(
                'Not all patterns and/or views are configured for operations {}'.format(self.operations))

        return patterns('', *operation_patterns)
