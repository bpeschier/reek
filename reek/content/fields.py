from django.db import models

from .forms import ContentField as ContentFormField


class ContentField(models.TextField):
    def formfield(self, **kwargs):
        return ContentFormField(**kwargs)


