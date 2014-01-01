from django.core.urlresolvers import ResolverMatch, Resolver404, RegexURLResolver, LocaleRegexProvider, get_resolver
from django.utils.datastructures import MultiValueDict
from django.utils.translation import get_language

from .views import registered_views, ApplicationView


class PageResolver(RegexURLResolver):
    """
    Extension of core's RegexURLResolver which resolves paths for pages.

    Does not provide any reverse information.
    """

    def __init__(self, page_model, namespace=None, app_name=None):
        LocaleRegexProvider.__init__(self, r'')
        self.page_model = page_model
        self.namespace = namespace
        self.app_name = app_name

        # Private dicts used for reverse mapping
        self._reverse_dict = {}
        self._namespace_dict = {}
        self._app_dict = {}

    def __repr__(self):
        return '<Page resolver>'

    def _populate(self):
        # Since we provide no reverses, we just leave this empty,
        # but we do need to setup with the language
        language_code = get_language()
        self._reverse_dict[language_code] = MultiValueDict()
        self._namespace_dict[language_code] = {}
        self._app_dict[language_code] = {}

    def get_pages_for_path(self, slugs):
        """
        Finds pages for given slugs in the path.
        Ordered by length, so the deepest option is on top.
        """
        ancestor_paths = [''] + ['/'.join(slugs[:i + 1]) for i in range(len(slugs))]
        return self.page_model.objects.filter(path__in=ancestor_paths).order_by('-path')

    def resolve(self, path):
        """
        Match path to Page object and return its registered view
        """
        if path and not path.endswith('/'):  # paths for pages should end with /
            raise Resolver404({'tried': [], 'path': path})

        try:
            clean_path = path[:-1]  # remove trailing /
            slugs = clean_path.split('/') if len(clean_path) > 0 else []
            page = self.get_pages_for_path(slugs)[0]  # Fetch best candidate
        except (self.page_model.DoesNotExist, IndexError):
            raise Resolver404({'tried': [], 'path': path})
        else:

            # Check which part of the url we are using
            if not page.path:
                page_slug = ''
                subpage_slugs = slugs
            else:
                used_slugs = page.path.split('/')
                page_slug = used_slugs[-1]
                subpage_slugs = slugs[len(used_slugs):]
            subpage_path = '/' + ''.join(slug + '/' for slug in subpage_slugs)

            # Return registered view with slugs
            view_class = registered_views.get_by_name(page.view_name)

            # If we have an ApplicationView, we need to go deeper
            if issubclass(view_class, ApplicationView):
                return get_resolver(view_class.urlconf_name).resolve(subpage_path)
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
        return [self.resolver,]


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
