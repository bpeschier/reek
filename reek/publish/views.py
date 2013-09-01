from django.http import Http404
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..urlconf.views import ContentMixin, ContentTemplateMixin, BasePageView


class PublishableContentMixin(ContentMixin):
    def get_content(self):
        """
        Get the latest published version of the content
        """
        content = super(PublishableContentMixin, self).get_content()
        perm = '%s.change_%s' % (self.model._meta.app_label, self.model._meta.model_name)
        version = self.request.GET.get('version', None) if self.request.user.has_perm(perm) else None

        if version:  # we are allowed to display a specific version
            try:
                return content.get_version(int(version)).object_version.object
            except models.ObjectDoesNotExist:
                raise Http404(_("Version %(version)s does not exist") % {'version': version, })
        elif not content.is_published:
            raise Http404(_("No published version for this %(verbose_name)s") %
                          {'verbose_name': self.model._meta.object_name})
        else:
            return content.published_version.object_version.object

    def get_context_data(self, **kwargs):
        """
        Insert version information
        """
        context = {
            'content_version': self.request.GET.get('version', None)
        }
        context.update(kwargs)
        return super(PublishableContentMixin, self).get_context_data(**context)


class PublishableContentView(ContentTemplateMixin, PublishableContentMixin, BasePageView):
    def get(self, request, *args, **kwargs):
        self.page = self.get_page()
        self.content = self.get_content()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
