from django.urls import path

from .views import SegmentStaringAPIToggle, RecentEffortsDataAPI, GetMapDataAPI, RecentEffortsChartData

app_name = 'activities-api'

urlpatterns = [
    path('segment-staring/<int:segment_id>/', SegmentStaringAPIToggle.as_view(), name='SegmentStaringAPIToggle'),
    path('segment-data/<int:segment_id>/', RecentEffortsDataAPI.as_view(), name='SegmentDataAPI'),
    path('segment-chart-htmx/<int:segment_id>/', RecentEffortsChartData.as_view(), name='SegmentChartHTMX-API'),
    path('segment-map/<int:model_id>/', GetMapDataAPI.as_view(), name='GetMapDataAPI'),
]
