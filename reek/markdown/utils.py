from collections import ChainMap


class Node(list):
    def __init__(self, *args):
        super().__init__(*args)
        self._parent = None
        self.attributes = {}
        self.context = ChainMap({})

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.context.maps = [self.context.maps[0], value.context]

    def __setitem__(self, key, value):
        value.parent = self
        super().__setitem__(key, value)


class Leaf:
    pass


class RootNode(Node):
    pass


class Text(Leaf):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return '"{}"'.format(self.text)


class TagNode(Node):
    def __init__(self, tag, *args):
        super().__init__(*args)
        self.tag = tag

    def __repr__(self):
        return '<{tag} {list}>'.format(tag=self.tag, list=super().__repr__())

