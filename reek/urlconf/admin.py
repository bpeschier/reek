from django.contrib import admin


class PageAdmin(admin.ModelAdmin):
    change_list_template = 'reek/urlconf/admin/page/change_list.html'


    class Media:
        css = {
            "all": ("reek/admin/page.css",)
        }
