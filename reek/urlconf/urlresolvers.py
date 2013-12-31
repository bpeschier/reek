from django.core.urlresolvers import ResolverMatch, Resolver404

from .views import registered_views


class BasePageResolver(object):
    def __init__(self, page_model, namespace=None, app_name=None):
        self.page_model = page_model
        self.namespace = namespace
        self.app_name = app_name

    def get_pages_for_path(self, slugs):
        """
        Finds pages for given slugs in the path.
        Ordered by length, so the deepest option is on top.
        """
        ancestor_paths = [u''] + [u'/'.join(slugs[:i + 1]) for i in range(len(slugs))]
        return self.page_model.objects.filter(path__in=ancestor_paths).order_by('-path')

    def resolve(self, path):
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
            kwargs = {
                'page': page,
                'slug': page_slug,
                'subpage_slugs': subpage_slugs,
            }
            return ResolverMatch(view, [], kwargs, app_name=self.app_name, namespaces=[self.namespace, ])
        except (self.page_model.DoesNotExist, IndexError):
            pass

        raise Resolver404({'tried': [], 'path': path})


def pages(page_model, app_name=None, namespace=None):
    return BasePageResolver(page_model)


def include_pages(page_model, app_name=None, namespace=None):
    return [pages(page_model, app_name, namespace)], app_name, namespace
