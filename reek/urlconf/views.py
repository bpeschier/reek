from django.views.generic import base
from django.db import models
from django.http import Http404
from django.utils import six
from django.utils.decorators import classonlymethod
from django.utils.translation import ugettext_lazy as _

from ..utils import Pool


class ViewPool(Pool):
    def get_view_by_name(self, name, *args, **kwargs):
        view_class = super(ViewPool, self).get_by_name(name)
        return view_class.as_view(*args, **kwargs)


registered_views = ViewPool()


class BasePageResolver(object):
    page_model = None

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classonlymethod
    def as_view(cls, **init_kwargs):
        """
        Main entry point for a request-response process.
        """

        def view(request, path, *args, **kwargs):
            self = cls(**init_kwargs)
            return self.dispatch(request, path, *args, **kwargs)

        return view

    def get_pages_for_path(self, slugs):
        """
        Finds pages for given slugs in the path.
        Ordered by length, so the deepest option is on top.
        """
        ancestor_paths = [u''] + [u'/'.join(slugs[:i + 1]) for i in range(len(slugs))]
        return self.page_model.objects.filter(path__in=ancestor_paths).order_by('-path')

    def dispatch(self, request, path, *args, **kwargs):
        """
        Match path to Page object and call its registered view
        """
        try:
            path = path.strip(u'/')
            slugs = path.split(u'/') if len(path) > 0 else []
            page = self.get_pages_for_path(slugs)[0]  # Fetch best candidate

            # Check which part of the url we are using
            if not page.path:
                page_slug = u''
                subpage_slugs = slugs
            else:
                used_slugs = page.path.split(u'/')
                page_slug = used_slugs[-1]
                subpage_slugs = slugs[len(used_slugs):]

            # Call registered view with slugs
            view = registered_views.get_view_by_name(page.view_name)
            return view(request, page=page, slug=page_slug, subpage_slugs=subpage_slugs, *args, **kwargs)

        except (self.page_model.DoesNotExist, IndexError):
            pass

        raise Http404(_("No page found for path '%(path)s'", {'path': path}))


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
        return super(PageMixin, self).get_context_data(**context)


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
        return super(BasePageView, self).dispatch(request, *args, **kwargs)


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
        return super(ContentMixin, self).get_context_data(**context)


class ContentTemplateMixin(base.TemplateResponseMixin, ContentMixin):
    def get_template_names(self):
        try:
            names = super(ContentTemplateMixin, self).get_template_names()
        except base.ImproperlyConfigured:
            names = []

        if self.model:
            names.append('pages/{content_model}.html'.format(content_model=self.model._meta.object_name.lower()))
        return names


class PageView(base.TemplateResponseMixin, BasePageView):
    verbose_name = 'Simple page'

    def get(self, request, *args, **kwargs):
        self.page = self.get_page()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class ContentView(ContentTemplateMixin, ContentMixin, BasePageView):
    verbose_name = 'Content page'

    def get(self, request, *args, **kwargs):
        self.page = self.get_page()
        self.content = self.get_content()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


