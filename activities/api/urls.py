from django.urls import path

from .views import SegmentStaringAPIToggle, RecentEffortsDataAPI, GetMapAPI

app_name = 'activities-api'

urlpatterns = [
    path('segment-staring/<int:segment_id>/', SegmentStaringAPIToggle.as_view(), name='SegmentStaringAPIToggle'),
    path('segment-data/<int:segment_id>/', RecentEffortsDataAPI.as_view(), name='SegmentDataAPI'),
    path('segment-map/<str:model_type>/<int:model_id>/', GetMapAPI.as_view(), name='SegmentMapAPI'),
]
