from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..models import OrderableModel


class BasePage(OrderableModel):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    path = models.CharField(max_length=255, db_index=True, blank=True)
    title = models.CharField(max_length=255)

    # Reference to our view
    view_name = models.CharField(max_length=100)

    class Meta:
        abstract = True
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Page /{path} pk={pk}>'.format(path=self.path, pk=self.pk)

    @property
    def slug(self):
        return self.path.split(u'/')[-1] if self.path else u''
