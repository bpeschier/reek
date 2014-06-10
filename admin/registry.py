from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class RegistryMixin:
    """
    Reusable registry
    """

    def __init__(self):
        super().__init__()
        self._registry = OrderedDict()

    def register(self, obj):
        if obj.label in self._registry:
            raise AlreadyRegistered(
                _('"%s" is already registered') % obj.label
            )
        else:
            self._registry[obj.label] = obj

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('"%s" is not registered') % label)
        return self._registry[label]

    def values(self):
        return self._registry.values()

    def keys(self):
        return self._registry.keys()

    def get_labels(self):
        return [
            (c.label, c.name) for c in self.values()
        ]

