from django.contrib.auth.decorators import login_required
from django.urls import path, include

from .views import (CalendarView,
                    activity_details,
                    segment_details,
                    )


app_name = 'activities'

urlpatterns = [
    path('', login_required(CalendarView.as_view()), name='calendar'),
    path('activity/<int:activity_id>/', login_required(activity_details), name='activity-details'),
    path('activity/<int:activity_id>/segment/<int:effort_id>/', login_required(segment_details), name='segment_details'),
    path('api/', include('activities.api.urls', namespace="activities-api")),
]
