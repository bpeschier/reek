from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http.response import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic.base import TemplateView, ContextMixin
from django.views.generic import detail as detail_views
from django.views.generic import edit as edit_views
from django.views.generic import list as list_views
from django.views.generic.edit import FormView


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

    def get_success_url(self):
        return reverse(self.admin.urls['index'].reverse_name)

    def get_template_names(self):
        info = dict(
            app=self.model._meta.app_label,
            model=self.model._meta.model_name,
            suffix=self.template_name_suffix
        )
        # Overwrite with our specific model template first,
        # and add a generic template as a fallback
        return ['admin/{app}/{model}{suffix}.html'.format(**info), 'admin/default/object{suffix}.html'.format(**info)]


class StaffRequiredMixin:
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BaseSiteMixin(StaffRequiredMixin, SiteContextMixin):
    pass


class BaseAdminMixin(StaffRequiredMixin, AdminContextMixin):
    pass


class LoginView(SiteContextMixin, FormView):
    template_name = 'admin/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('admin:index')

    def form_valid(self, form):
        redirect_to = self.get_success_url()
        # Ensure the user-originating redirection url is safe.
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        # Okay, security check complete. Log the user in.
        login(self.request, form.get_user())

        return HttpResponseRedirect(redirect_to)


class ChangePasswordView:
    pass


class ResetPasswordView:
    pass


class IndexView(BaseSiteMixin, TemplateView):
    template_name = 'admin/index.html'


class SectionIndexView(BaseSiteMixin, TemplateView):
    template_name = 'admin/section_index.html'
    section = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        return context


class ListView(BaseAdminMixin, list_views.ListView):
    pass


class CreateView(BaseAdminMixin, edit_views.CreateView):
    pass


class DetailView(BaseAdminMixin, detail_views.DetailView):
    pass


class UpdateView(BaseAdminMixin, edit_views.UpdateView):
    pass


class DeleteView(BaseAdminMixin, edit_views.DeleteView):
    pass