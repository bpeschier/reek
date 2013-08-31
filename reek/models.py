from django.db import models


class OrderableModel(models.Model):
    order = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True


