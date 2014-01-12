from ..utils import Pool


class PluginPool(Pool):
    pass


plugins = PluginPool()


class Plugin(object):
    def render(self, region, context):
        raise NotImplementedError


class RichTextPlugin(object):
    def render(self, region, context):
        raise NotImplementedError


plugins.register(RichTextPlugin)


