from itertools import dropwhile
import datetime

from django.db import models
from django.db.models.base import ModelBase
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from reversion.models import Revision
import reversion


class PublishState(models.Model):
    revision = models.OneToOneField(Revision)

    date_requested = models.DateTimeField(null=True)
    user_requested = models.ForeignKey(User, related_name='publishstate_requested', null=True)

    date_published = models.DateTimeField(null=True)
    user_published = models.ForeignKey(User, null=True)

    class Meta:
        ordering = ["date_published", "date_requested"]
        verbose_name = _('Publish state')
        verbose_name_plural = _('Publish states')


class PublishableBase(ModelBase):
    def __new__(mcs, name, bases, attrs):
        # Make sure we are registered
        follow = attrs.pop('version_follow', [])
        kls = super(PublishableBase, mcs).__new__(mcs, name, bases, attrs)
        if not kls._meta.abstract and not reversion.is_registered(kls):
            reversion.register(kls, follow=follow)
        return kls


class Publishable(models.Model):
    __metaclass__ = PublishableBase

    version_follow = []  # Follow these FK's when saving this object

    class Meta:
        abstract = True
        permissions = (
            ('can_request', _('Can request object to be published')),
            ('can_publish', _('Can publish object')),
        )

    def publish(self, user):
        # Get latest revision and mark as published
        versions = reversion.get_for_object(self)
        if versions:
            revision = versions[0].revision
            published_version = self.published_version
            state, created = PublishState.objects.get_or_create(revision=revision)
            state.date_published = datetime.datetime.utcnow().replace(tzinfo=utc)
            state.user_published = user
            state.save()

            if published_version:
                self.clean_before(published_version.revision)

    def request_publish(self, user):
        # Get latest revision and mark as published
        versions = reversion.get_for_object(self)
        if versions:
            revision = versions[0].revision
            state, created = PublishState.objects.get_or_create(revision=revision)
            state.date_requested = datetime.datetime.utcnow().replace(tzinfo=utc)
            state.user_requested = user
            state.save()

    def unpublish(self):
        # Get the latest revision marked as published and remove it
        version = self.published_version

        if version is not None:
            version.revision.publishstate.delete()

    @property
    def state(self):
        state = getattr(self, '_state', None)
        if not state:
            self._state = reversion.get_for_object(self).filter(revision__publishstate__date_published__isnull=False)[0]
        return self._state

    @property
    def published_version(self):
        version = getattr(self, '_published_version', None)
        if version is None:
            self._published_version = self._get_published_version()
        return self._published_version

    @property
    def requested_version(self):
        version = getattr(self, '_requested_version', None)
        if version is None:
            self._requested_version = self._get_requested_version()
        return self._requested_version

    @property
    def latest_version(self):
        version = getattr(self, '_latest_version', None)
        if version is None:
            self._latest_version = reversion.get_for_object(self)[0]
        return self._latest_version

    def get_version(self, version_id):
        return reversion.get_for_object(self).get(id=version_id)

    def _get_published_version(self):
        try:
            version = reversion.get_for_object(self).filter(
                revision__publishstate__date_published__isnull=False)[0]
        except IndexError:
            version = None
        return version

    def _get_requested_version(self):
        try:
            version = reversion.get_for_object(self).filter(
                revision__publishstate__date_published__isnull=True,
                revision__publishstate__date_requested__isnull=False)[0]
        except IndexError:
            version = None
        return version

    @property
    def is_publishable(self):
        try:
            version = reversion.get_for_object(self)[0]
            state = version.revision.publishstate
            can_publish = state.date_published is None
        except PublishState.DoesNotExist:
            can_publish = True
        except IndexError:
            can_publish = False
        return can_publish

    @property
    def is_requestable(self):
        try:
            version = reversion.get_for_object(self)[0]
            state = version.revision.publishstate
            can_request = state.date_requested is None and state.date_published is None
        except PublishState.DoesNotExist:
            can_request = True
        except IndexError:
            can_request = False
        return can_request

    @property
    def is_published(self):
        return self.published_version is not None

    @property
    def date_published(self):
        if self.published_version is not None:
            return self.published_version.revision.publishstate.date_published

    @property
    def is_requested(self):
        return self.requested_version is not None

    @property
    def date_requested(self):
        if self.requested_version is not None:
            return self.requested_version.revision.publishstate.date_requested

    def has_publish_permission(self, request):
        return request.user.has_perm(self._meta.app_label + '.can_publish')

    def has_request_publish_permission(self, request):
        return request.user.has_perm(self._meta.app_label + '.can_request')

    def clean_before(self, revision):
        """
        Removes all versions before given revision.

        Used to keep the amount of revisions in the database low by
        removing all versions before the last published version
        """
        versions = reversion.get_for_object(self)
        old_versions = dropwhile(
            lambda v: v.revision.pk == revision.pk,
            dropwhile(
                lambda v: v.revision.pk != revision.pk,
                versions
            )
        )

        for version in old_versions:
            version.revision.delete()

