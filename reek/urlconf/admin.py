from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

class ResultTree(object):
    pass


class TreeChangeList(ChangeList):

    def __init__(self, *args, **kwargs):
        super(TreeChangeList, self).__init__(*args, **kwargs)

    def get_results(self, request):
        if not self.query_set.query.where:
            full_result_count = self.query_set.count()
        else:
            full_result_count = self.root_query_set.count()

        result_list = self.query_set._clone()

        self.result_count = full_result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.result_root = self.query_set._clone().first()
        self.can_show_all = True
        self.multi_page = False
        self.paginator = None


class PageAdmin(admin.ModelAdmin):
    change_list_template = 'reek/urlconf/admin/page/change_list.html'
    ordering = ('path', 'order',)

    def get_changelist(self, request, **kwargs):
        return TreeChangeList

    class Media:
        css = {
            "all": ("reek/admin/page.css",)
        }
