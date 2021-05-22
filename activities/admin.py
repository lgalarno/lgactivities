from django.contrib import admin

from .models import Activity, Map, Segment, SegmentEffort


# Register your models here.
admin.site.register(Activity)
admin.site.register(Map)
admin.site.register(Segment)
admin.site.register(SegmentEffort)
