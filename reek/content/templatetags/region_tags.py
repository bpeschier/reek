from django import template

register = template.Library()


class RegionRenderNode(template.Node):
    def __init__(self, region):
        self.region = region

    def render(self, context):
        return self.region.resolve(context).render(context)


class RegionAssignmentNode(template.Node):
    def __init__(self, region, target):
        self.region = region
        self.target = target

    def render(self, context):
        region = self.region.resolve(context)
        target = self.target.resolve(context)
        context[target] = region.plugin_set.all()
        return ''


def region(parser, token):
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) not in [2, 4] or (len(bits) == 4 and bits[-2] != 'as'):
        raise template.TemplateSyntaxError("'{0}' tag takes 2 arguments and optionally an assigment".format(tag_name))

    region_variable = template.Variable(bits[1])
    if len(bits) == 4:
        return RegionAssignmentNode(region_variable, template.Variable(bits[-1]))
    else:
        return RegionRenderNode(region_variable)
