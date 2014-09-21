from collections import OrderedDict
import copy

from django.conf.urls import url as conf_url, include as conf_include
from django.views.generic.base import View

from .urlresolvers import PageResolver


#
# Declared URL patterns
#

class URL:
    # Tracks each time a URL instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, pattern, view, attribute_name=None, name=None, namespace=None):
        self.pattern = pattern
        self.attribute_name = attribute_name
        self.name = name
        self.view = view
        self.namespace = namespace
        self.urls = None

        self.creation_counter = URL.creation_counter
        URL.creation_counter += 1

    def as_url(self):
        return conf_url(
            self.pattern,
            self.get_view_function(**self.urls.get_view_kwargs(self.attribute_name)),
            name=self.get_view_name()
        )

    def get_view_function(self, **kwargs):
        if isinstance(self.view, type) and issubclass(self.view, View):  # CBV
            return self.view.as_view(**kwargs)
        else:  # Function
            return self.view

    def get_view_name(self):
        return self.name.format(
            **self.urls.get_view_name_fields(self.attribute_name)) if self.name else self.attribute_name

    def get_namespace(self):
        urls_namespace = self.urls.get_namespace()
        return urls_namespace if urls_namespace else self.namespace

    @property
    def reverse_name(self):
        namespace = self.get_namespace()
        if namespace is None:
            return self.name
        else:
            return '{ns}:{name}'.format(ns=namespace, name=self.get_view_name())


class URLsMeta(type):
    def __new__(mcs, name, bases, attrs):
        # Collect urls from current class.
        current_urls = []
        for key, value in list(attrs.items()):
            if isinstance(value, URL):
                value.attribute_name = key  # Set the base name to the attribute name
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
    namespace = None
    app_name = None

    def __init__(self, namespace=None, app_name=None):
        if namespace:
            self.namespace = namespace
        if app_name:
            self.app_name = app_name

        # base_urls is the *class*-wide definition of urls
        self.urls = copy.deepcopy(self.base_urls)
        for url in self.urls.values():
            url.urls = self

    def get_view_name_fields(self, name):
        return {}

    def get_view_kwargs(self, name):
        return {}

    def get_namespace(self):
        return self.namespace

    def get_app_name(self):
        return self.app_name

    def as_urls(self):
        return [url.as_url() for url in self.urls.values()]

    def as_include(self):
        return conf_include(
            self.as_urls(),
            app_name=self.get_app_name(),
            namespace=self.get_namespace()
        )


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
