from collections import OrderedDict

from django.conf.urls import patterns, url
from django.views.generic.base import View

from .resolver import PageResolver


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

        self.creation_counter = URL.creation_counter
        URL.creation_counter += 1

    def as_url(self, name=None, name_kwargs=None, view_kwargs=None):
        name_kwargs = {} if name_kwargs is None else name_kwargs
        view_kwargs = {} if view_kwargs is None else view_kwargs

        name = name if self.name is None else self.name  # Use the overriden name if set
        name = name.format(**name_kwargs)
        return url(self.pattern, self.view.as_view(**view_kwargs), name=name)


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

    def get_view_name_kwargs(self):
        return {}

    def get_view_kwargs(self):
        return {}

    def as_urls(self):
        return patterns('', *[
            declared_url.as_url(
                name=name,
                view_kwargs=self.get_view_kwargs(),
                name_kwargs=self.get_view_name_kwargs()
            )
            for name, declared_url in self.declared_urls.items()
        ])


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


