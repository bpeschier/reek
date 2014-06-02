from django.views.generic.base import TemplateView, ContextMixin
from django.views.generic import detail as detail_views
from django.views.generic import edit as edit_views
from django.views.generic import list as list_views


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
    pass


class DeleteView(edit_views.DeleteView):
    pass