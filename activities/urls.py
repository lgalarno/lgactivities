from django.contrib.auth.decorators import login_required
from django.urls import path, include

from .views import (
    ActivityDetailsView,
    ActivityListView,
    EffortDetailsView,
    SegmentDetailsView,
    SegmentListView,
    StaredSegmentsListView
    )

app_name = 'activities'

urlpatterns = [
    path('stared-segments/', login_required(StaredSegmentsListView.as_view()), name='stared-segments'),
    path('activity-list/', login_required(ActivityListView.as_view()), name='activity-list'),
    path('activity/<int:pk>/', ActivityDetailsView.as_view(), name='activity-details'),
    path('segment/<int:pk>/', SegmentDetailsView.as_view(), name='segment-details'),
    path('segment-list/', login_required(SegmentListView.as_view()), name='segment-list'),
    # path('activity/<int:activity_id>/effort/<int:effort_id>/', login_required(segment_details), name='segment_details'),
    path('effort/<int:pk>/', EffortDetailsView.as_view(), name='effort_details'),
    path('api/', include('activities.api.urls', namespace="activities-api")),
]
