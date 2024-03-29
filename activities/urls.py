from django.contrib.auth.decorators import login_required
from django.urls import path, include

from activities import views

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
    path('stared-segments/', StaredSegmentsListView.as_view(), name='stared-segments'),
    path('activity-list/', ActivityListView.as_view(), name='activity-list'),
    path('activity/<int:pk>/', ActivityDetailsView.as_view(), name='activity-details'),
    path('refresh-activity/<int:pk>/', login_required(views.refresh_activity), name='refresh-activity'),
    path('segment/<int:pk>/', SegmentDetailsView.as_view(), name='segment-details'),
    path('segment-list/', SegmentListView.as_view(), name='segment-list'),
    path('effort/<int:pk>/', EffortDetailsView.as_view(), name='effort_details'),
    path('fit-file-utils/', views.fit_file_utils, name='fit_file_utils'),
    path('api/', include('activities.api.urls', namespace="activities-api")),
]
