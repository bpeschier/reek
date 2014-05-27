from django import template

register = template.Library()


@register.inclusion_tag('menus/menu.html')
def menu_for(page, sublevels=2):
    return {
        'page': page,
        'sublevels': sublevels
    }

