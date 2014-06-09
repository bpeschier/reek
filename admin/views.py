from django.views.generic.base import TemplateView, ContextMixin, TemplateResponseMixin
from django.views.generic import detail as detail_views
from django.views.generic import edit as edit_views
from django.views.generic import list as list_views


class SiteContextMixin(ContextMixin):
    site = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = self.site
        return context


class AdminContextMixin(SiteContextMixin):
    admin = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin'] = self.admin
        return context

    def get_template_names(self):
        info = dict(
            app=self.model._meta.app_label,
            model=self.model._meta.model_name,
            suffix=self.template_name_suffix
        )
        # Overwrite with our specific model template first,
        # and add a generic template as a fallback
        return ['admin/{app}/{model}{suffix}.html'.format(**info), 'admin/default/object{suffix}.html'.format(**info)]


class LoginView:
    pass


class ChangePasswordView:
    pass


class ResetPasswordView:
    pass


class IndexView(SiteContextMixin, TemplateView):
    template_name = 'admin/index.html'


class SectionIndexView(SiteContextMixin, TemplateView):
    template_name = 'admin/section_index.html'
    section = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        return context


class ListView(AdminContextMixin, list_views.ListView):
    pass


class CreateView(AdminContextMixin, edit_views.CreateView):
    pass


class DetailView(AdminContextMixin, detail_views.DetailView):
    pass


class UpdateView(AdminContextMixin, edit_views.UpdateView):
    pass


class DeleteView(AdminContextMixin, edit_views.DeleteView):
    pass