from django import forms
from django.template.loader import render_to_string


class ContentWidget(forms.Widget):
    choices = []

    def render(self, name, value, attrs=None):
        context = {
            'name': name,
            'value': value,
        }
        context.update(attrs)
        return render_to_string('reek/content/widgets/contentfield.html', context)

    @property
    def media(self):
        return forms.Media(
            js=('js/content-editor.js',)
        )


class ContentField(forms.Field):
    widget = ContentWidget
    auto_id = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = ContentWidget()


