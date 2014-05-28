from django.views.generic.base import TemplateView, ContextMixin


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


