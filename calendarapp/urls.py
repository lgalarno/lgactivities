from django.contrib.auth.decorators import login_required
from django.urls import path, include

from .views import (CalendarView
                    )

app_name = 'calendarapp'

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar_view'),
]
