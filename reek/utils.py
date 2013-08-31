import re

from unidecode import unidecode

from django.utils.functional import allow_lazy
from django.utils.safestring import mark_safe


@allow_lazy
def slugify(value):
    value = unidecode(value)
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return mark_safe(re.sub('[-\s]+', '-', value))


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Pool(object):
    def __init__(self):
        self._registry = {}  # name --> class

    def register(self, model):
        name = model.__name__
        if name in self._registry:
            raise AlreadyRegistered("'{0}' already registered".format(name))
        else:
            self._registry[name] = model

    def unregister(self, model):
        name = model.__name__
        if not name in self._registry:
            raise NotRegistered("'{0}' not registered".format(name))
        else:
            del self._registry[name]

    def get_by_name(self, name):
        try:
            name = str(name)
            return self._registry[name]
        except KeyError:
            raise NotRegistered("'{0}' not registered".format(name))
