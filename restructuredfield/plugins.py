from django.utils.translation import ugettext_lazy as _
from docutils.parsers.rst.directives.admonitions import Admonition


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Registry:
    def __init__(self):
        self._registry = {}

    def register(self, plugin_class):
        if plugin_class.label in self._registry:
            raise AlreadyRegistered(
                _('Plugin "%s" is already registered') % plugin_class.label
            )
        else:
            self._registry[plugin_class.label] = plugin_class

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('Plugin "%s" is not registered') % label)
        return self._registry[label]

    def get_plugins(self):
        return sorted(self._registry.values(), key=lambda x: x.name)

    def get_plugin_labels(self):
        return [
            (c.label, c.name) for c in self.get_views()
        ]


registry = Registry()
register = registry.register


class Plugin:
    directive = None
    editor_plugin = None


class AdmonitionPlugin(Plugin):
    directive = Admonition
    editor_plugin = 'content/plugins/admonition'


register(AdmonitionPlugin)