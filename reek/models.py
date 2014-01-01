from django.db import models


class OrderableModel(models.Model):
    order = models.PositiveSmallIntegerField()  # XXX TODO should be editable=False

    class Meta:
        abstract = True


