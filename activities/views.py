from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.views.generic import ListView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

import json
import polyline
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
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['cal'] = cal
        # context['year'] = cal.year
        # context['next_year'] = next_year(d)
        # context['prev_year'] = prev_year(d)
        # context['prev_month'] = prev_month(d)
        # context['next_month'] = next_month(d)
        return context


def activity_details(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    segments_efforts = activity.get_all_segments()
    activity_map = polyline.decode(activity.map.polyline)

    if activity.start_lat and activity.start_lng:
        center = activity.get_center  #  f'[{activity.start_lat}, {activity.start_lng}]'
    else:
        center = '[46.87591, -71.28951]'
    context = {
        'activity': activity,
        'center': center,
        'segments_efforts': segments_efforts,
        'coord': json.dumps(activity_map),
        'title': 'Activity'
    }
    return render(request, 'activities/activity-details.html', context)


def segment_details(request, activity_id, effort_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    this_effort = get_object_or_404(SegmentEffort, pk=effort_id)
    segment = get_object_or_404(Segment, pk=this_effort.segment_id)
    if not segment.has_map:
        e, access_token = check_token()
        if e is True:
            header = {'Authorization': f'Bearer {access_token}'}
            param = {
            }
            url = f"{settings.STRAVA_URLS['athlete']}segments/{segment.id}"
            segment_detail = requests.get(url, headers=header, params=param, verify=False).json()
            # print(segment_detail)
            if 'errors' in segment_detail:
                e = formaterror(segment_detail['errors'])
                messages.warning(request, f'An error occurred while getting the segment: {e}')
                return HttpResponseRedirect('/')
            else:
                m = Map(
                    segment=segment,
                    polyline=segment_detail['map']['polyline'],
                )
                m.save()

                segment.start_lat = segment_detail['start_latlng'][0]
                segment.start_lng = segment_detail['start_latlng'][1]
                segment.save()

    segment_map = polyline.decode(segment.map.polyline)
    efforts = segment.get_all_efforts()
    if segment.start_lat and segment.start_lng:
        center = f'[{segment.start_lat}, {segment.start_lng}]'
    else:
        center = '[46.87591, -71.28951]'
    context = {
        'activity': activity,
        'this_effort': this_effort,
        'segment': segment,
        'efforts': efforts,
        'center': center,
        'coord': json.dumps(segment_map),
        'title': 'Efforts'
    }
    return render(request, 'activities/segment-details.html', context)


class SegmentStaringAPIToggle(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, segment_id=None, format=None):
        obj = get_object_or_404(Segment, pk=segment_id)
        print(obj.staring)
        s = obj.staring
        if s:
            obj.staring = False
            staring = False
        else:
            obj.staring = True
            staring = True
        obj.save()
        data = {
            'staring': staring
        }
        return Response(data)
