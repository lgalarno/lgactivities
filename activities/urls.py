from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'activities'

urlpatterns = [
    path('', login_required(views.CalendarView.as_view()), name='calendar'),
    path('activity/<int:activity_id>/', login_required(views.activity_details), name='activity-details'),
    path('activity/<int:activity_id>/segment/<int:effort_id>/', login_required(views.segment_details), name='segment_details'),
    path('activity/segment/<int:segment_id>/api/', views.SegmentStaringAPIToggle.as_view(), name='SegmentStaringAPIToggle'),
]
