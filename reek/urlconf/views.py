from django.views.generic import base
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from ..utils import Pool


registered_views = Pool()


#
# Simple pages
#

class PageMixin(base.ContextMixin):
    page_url_kwarg = 'page'
    context_page_name = 'page'

    def get_page(self):
        """
        Get the page object from kwargs.
        """
        return self.kwargs.get(self.page_url_kwarg, None)

    def get_context_page_name(self, obj):
        """
        Get the name to use for the page object.
        """
        if self.context_page_name:
            return self.context_page_name
        elif isinstance(obj, models.Model):
            return obj._meta.object_name.lower()
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = {}
        context_page_name = self.get_context_page_name(self.page)
        if context_page_name:
            context[context_page_name] = self.page
        context.update(kwargs)
        return super().get_context_data(**context)


class BasePageView(PageMixin, base.View):
    allows_subpages = False

    def is_ancestor_view(self):
        return len(self.kwargs.get('subpage_slugs', [])) > 0

    def dispatch(self, request, *args, **kwargs):
        """
        Check if we have subhomes
        """
        if not self.allows_subpages and self.is_ancestor_view():
            raise Http404(_("View '%(verbose_name)s' does not allow subpages") %
                          {'verbose_name': self.__class__.__name__})
        return super().dispatch(request, *args, **kwargs)


class PageView(base.TemplateResponseMixin, BasePageView):
    verbose_name = 'Simple page'

    def get(self, request, *args, **kwargs):
        self.page = self.get_page()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


#
# Content-based pages.
# These have their own Model which get fed to the template
#


class ContentMixin(base.ContextMixin):
    model = None
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_content_name = 'content'

    def get_content(self):
        """
        Get the content object from kwargs. Defaults to querying by slug.
        """
        content = None
        if self.model and self.slug_url_kwarg:
            slug = self.kwargs.get(self.slug_url_kwarg, None)
            slug_filter = {self.slug_field: slug, }
            try:
                content = self.model.objects.get(**slug_filter)
            except self.model.DoesNotExist:
                raise Http404(_("No %(verbose_name)s found matching the slug") %
                              {'verbose_name': self.model._meta.verbose_name})
        return content

    def get_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.slug_field

    def get_content_slug(self):
        """
        Get (or generate) the slug from the content object.
        """
        self.content = self.content or self.get_content()
        return getattr(self.content, self.get_slug_field())

    def get_context_content_name(self, obj):
        """
        Get the name to use for the content object.
        """
        if self.context_content_name:
            return self.context_content_name
        elif isinstance(obj, models.Model):
            return obj._meta.object_name.lower()
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = {}
        context_content_name = self.get_context_content_name(self.content)
        if context_content_name:
            context[context_content_name] = self.content
        context.update(kwargs)
        return super().get_context_data(**context)


class ContentTemplateMixin(base.TemplateResponseMixin, ContentMixin):
    def get_template_names(self):
        try:
            names = super().get_template_names()
        except base.ImproperlyConfigured:
            names = []

        if self.model:
            names.append('pages/{content_model}.html'.format(content_model=self.model._meta.object_name.lower()))
        return names


class ContentView(ContentTemplateMixin, ContentMixin, BasePageView):
    verbose_name = 'Content page'

    def get(self, request, *args, **kwargs):
        self.page = self.get_page()
        self.content = self.get_content()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


#
# Application pages
# These act as anchor of another Django app
#

class ApplicationView:
    urlconf_name = None
    namespace = None
    app_name = None

    verbose_name = None
