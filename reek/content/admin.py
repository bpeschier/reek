from django.contrib import admin

from .fields import RegionField


class RegionAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, RegionField):
            kwargs.pop('request')
            kwargs['region_field'] = db_field
            return db_field.formfield(**kwargs)
        else:
            return super(RegionAdmin, self).formfield_for_dbfield(db_field, **kwargs)


