from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils.safestring import mark_safe

from activities.models import Activity
from .utils import Calendar

# Create your views here.

STRAVA_API = settings.STRAVA_API


class CalendarView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Activity
    template_name = 'calendarapp/calendar.html'

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        qs = self.get_queryset()
        context = super().get_context_data(**kwargs)
        cal = Calendar(qs=qs, d=self.request.GET.get('month', None))  #  year=d.year, month=d.month)
        html_cal = cal.formatmonth(withyear=False)
        context['calendar'] = mark_safe(html_cal)
        context['cal'] = cal
        context['title'] = 'calendar'
        return context
