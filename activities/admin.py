from django.contrib import admin

from .models import Activity, Map, Segment, SegmentEffort, StaredSegment, ActivityType


class SegmentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    list_display = ['name', 'updated']

    class Meta:
        model = Segment


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'start_date_local']
    list_filter = ['type', 'user']
    search_fields = ['name', 'type__name', 'id']

    class Meta:
        model = Activity


class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    readonly_fields = ('id',)


class SegmentEffortAdmin(admin.ModelAdmin):
    search_fields = ['id']

    class Meta:
        model = Segment


# Register your models here.
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityType, ActivityTypeAdmin)
admin.site.register(Map)
admin.site.register(StaredSegment)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(SegmentEffort, SegmentEffortAdmin)
