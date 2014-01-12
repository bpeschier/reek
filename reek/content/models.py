from django.db import models

from .plugins import plugins


class Region(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    plugin = models.CharField(max_length=127)
    shared_name = models.CharField(max_length=127, blank=True, unique=True, null=True, default=None)

    def render(self, context):
        plugin = plugins.get_by_name(self.plugin)
        return plugin.render(self, context)


