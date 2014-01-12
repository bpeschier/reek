from django.db import models

from .forms import RegionField as RegionFormField


class RegionField(models.OneToOneField):

    def __init__(self, shared_name=None, to_field=None, initial_plugin=None, **kwargs):
        from .models import Region
        self.initial_plugin = initial_plugin
        self.shared_name = shared_name
        super(RegionField, self).__init__(Region, to_field=to_field, **kwargs)

    def formfield(self, **kwargs):
        return RegionFormField(**kwargs)

    def pre_save(self, model_instance, add):
        self._ensure_region(model_instance)
        return super(RegionField, self).pre_save(model_instance, add)

    def save_form_data(self, instance, data):
        data = self._ensure_region(instance)
        super(RegionField, self).save_form_data(instance, data)

    #
    # Private functions
    #

    def _create_region(self):
        from .models import Region
        if self.shared_name:
            try:
                region = Region.objects.get(shared_name=self.shared_name)
            except Region.DoesNotExist:
                region = Region.objects.create()
        else:
            region = Region.objects.create()

        return region

    def _ensure_region(self, instance):
        if not getattr(instance, self.name, None):
            setattr(instance, self.name, self._create_region())
        return getattr(instance, self.name, None)
