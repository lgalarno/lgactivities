from django.contrib import admin

from .models import ImportActivitiesTask, SyncActivitiesTask, TaskLog

# Register your models here.


class ImportActivitiesTaskAdmin(admin.ModelAdmin):
    search_fields = ['user', 'active']

    class Meta:
        model = ImportActivitiesTask


class SyncActivitiesTaskAdmin(admin.ModelAdmin):
    search_fields = ['user', 'active']

    class Meta:
        model = SyncActivitiesTask


admin.site.register(ImportActivitiesTask, ImportActivitiesTaskAdmin)
admin.site.register(SyncActivitiesTask, SyncActivitiesTaskAdmin)
admin.site.register(TaskLog)
