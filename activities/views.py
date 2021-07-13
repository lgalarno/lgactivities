from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.utils.safestring import mark_safe

import requests

# from connections.utils import check_token, formaterror, get_token
from getactivities.utils import formaterror, get_token

from .models import Activity, Segment, SegmentEffort, Map, StaredSegment
from .utils import Calendar

# Create your views here.

STRAVA_API = settings.STRAVA_API
User = get_user_model()


class CalendarView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Activity
    template_name = 'activities/calendar.html'

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


#TODO CBV activity_details
class ActivityDetailsView(LoginRequiredMixin, DetailView):
    model = Activity
    template_name = 'activities/activity-details.html'

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['segments_efforts'] = self.object.get_all_segments()
        context['title'] = 'Activity'
        return context


def segment_details(request, activity_id, effort_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    this_effort = get_object_or_404(SegmentEffort, pk=effort_id)
    segment = get_object_or_404(Segment, pk=this_effort.segment_id)
    # e, access_token = check_token()
    e, access_token = get_token(user=request.user)
    if not e:
        header = {'Authorization': f'Bearer {access_token}'}
        param = {
        }
        url = f"{STRAVA_API['URLS']['athlete']}segments/{segment.id}"
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
            'staring': segment.is_stared(user=request.user),
            'title': 'segment details'
        }
        return render(request, 'activities/segment-details.html', context)
    elif access_token is None:
        request.session['nextpage'] = request.path
        return redirect('connections:requestcode')
    else:
        messages.warning(request, f'An error occurred while getting the segment: {e}')
        return HttpResponseRedirect('/')


class StaredSegmentsListView(LoginRequiredMixin, ListView):
    model = StaredSegment
    template_name = "activities/stared_segments.html"

    def get_queryset(self):
        return StaredSegment.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'stared segments'
        return context
