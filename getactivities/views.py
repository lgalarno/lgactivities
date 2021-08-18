from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import UpdateView

import requests
from datetime import datetime

from activities.models import Activity, Map, Segment, SegmentEffort

from profiles.models import StravaProfile

from .forms import GetActivitiesTaskForm
from .models import GetActivitiesTask
from .utils import formaterror, get_token

STRAVA_API = settings.STRAVA_API
# Create your views here.


class GetActivitiesTaskView(LoginRequiredMixin, UpdateView):
    model = GetActivitiesTask
    #form_class = GetActivitiesTaskForm
    template_name = 'getactivities/task-detail.html'
    fields = ['start_date', 'frequency', 'active']

    def get_form(self):
        form = super().get_form()
        form.fields['start_date'].widget = forms.DateInput(
            attrs={'type': 'date',
                   'value': datetime.today().date()
                   }
        )
        return form

    def get_object(self):
        obj, created = GetActivitiesTask.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        sid = StravaProfile.objects.get(user_id=self.request.user.pk)
        context['title'] = 'task'
        if sid.avatar:
            context['avatar'] = sid.avatar.url
        return context

    def get_success_url(self):
        return '/getactivities/task/'



def getactivities(request):
    if request.method == "POST":
        context = {}
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
        if start_date is None or end_date is None:
            raise Http404()
        e, access_token = get_token(user = request.user)
        if not e:
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'after': int(datetime.strptime(start_date,'%Y-%m-%d').timestamp()),
                'before': int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()),
            }
            url = f"{STRAVA_API['URLS']['athlete']}athlete/activities"
            e, activities = _requestStrava(url, headers, params, verify=False)
            if not e:
                for activity in activities:
                    a, created = Activity.objects.get_or_create(id=activity.get('id'), user=request.user)
                    a.name = activity.get('name')
                    a.type = activity.get('type')
                    a.start_date = activity.get('start_date')
                    a.start_date_local = activity.get('start_date_local')
                    a.save()
                    params = {}
                    url = f"{STRAVA_API['URLS']['athlete']}activities/{a.id}/?include_all_efforts=True"
                    e, activity_detailed = _requestStrava(url, headers, params, verify=False)
                    if not e:
                        print(activity_detailed)
                        m, created = Map.objects.get_or_create(activity=a)
                        m.polyline = activity_detailed.get('map').get('polyline')
                        m.save()
                        if "segment_efforts" in activity_detailed:
                            segment_efforts = activity_detailed.get("segment_efforts")
                            print(segment_efforts)
                            for se in segment_efforts:
                                print(se)
                                segment, created = Segment.objects.get_or_create(
                                    id=se.get('segment').get('id')
                                )
                                segment.name = se.get('segment').get('name')
                                segment.save()
                                # elements required for 'set_pr_rank' in models of SegmentEffort
                                obj, created = SegmentEffort.objects.get_or_create(
                                    id=se.get('id'),
                                    activity=a,
                                    segment=segment,
                                    elapsed_time=se.get('elapsed_time')
                                )
                                obj.start_date = se.get('start_date')
                                obj.start_date_local = se.get('start_date_local')
                                obj.distance = se.get('distance')
                                obj.save()
                        else:
                            messages.warning(request, f'An error occurred while getting the activity {a.id}: {e}')
                messages.success(request, f"{len(activities)} activities were entered into the database")
                return redirect('getactivities:getactivities')
            else:
                messages.warning(request, f'An error occurred while getting the activity: {e}')
        else:
            messages.warning(request, f'An error occurred while getting the activity: {e}')
            context = {
                'date_from': start_date,
                'date_to': end_date
            }
    else:
        latestactity = Activity.objects.filter(user=request.user).order_by('start_date').last()
        if latestactity:
            date_from = latestactity.start_date.strftime('%Y-%m-%d')
        else:
            date_from = '2011-04-23'
        context = {
            'date_from': date_from,
            'date_to': date_from
        }
    context['title'] = 'get-activity'
    return render(request, 'getactivities/get-getactivities.html', context)


def _requestStrava(url, headers, params, verify=False):
    e = False
    data = requests.get(url, headers=headers, params=params, verify=verify).json()
    if 'errors' in data:
        e = formaterror(data['errors'])
    return e, data
