from django import forms
from django.template.loader import render_to_string


class RegionWidget(forms.Widget):
    choices = []

    def __init__(self, **kwargs):
        self.region_field = kwargs.pop('region_field')
        super(RegionWidget, self).__init__(**kwargs)

    def render(self, name, value, attrs=None):
        context = {
            'name': name,
            'value': value,
            'plugin': self.region_field.initial_plugin
        }
        context.update(attrs)
        return render_to_string('reek/content/widgets/regionfield.html', context)

    @property
    def media(self):
        # TODO: list plugins for this one
        return forms.Media(
            js=('js/region-editor.js',)
        )


class RegionField(forms.Field):
    widget = RegionWidget
    auto_id = True

    def __init__(self, *args, **kwargs):
        self.region_field = kwargs.pop('region_field')
        kwargs['widget'] = self.widget(region_field=self.region_field)
        super(RegionField, self).__init__(*args, **kwargs)


