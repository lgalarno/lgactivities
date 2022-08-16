from django.urls import path
from django.views.decorators.cache import cache_page

from .views import CalendarView

app_name = 'calendarapp'

urlpatterns = [
    path('', cache_page(600)(CalendarView.as_view()), name='calendar_view'),
]
