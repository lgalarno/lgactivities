from django.contrib.auth.decorators import login_required
from django.urls import path, include

from .views import (effort_details,
                    EffortDetailsView,
                    StaredSegmentsListView,
                    ActivityDetailsView
                    )

app_name = 'activities'

urlpatterns = [
    path('stared-segments/', login_required(StaredSegmentsListView.as_view()), name='stared-segments'),
    path('activity/<int:pk>/', ActivityDetailsView.as_view(), name='activity-details'),
    # path('activity/<int:activity_id>/effort/<int:effort_id>/', login_required(segment_details), name='segment_details'),
    # path('effort/<int:pk>/', login_required(effort_details), name='effort_details'),
    path('effort/<int:pk>/', EffortDetailsView.as_view(), name='effort_details'),
    path('api/', include('activities.api.urls', namespace="activities-api")),
]
