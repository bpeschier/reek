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

