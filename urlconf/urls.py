from collections import OrderedDict
import copy

from django.conf.urls import patterns, url as conf_url
from django.views.generic.base import View

from .urlresolvers import PageResolver



#
# Declared URL patterns
#

class URL:
    # Tracks each time a URL instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, pattern, view, name=None):
        self.pattern = pattern
        self.name = name
        self.view = view
        self.namespace = None

        self.creation_counter = URL.creation_counter
        URL.creation_counter += 1

    def as_url(self):
        return conf_url(self.pattern, self.view, name=self.name)

    @property
    def reverse_name(self):
        if self.namespace is None:
            return self.name
        else:
            return '{ns}:{name}'.format(ns=self.namespace, name=self.name)

    def update_instance(self, name, view):
        self.name = name
        self.view = view


class URLsMeta(type):
    def __new__(mcs, name, bases, attrs):
        # Collect urls from current class.
        current_urls = []
        for key, value in list(attrs.items()):
            if isinstance(value, URL):
                current_urls.append((key, value))
                attrs.pop(key)
        current_urls.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_urls'] = OrderedDict(current_urls)

        new_class = super().__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_urls = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect urls from base class.
            if hasattr(base, 'declared_urls'):
                declared_urls.update(base.declared_urls)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_urls:
                    declared_urls.pop(attr)

        new_class.base_urls = declared_urls
        new_class.declared_urls = declared_urls

        return new_class


class BaseURLs:
    """
    URLs are collections of urls.

    They expose a single urls property which returns the patterns for
    the underlying urls.
    """

    declared_urls = OrderedDict()
    base_urls = OrderedDict()

    def __init__(self):
        # base_urls is the *class*-wide definition of urls
        self.urls = copy.deepcopy(self.base_urls)

        # Update based on this URLs
        for name, url in self.urls.items():
            url.update_instance(
                self.get_view_name(name, url),
                self.get_view(name, url),
            )

    def get_view_name_kwargs(self):
        return {}

    def get_view_kwargs(self):
        return {}

    def get_view_name(self, attr_name, url):
        name_kwargs = getattr(self, 'get_{}_name_kwargs'.format(attr_name), self.get_view_name_kwargs)()
        name = attr_name if url.name is None else url.name  # Use the overridden name if set
        return name.format(**name_kwargs)

    def get_view(self, attr_name, url):
        if isinstance(url.view, type):
            view_kwargs = getattr(self, 'get_{}_view_kwargs'.format(attr_name), self.get_view_kwargs)()
            return url.view.as_view(**view_kwargs)
        else:
            return url.view

    def as_urls(self):
        return patterns('', *[url.as_url() for url in self.urls.values()])


class URLs(BaseURLs, metaclass=URLsMeta):
    pass


#
# Dynamic page confs
#

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

    urlpatterns = [
        page_urls(Page),
    ]
    """
    return PageResolver(page_model, app_name=app_name, namespace=namespace)


def include_pages(page_model, app_name=None, namespace=None):
    """
    Include page urls within a url pattern.

    Usage:

    urlpatterns = [
        url(r'^subpath/', include_pages(Page)),
    ]
    """
    return URLConfWrapper(page_urls(page_model, app_name, namespace)), app_name, namespace


