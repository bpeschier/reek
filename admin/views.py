from django.views.generic.base import TemplateView, ContextMixin
from django.views.generic import detail as detail_views
from django.views.generic import edit as edit_views
from django.views.generic import list as list_views
from django.forms import models as model_forms


class AdminContextMixin(ContextMixin):
    site = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = self.site
        return context


class LoginView:
    pass


class ChangePasswordView:
    pass


class ResetPasswordView:
    pass


class IndexView(AdminContextMixin, TemplateView):
    template_name = 'admin/index.html'


class ListView(list_views.ListView):
    pass


class CreateView(edit_views.CreateView):
    pass


class DetailView(detail_views.DetailView):
    pass


class UpdateView(edit_views.UpdateView):
    def get_form_class(self):
        # XXX extract into mixin for other views, rethink how we
        # customise stuff in ModelAdmin

        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                self.fields = [f.name for f in model._meta.fields]

            return model_forms.modelform_factory(model, fields=self.fields)


class DeleteView(edit_views.DeleteView):
    pass