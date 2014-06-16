URLconf
=======

Class-based URLs
----------------

.. code-block:: python

    # urls.py
    from urlconf import urls


    class ViewSet(urls.URLs):

        index = urls.URL(r'^$', ListView)
        create = urls.URL(r'^add/$', CreateView)
        detail = urls.URL(r'^(?P<pk>.+)/preview/$', DetailView)
        update = urls.URL(r'^(?P<pk>.+)/edit/$', UpdateView)
        delete = urls.URL(r'^(?P<pk>.+)/delete/$', DeleteView)

    urlpatterns = ViewSet().as_urls()


Dynamic urls
------------

.. code-block:: python

    # models.py
    from django.db import models

    from urlconf.models import BasePage


    class Page(BasePage):
        pass


    class ContentPage(models.Model):
        title = models.CharField(max_length=255)
        slug = models.SlugField(max_length=255)
        content = models.TextField()


.. code-block:: python

    # views.py
    from urlconf.views import PageView, ApplicationView
    from urlconf.registry import registry

    from .models import ContentPage


    class ContentPageView(PageView):
        verbose_name = 'Simple content page'
        label = 'ContentPageView'
        model = ContentPage


    class HomePageView(PageView):
        template_name = 'pages/home.html'
        label = 'HomePageView'
        verbose_name = 'Home page'


    class TestApplicationView(ApplicationView):
        urlconf_name = 'testcms.test_urls'
        verbose_name = 'The test application'
        label = 'TestApplicationView'
        namespace = 'testapp'


    registry.register(ContentPageView)
    registry.register(HomePageView)
    registry.register(TestApplicationView)

.. code-block:: python

    # urls.py
    from urlconf.urls import page_urls
    from .models import Page

    urlpatterns = [
        # ...
        page_urls(Page),
    ]
