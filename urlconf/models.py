from django.db import models
from django.utils.translation import ugettext_lazy as _

from .registry import registry


class BasePage(models.Model):
    order = models.PositiveSmallIntegerField(
        editable=False
    )

    # Reference to our view
    view_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Page type')
    )

    # Tree-fields
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent')
    )
    path = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        verbose_name=_('Full path')
    )

    # For menus
    title = models.CharField(
        max_length=255,
        verbose_name=_('Page title')
    )

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
        return self.basename

    @property
    def basename(self):
        return self.path.split('/')[-1]

    @property
    def view_class(self):
        return registry.get(self.view_name)

    def get_absolute_url(self):
        return '/{0}/'.format(self.path)
