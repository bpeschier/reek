from django.views.generic import base
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_lazy as _


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

    @staticmethod
    def can_have_parent_view(view_class):
        """
        Helper function for validating whether or not this view can
        have view_class as parent.
        """
        return True


class BasePageView(PageMixin, base.View):
    allows_subpages = False

    def is_ancestor_view(self):
        return len(self.kwargs.get('subpage_slugs', [])) > 0

    def dispatch(self, request, *args, **kwargs):
        """
        Check if we have subhomes
        """
        if not self.allows_subpages and self.is_ancestor_view():
            raise Http404(_("View '%(name)s' does not allow subpages") %
                          {'name': self.__class__.__name__})
        return super().dispatch(request, *args, **kwargs)


class PageView(base.TemplateResponseMixin, BasePageView):
    name = 'Simple page'
    label = 'page'

    def get(self, request, **kwargs):
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

    @classmethod
    def get_content_by_slug(cls, slug):
        """
        Query the database for the related content object
        """
        slug_filter = {cls.slug_field: slug, }
        return cls.model.objects.get(**slug_filter)

    def get_content(self):
        """
        Get the content object from kwargs. Defaults to querying by slug.
        """
        content = None
        if self.model and self.slug_url_kwarg:
            slug = self.kwargs.get(self.slug_url_kwarg, None)
            try:
                content = ContentMixin.get_content_by_slug(slug)
            except self.model.DoesNotExist:
                raise Http404(_("No %(name)s found matching the slug") %
                              {'name': self.model._meta.name})
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
    name = 'Content page'
    label = 'content_page'

    def get(self, request, **kwargs):
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

    name = None
    label = None
    allows_subpages = True
