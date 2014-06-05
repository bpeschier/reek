import functools
from django.core.urlresolvers import ResolverMatch, Resolver404, RegexURLResolver, LocaleRegexProvider, clear_url_caches
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_text
from django.utils.regex_helper import normalize
from django.utils.translation import get_language
from django.db.models.signals import post_save

from .views import ApplicationView


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

        # urlpatterns
        self._callback_strs = set()
        self._populated = False

        # Let us see if this will clear the root url resolver
        def clear_urlconf(**kwargs):
            clear_url_caches()

        post_save.connect(clear_urlconf, sender=self.page_model)

    def __repr__(self):
        return '<Page resolver>'

    @staticmethod
    def get_subresolver(view_class, path=None):
        """
        Create a subresolver for an ApplicationView
        Resolver will have path as base path/regex.
        """
        path = r'' if path is None else r'^{}/'.format(path)
        return RegexURLResolver(
            path, urlconf_name=view_class.urlconf_name, namespace=view_class.namespace, app_name=view_class.app_name)

    def _populate(self):
        lookups = MultiValueDict()
        namespaces = {}
        apps = {}

        # PageResolver does not have reverses,
        # but ApplicationViews might have
        for page in self.page_model.objects.all():
            view_class = page.view_class
            if issubclass(view_class, ApplicationView):
                resolver = self.get_subresolver(view_class, page.path)
                self._populate_subresolver(resolver, lookups, namespaces, apps)

        language_code = get_language()
        self._reverse_dict[language_code] = lookups
        self._namespace_dict[language_code] = namespaces
        self._app_dict[language_code] = apps

        self._populated = True

    def _populate_subresolver(self, resolver, lookups, namespaces, apps):
        # XXX emulate part of _populate :/

        lookups = MultiValueDict()
        namespaces = {}
        apps = {}
        language_code = get_language()

        if hasattr(resolver, '_callback_str'):
            self._callback_strs.add(resolver._callback_str)
        elif hasattr(resolver, '_callback'):
            callback = resolver._callback
            if isinstance(callback, functools.partial):
                callback = callback.func

            if not hasattr(callback, '__name__'):
                lookup_str = callback.__module__ + "." + callback.__class__.__name__
            else:
                lookup_str = callback.__module__ + "." + callback.__name__
            self._callback_strs.add(lookup_str)
        p_pattern = resolver.regex.pattern
        if p_pattern.startswith('^'):
            p_pattern = p_pattern[1:]
        if isinstance(resolver, RegexURLResolver):
            if resolver.namespace:
                namespaces[resolver.namespace] = (p_pattern, resolver)
                if resolver.app_name:
                    apps.setdefault(resolver.app_name, []).append(resolver.namespace)
            else:
                parent_pat = resolver.regex.pattern
                for name in resolver.reverse_dict:
                    for matches, pat, defaults in resolver.reverse_dict.getlist(name):
                        new_matches = normalize(parent_pat + pat)
                        lookups.appendlist(name,
                            (new_matches, p_pattern + pat, dict(defaults, **resolver.default_kwargs)))
                for namespace, (prefix, sub_pattern) in resolver.namespace_dict.items():
                    namespaces[namespace] = (p_pattern + prefix, sub_pattern)
                for app_name, namespace_list in resolver.app_dict.items():
                    apps.setdefault(app_name, []).extend(namespace_list)
                self._callback_strs.update(resolver._callback_strs)
        else:
            bits = normalize(p_pattern)
            lookups.appendlist(resolver.callback, (bits, p_pattern, resolver.default_args))
            if resolver.name is not None:
                lookups.appendlist(resolver.name, (bits, p_pattern, resolver.default_args))

    def find_page_for_path(self, path):
        """
        Resolve the path into the Page instance and return it with trailing subpage information.
        """
        clean_path = path[:-1]  # remove trailing /
        slugs = clean_path.split('/') if clean_path else []
        ancestor_paths = [''] + ['/'.join(slugs[:i + 1]) for i in range(len(slugs))]
        pages = self.page_model.objects.filter(path__in=ancestor_paths).order_by('-path')

        # Bail if we don't have a result
        if not pages.exists():
            raise Resolver404({'tried': [], 'path': path})  # since we query, we don't really have a "tried" list

        page = pages[0]  # this is our best candidate

        # Check which part of the url we are using
        used_slugs = page.path.split('/') if page.path else []
        page_slug = used_slugs[-1] if used_slugs else ''
        subpage_slugs = slugs[len(used_slugs):]

        return page, page_slug, subpage_slugs

    def resolve(self, path):
        """
        Match path to Page object and return its registered view
        """
        # Clean up and check path
        path = force_text(path)  # path may be a reverse_lazy object
        if path and not path.endswith('/'):
            # If we don't have a / at the end, we bail. If APPEND_SLASH is set,
            # this will redirect it to the view with a /
            raise Resolver404({'tried': [], 'path': path})

        # Get the associated page
        page, page_slug, subpage_slugs = self.find_page_for_path(path)

        # Fetch the View class
        view_class = page.view_class

        # The view specifies if it allows subpages. We raise Resolver404 to
        # allow other patterns below this one in the urlconf
        if not view_class.allows_subpages and subpage_slugs:
            raise Resolver404({'tried': [], 'path': path})

        # If we have an ApplicationView, we need to go deeper
        if issubclass(view_class, ApplicationView):
            resolver = self.get_subresolver(view_class, page.path)
            try:
                return resolver.resolve(path)
            except Resolver404 as e:
                # Add PageResolver as base to the tried patterns
                sub_tried = e.args[0].get('tried') or []
                raise Resolver404({'path': path, 'tried': [[resolver] + t for t in sub_tried]})
        else:
            kwargs = {
                'page': page,
                'slug': page_slug,
                'subpage_slugs': subpage_slugs,
            }
            return ResolverMatch(view_class.as_view(), [], kwargs, app_name=self.app_name, namespaces=[self.namespace])
