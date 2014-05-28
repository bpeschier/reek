from django.db import models

from .forms import RestructuredField as RestructuredFormField


class RestructuredField(models.TextField):
    def formfield(self, **kwargs):
        return RestructuredFormField(**kwargs)
