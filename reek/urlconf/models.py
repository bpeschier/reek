from django.db import models
from django.utils.translation import ugettext_lazy as _

from .views import registered_views


class BasePage(models.Model):
    order = models.PositiveSmallIntegerField()  # XXX TODO should be editable=False

    # Reference to our view
    view_name = models.CharField(max_length=100, verbose_name=_('Page type'), blank=True)

    # Tree-fields
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    path = models.CharField(max_length=255, db_index=True, blank=True)

    # For menus
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Page /{path} pk={pk}>'.format(path=self.path, pk=self.pk)

    @property
    def slug(self):
        return self.path.split('/')[-1] if self.path else u''

    @property
    def view_class(self):
        return registered_views.get_by_name(self.view_name)

    def get_absolute_url(self):
        return '/{0}/'.format(self.path)
