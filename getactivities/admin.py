from django.contrib import admin

from .models import GetActivitiesTask

# Register your models here.


class GetActivitiesTaskAdmin(admin.ModelAdmin):
    search_fields = ['name', 'active']

    class Meta:
        model = GetActivitiesTask


admin.site.register(GetActivitiesTask, GetActivitiesTaskAdmin)
