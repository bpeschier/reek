from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django import forms

from .views import registered_views


class TreeChangeList(ChangeList):
    def __init__(self, *args, **kwargs):
        super(TreeChangeList, self).__init__(*args, **kwargs)

    def get_results(self, request):
        # XXX Not sure if we really want to override the paginator
        if not self.queryset.query.where:
            full_result_count = self.queryset.count()
        else:
            full_result_count = self.root_queryset.count()

        result_list = self.queryset._clone()

        self.result_count = full_result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.result_root = self.queryset._clone().first()
        self.can_show_all = True
        self.multi_page = False
        self.paginator = None


class PageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['view_name'].widget.choices = ((name, view.verbose_name) for (name, view) in
                                                   registered_views.items())

    class Meta:
        widgets = {
            'view_name': forms.Select
        }


class PageAdmin(admin.ModelAdmin):
    change_list_template = 'reek/urlconf/admin/page/change_list.html'
    ordering = ('path', 'order',)

    form = PageForm

    def get_changelist(self, request, **kwargs):
        return TreeChangeList

    class Media:
        css = {
            "all": ("reek/admin/page.css",)
        }
