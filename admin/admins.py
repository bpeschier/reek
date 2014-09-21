from functools import reduce

from django.apps.registry import apps
from django.conf.urls import url as conf_url, include
from django.contrib.auth import get_permission_codename
from django.core.exceptions import ImproperlyConfigured

import declarative_urlconf as urlconf
from . import views
from .registry import RegistryMixin


class LabeledURLs(urlconf.URLs):
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
    index = urlconf.URL(r'^$', views.SectionIndexView, name='{section}_index')

    def __init__(self, site=None):
        self.site = site
        super().__init__()
        site.register(self)

    def get_namespace(self):
        return self.site.namespace

    def register(self, admin_class):
        super().register(self.init_admin(admin_class))

    def init_admin(self, admin_class):
        return admin_class(section=self)

    def has_permission(self, request):
        return True

    @property
    def admins(self):
        return self.values()

    def admins_as_urls(self):
        return reduce(lambda a, b: a + b, [admin.as_urls() for admin in self.admins])

    def get_view_kwargs(self, name):
        return {
            'site': self.site,
            'section': self,
        }

    def get_view_name_fields(self, name):
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
        label = super().get_label()
        return label if label is not None else self.app.label

    def get_verbose_name(self):
        verbose_name = super().get_verbose_name()
        return verbose_name if verbose_name is not None else self.app.verbose_name

    def has_permission(self, request):
        return request.user.has_module_perms(self.app.label)


#
# Admin within a Section
#

class Admin(LabeledURLs):
    list_display = ['__str__']

    def __init__(self, section=None):
        self.section = section
        super().__init__()

    @property
    def site(self):
        return self.section.site

    def has_add_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        raise NotImplementedError

    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        raise NotImplementedError

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        raise NotImplementedError

    def get_permissions(self, request):
        """
        Returns a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request)
        }


class ModelAdmin(Admin):
    model = None
    fields = '__all__'  # The admin shows all fields by default... for now

    index = urlconf.URL(r'^$', views.ListView, name='{app}_{model}_index')
    create = urlconf.URL(r'^add/$', views.CreateView, name='{app}_{model}_create')
    detail = urlconf.URL(r'^(?P<pk>.+)/preview/$', views.DetailView, name='{app}_{model}_detail')
    update = urlconf.URL(r'^(?P<pk>.+)/edit/$', views.UpdateView, name='{app}_{model}_update')
    delete = urlconf.URL(r'^(?P<pk>.+)/delete/$', views.DeleteView, name='{app}_{model}_delete')

    def __init__(self, model=None, **kwargs):
        # We need a model, either with the init or on the class
        self.model = self.model if model is None else model
        if self.model is None:
            raise ImproperlyConfigured('Model class is not set on ModelAdmin or in constructor')
        self.opts = self.model._meta

        super().__init__(**kwargs)

    #
    # URLs
    #

    def get_namespace(self):
        return self.section.site.namespace

    def get_view_kwargs(self, name):
        base_kwargs = {
            'model': self.model,
            'site': self.site,
            'admin': self,
        }
        if name in ['update', 'create']:
            base_kwargs.update({
                'fields': self.fields,
            })
        return base_kwargs

    def get_view_name_fields(self, name):
        return {
            'app': self.section.label,
            'model': self.opts.model_name,
        }

    #
    # Labels and naming
    #

    def get_label(self):
        label = super().get_label()
        return label if label is not None else self.opts.model_name

    def get_verbose_name(self):
        verbose_name = super().get_verbose_name()
        return verbose_name if verbose_name is not None else self.opts.verbose_name_plural

    #
    # Permissions
    #

    def has_add_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('add', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('change', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('delete', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))
