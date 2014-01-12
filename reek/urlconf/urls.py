import re
from django.core.urlresolvers import ResolverMatch, Resolver404, RegexURLResolver, LocaleRegexProvider, get_resolver, \
    RegexURLPattern
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_text
from django.utils.regex_helper import normalize
from django.utils.translation import get_language
from django.db.models.signals import post_save

from .views import registered_views, ApplicationView


class PageResolver(RegexURLResolver):
    """
    Extension of core's RegexURLResolver which resolves paths for pages.

    Integrates any ApplicationView into reverse information. This lookup is
    (crudely) refreshed every time a page gets saved
    """

    def __init__(self, page_model, namespace=None, app_name=None):
        LocaleRegexProvider.__init__(self, r'')
        self.page_model = page_model
        self.namespace = namespace
        self.app_name = app_name
        self.default_kwargs = {}

        # Private dicts used for reverse mapping
        self._reverse_dict = {}
        self._namespace_dict = {}
        self._app_dict = {}

        # Let us see if this will clear the root url resolver
        def clear_urlconf(**kwargs):
            get_resolver(None)._populate()

        post_save.connect(clear_urlconf, sender=self.page_model)

    def __repr__(self):
        return '<Page resolver>'

    @staticmethod
    def get_subresolver(view_class):
        return RegexURLResolver(
            r'', urlconf_name=view_class.urlconf_name, namespace=view_class.namespace, app_name=view_class.app_name)

    def _populate(self):
        lookups = MultiValueDict()
        namespaces = {}
        apps = {}

        # PageResolver does not have reverses,
        # but ApplicationViews might have
        for page in self.page_model.objects.all():
            view_class = registered_views.get_by_name(page.view_name)
            if issubclass(view_class, ApplicationView):
                resolver = self.get_subresolver(view_class)
                self._populate_subresolver(resolver, lookups, namespaces, apps)

        language_code = get_language()
        self._reverse_dict[language_code] = lookups
        self._namespace_dict[language_code] = namespaces
        self._app_dict[language_code] = apps

    @staticmethod
    def _populate_subresolver(resolver, lookups, namespaces, apps):
        # XXX emulate part of _populate :/
        p_pattern = resolver.regex.pattern
        if p_pattern.startswith('^'):
            p_pattern = p_pattern[1:]
        if resolver.namespace:
            namespaces[resolver.namespace] = (p_pattern, resolver)
            if resolver.app_name:
                apps.setdefault(resolver.app_name, []).append(resolver.namespace)
        else:
            parent = normalize(resolver.regex.pattern)
            for name in resolver.reverse_dict:
                for matches, pat, defaults in resolver.reverse_dict.getlist(name):
                    new_matches = []
                    for piece, p_args in parent:
                        new_matches.extend((piece + suffix, p_args + args) for (suffix, args) in matches)
                    lookups.appendlist(name, (new_matches, p_pattern + pat, dict(defaults, **resolver.default_kwargs)))
            for namespace, (prefix, sub_pattern) in resolver.namespace_dict.items():
                namespaces[namespace] = (p_pattern + prefix, sub_pattern)
            for app_name, namespace_list in resolver.app_dict.items():
                apps.setdefault(app_name, []).extend(namespace_list)

    def get_pages_for_path(self, slugs):
        """
        Finds pages for given slugs in the path.
        Ordered by length, so the deepest option is on top.
        """

    def resolve(self, path):
        """
        Match path to Page object and return its registered view
        """
        path = force_text(path)  # path may be a reverse_lazy object

        if path and not path.endswith('/'):  # paths for pages should end with /
            raise Resolver404({'tried': [], 'path': path})

        clean_path = path[:-1]  # remove trailing /
        slugs = clean_path.split('/') if len(clean_path) > 0 else []
        ancestor_paths = [''] + ['/'.join(slugs[:i + 1]) for i in range(len(slugs))]
        pages = self.page_model.objects.filter(path__in=ancestor_paths).order_by('-path')
        if not pages.exists():
            raise Resolver404({'tried': [[RegexURLPattern(t + '/', None)] for t in ancestor_paths], 'path': path})
        page = pages[0]  # this is our best candidate

        # Check which part of the url we are using
        if not page.path:
            page_slug = ''
            subpage_slugs = slugs
        else:
            used_slugs = page.path.split('/')
            page_slug = used_slugs[-1]
            subpage_slugs = slugs[len(used_slugs):]
        subpage_path = ''.join(slug + '/' for slug in subpage_slugs)

        # Return registered view with slugs
        view_class = registered_views.get_by_name(page.view_name)
        if not view_class.allows_subpages and subpage_path:
            raise Resolver404({'tried': [[RegexURLPattern(t + '/', None)] for t in ancestor_paths], 'path': path})



        # If we have an ApplicationView, we need to go deeper
        if issubclass(view_class, ApplicationView):
            resolver = self.get_subresolver(view_class)
            return resolver.resolve(subpage_path)
        else:
            kwargs = {
                'page': page,
                'slug': page_slug,
                'subpage_slugs': subpage_slugs,
                'subpage_path': subpage_path,
            }
            return ResolverMatch(
                view_class.as_view(), [], kwargs, app_name=self.app_name, namespaces=[self.namespace, ])


class URLConfWrapper:
    """
    Mimicks a urls.py urlconf interface so RegexURLResolver can work with it
    """

    def __init__(self, resolver):
        self.resolver = resolver

    @property
    def urlpatterns(self):
        return [self.resolver, ]


def page_urls(page_model, app_name=None, namespace=None):
    """
    Include page urls as pattern.

    Usage:

    urlpatterns = patterns(
        '',
        page_urls(Page),
    )
    """
    return PageResolver(page_model, app_name=app_name, namespace=namespace)


def include_pages(page_model, app_name=None, namespace=None):
    """
    Include page urls within a url pattern.

    Usage:

    urlpatterns = patterns(
        '',
        url(r'^subpath/', include_pages(Page)),
    )
    """
    return URLConfWrapper(page_urls(page_model, app_name, namespace)), app_name, namespace


def page_patterns(page_model):
    """
    Include page urls as pattern list.

    Usage:

    urlpatterns = patterns(
        '',
        url(r'^some-path/$', 'some.view'),
    ) + page_patterns(Page)
    """
    return [page_urls(page_model), ]
