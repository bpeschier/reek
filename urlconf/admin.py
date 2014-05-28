from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django import forms

from .registry import registry


class PageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)

        # Fetch registered views to show
        self.fields['view_name'].widget.choices = registry.get_view_labels()

    class Meta:
        widgets = {
            'view_name': forms.Select
        }


