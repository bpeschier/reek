from django.utils.translation import ugettext_lazy as _


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Registry:
    def __init__(self):
        self._registry = {}

    def register(self, view_class):
        if view_class.label in self._registry:
            raise AlreadyRegistered(
                _('View "%s" is already registered') % view_class.label
            )
        else:
            self._registry[view_class.label] = view_class

    def get(self, label):
        if label not in self._registry:
            raise NotRegistered(_('View "%s" is not registered') % label)
        return self._registry[label]

    def get_views(self):
        return sorted(self._registry.values(), key=lambda x: x.name)

    def get_view_labels(self):
        return [
            (c.label, c.name) for c in self.get_views()
        ]


registry = Registry()
register = registry.register