from django.db import models


class OrderableModel(models.Model):
    order = models.PositiveSmallIntegerField(editable=False)

    class Meta:
        abstract = True


