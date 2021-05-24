from django.contrib import admin

from .models import Activity, Map, Segment, SegmentEffort


class SegmentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    list_display = ['name', 'has_map']

    class Meta:
        model = Segment


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']
    search_fields = ['name', 'type', 'id']

    class Meta:
        model = Activity


class SegmentEffortAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']

    class Meta:
        model = Segment


# Register your models here.
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Map)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(SegmentEffort, SegmentEffortAdmin)
