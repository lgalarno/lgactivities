from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.utils.safestring import mark_safe

import requests

from connections.utils import check_token, formaterror
from .models import Activity, Segment, SegmentEffort, Map
from .utils import Calendar, get_date

# Create your views here.

STRAVA_API = settings.STRAVA_API


class CalendarView(ListView):
    login_url = 'login'
    model = Activity
    template_name = 'activities/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=False)
        context['calendar'] = mark_safe(html_cal)
        context['cal'] = cal
        context['title'] = 'calendar'
        return context


def activity_details(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    segments_efforts = activity.get_all_segments()
    context = {
        'activity': activity,
        'segments_efforts': segments_efforts,
        'title': 'Activity'
    }
    return render(request, 'activities/activity-details.html', context)


def segment_details(request, activity_id, effort_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    this_effort = get_object_or_404(SegmentEffort, pk=effort_id)
    segment = get_object_or_404(Segment, pk=this_effort.segment_id)

    e, access_token = check_token()
    if not e:
        header = {'Authorization': f'Bearer {access_token}'}
        param = {
        }
        url = f"{settings.STRAVA_URLS['athlete']}segments/{segment.id}"
        segment_detail = requests.get(url, headers=header, params=param, verify=False).json()
        if 'errors' in segment_detail:
            e = formaterror(segment_detail['errors'])
            messages.warning(request, f'An error occurred while getting the segment: {e}')
            return HttpResponseRedirect('/')
        else:
            if not segment.updated:
                m, created = Map.objects.get_or_create(
                                      segment=segment)
                if created:
                    m.polyline = segment_detail['map']['polyline']
                    m.save()
                segment = segment.update_from_strava(segment_detail=segment_detail)

    efforts = segment.get_all_efforts()
    context = {
        'activity': activity,
        'this_effort': this_effort,
        'segment': segment,
        'efforts': efforts,
        'title': 'segment details'
    }
    return render(request, 'activities/segment-details.html', context)


class StaredSegmentsListView(ListView):
    model = Segment
    template_name = "activities/stared_segments.html"

    def get_queryset(self):
        return Segment.objects.filter(staring=True)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'stared segments'
        return context
