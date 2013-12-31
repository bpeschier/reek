from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from reversion.admin import VersionAdmin

#
# TODO:
# - temporary reverted to pre-1.6 model_name
#


class PublishAdmin(VersionAdmin):
    def get_model_perms(self, request):
        perms = super(PublishAdmin, self).get_model_perms(request)
        perms.update({
            'publish': self.has_publish_permission(request),
            'request_publish': self.has_request_publish_permission(request),
        })
        return perms

    def get_list_display(self, request):
        display = super(PublishAdmin, self).get_list_display(request)
        can_publish = self.has_publish_permission(request)
        can_request = self.has_request_publish_permission(request)

        def is_published(obj):
            context = {
                'instance': obj,
                'can_publish': can_publish,
                'can_request': can_request,
            }

            return render_to_string('reek/publish/admin/list_state.html', context)

        is_published.allow_tags = True
        is_published.short_description = _('Published')

        def publish_actions(obj):
            suffix = u'{app}_{module}'.format(app=obj._meta.app_label, module=obj._meta.model_name)
            context = {
                'instance': obj,
                'can_publish': can_publish,
                'can_request': can_request,
                'request_url': reverse("admin:publishable_request_publish_%s" % suffix, kwargs={'pk': obj.pk}),
                'publish_url': reverse("admin:publishable_publish_%s" % suffix, kwargs={'pk': obj.pk}),
                'unpublish_url': reverse("admin:publishable_unpublish_%s" % suffix, kwargs={'pk': obj.pk}),
                'review_url': reverse("admin:publishable_review_%s" % suffix, kwargs={'pk': obj.pk}),
            }
            return render_to_string('reek/publish/admin/actions.html', context)

        publish_actions.allow_tags = True
        publish_actions.short_description = ''

        def latest_version(obj):
            return obj.latest_version.id if obj.latest_version else _('Unknown')

        latest_version.short_description = _('Latest')

        return tuple(list(display) + [latest_version, is_published, publish_actions])

    def has_publish_permission(self, request):
        return request.user.has_perm(self.opts.app_label + '.can_publish')

    def has_request_publish_permission(self, request):
        return request.user.has_perm(self.opts.app_label + '.can_request')

    #
    # URLS and Views
    #

    def get_urls(self):
        urls = super(PublishAdmin, self).get_urls()
        suffix = u'{app}_{module}'.format(app=self.model._meta.app_label, module=self.model._meta.model_name)
        publish_urls = patterns(
            '',
            url(r'^publish/(?P<pk>(\d+))/$', self.admin_site.admin_view(self.publish_view),
                name="publishable_publish_%s" % suffix),
            url(r'^review/(?P<pk>(\d+))/$', self.admin_site.admin_view(self.review_view),
                name="publishable_review_%s" % suffix),
            url(r'^unpublish/(?P<pk>(\d+))/$', self.admin_site.admin_view(self.unpublish_view),
                name="publishable_unpublish_%s" % suffix),
            url(r'^request/(?P<pk>(\d+))/$', self.admin_site.admin_view(self.request_view),
                name="publishable_request_publish_%s" % suffix),
        )
        return publish_urls + urls

    def review_view(self, request, pk=None):
        """
        Naively assume the object has an `get_absolute_url` and use it to review the requested version.
        """
        instance = self.model.objects.get(pk=pk)
        if self.has_publish_permission(request) and instance.is_requested:
            return HttpResponseRedirect(
                u'{url}?version={version}'.format(
                    url=instance.get_absolute_url(),
                    version=instance.requested_version.id))
        else:
            return HttpResponseNotAllowed('Go away')

    def request_view(self, request, pk=None):
        instance = self.model.objects.get(pk=pk)
        if self.has_request_publish_permission(request) and not instance.is_requested:
            instance.request_publish(request.user)
            messages.add_message(
                request, messages.INFO,
                '{model} is requested for publish'.format(model=self.model._meta.verbose_name))
            info = (self.model._meta.app_label, self.model._meta.model_name)
            redirect = reverse('admin:%s_%s_changelist' % info)
            return HttpResponseRedirect(redirect)
        else:
            return HttpResponseNotAllowed('Go away')

    def publish_view(self, request, pk=None):
        instance = self.model.objects.get(pk=pk)
        if self.has_publish_permission(request) and instance.is_publishable:
            instance.publish(request.user)
            messages.add_message(
                request, messages.INFO,
                '{model} was published'.format(model=self.model._meta.verbose_name))
            info = (self.model._meta.app_label, self.model._meta.model_name)
            redirect = reverse('admin:%s_%s_changelist' % info)
            return HttpResponseRedirect(redirect)
        else:
            return HttpResponseNotAllowed('Go away')

    def unpublish_view(self, request, pk=None):
        instance = self.model.objects.get(pk=pk)
        if self.has_publish_permission(request) and instance.is_published:
            instance.unpublish()
            messages.add_message(
                request, messages.INFO,
                '{model} is no longer published'.format(model=self.model._meta.verbose_name))
            info = (self.model._meta.app_label, self.model._meta.model_name)
            redirect = reverse('admin:%s_%s_changelist' % info)
            return HttpResponseRedirect(redirect)
        else:
            return HttpResponseNotAllowed('Go away')


