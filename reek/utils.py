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


class Pool(dict):
    def register(self, model):
        name = model.__name__
        if name in self:
            raise AlreadyRegistered("'{0}' already registered".format(name))
        else:
            self[name] = model

    def unregister(self, model):
        name = model.__name__
        if not name in self:
            raise NotRegistered("'{0}' not registered".format(name))
        else:
            del self[name]

    def get_by_name(self, name):
        try:
            return self[name]
        except KeyError:
            raise NotRegistered("'{0}' not registered".format(name))

