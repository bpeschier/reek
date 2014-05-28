from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_text

from .plugins import registry


class RestructuredWidget(forms.Widget):
    choices = []

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name, plugins=registry.get_plugins())
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        return render_to_string('restructuredfield/widgets/rstfield.html', final_attrs)

    @property
    def media(self):
        return forms.Media(
            js=('restructuredfield/js/require.js', ),
            css={
                'screen': ('restructuredfield/css/content-editor.css',),
            },
        )


class RestructuredField(forms.Field):
    widget = RestructuredWidget
    auto_id = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = RestructuredWidget()
