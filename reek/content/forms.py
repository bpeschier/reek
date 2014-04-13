from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_text


class ContentWidget(forms.Widget):
    choices = []

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        return render_to_string('reek/content/widgets/contentfield.html', final_attrs)

    @property
    def media(self):
        return forms.Media(
            js=('content/js/content-editor.js',),
            css={
                'screen': ('content/css/content-editor.css',),
            },
        )


class ContentField(forms.Field):
    widget = ContentWidget
    auto_id = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = ContentWidget()


