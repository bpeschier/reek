from .utils import Leaf


class HTML5Serialiser:
    def serialise(self, node):
        if isinstance(node, Leaf):
            return str(node)

        serialised_children = '\n'.join(self.serialise(child) for child in node)
        if hasattr(node, 'tag'):
            return '<{tag}>{children}</{tag}>'.format(tag=node.tag, children=serialised_children)
        else:
            return serialised_children

