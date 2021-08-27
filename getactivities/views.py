from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import UpdateView

import math
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

from activities.models import Activity, Map, Segment, SegmentEffort

from profiles.models import StravaProfile

# from .forms import GetActivitiesTaskForm
from .models import ImportActivitiesTask, SyncActivitiesTask
from .utils import formaterror, get_token, get_activities

STRAVA_API = settings.STRAVA_API

# Create your views here.


class SyncActivitiesTaskView(LoginRequiredMixin, UpdateView):
    model = SyncActivitiesTask
    template_name = 'getactivities/get-activities-task.html'
    fields = ['start_date', 'frequency', 'active']

    def get_object(self):
        obj, created = SyncActivitiesTask.objects.get_or_create(user=self.request.user)
        if created:
            obj.start_date = datetime.today().date()
        return obj

    def get_form(self):
        form = super().get_form()
        form.fields['start_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )
        return form

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.frequency > 7:
            instance.end_date = instance.start_date + relativedelta(months=1)
        else:
            instance.end_date = instance.start_date + relativedelta(days=instance.frequency)
        messages.success(self.request, "Your task has been registered.")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        sid = StravaProfile.objects.get(user_id=self.request.user.pk)
        context['title'] = 'get-task'

        if sid.avatar:
            context['avatar'] = sid.avatar.url
        return context

    def get_success_url(self):
        return '/getactivities/sync-task/'


class ImportActivitiesTaskView(LoginRequiredMixin, UpdateView):
    model = ImportActivitiesTask
    template_name = 'getactivities/import-activities-task.html'
    fields = ['start_date', 'to_date', 'frequency', 'active']

    def get_object(self):
        obj, created = ImportActivitiesTask.objects.get_or_create(user=self.request.user)
        if created:
            obj.to_date = datetime.today().date()
            obj.start_date = datetime.today().date()
        return obj

    def get_form(self):
        form = super().get_form()
        form.fields['start_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )
        form.fields['to_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )
        return form

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.start_date > instance.to_date:
            form.add_error('start_date', 'The Start date should be before the To date')
            return self.form_invalid(form)
        else:
            if instance.frequency > 7:
                instance.end_date = instance.start_date + relativedelta(months=1)
                dt = relativedelta(instance.to_date, instance.start_date)
                n = dt.years * 12 + dt.months + (dt.days > 0) +1
            else:
                instance.end_date = instance.start_date + relativedelta(days=instance.frequency)
                dt = (instance.to_date - instance.start_date).days
                n = math.ceil(dt / 7) + 1

            #dt = relativedelta(instance.to_date, instance.start_date)
            instance.n_intervals = n
            m = f'Your data will be available in {n} hours'
            if not instance.active:
                m = m + ' when active'
            messages.success(self.request, m)
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        sid = StravaProfile.objects.get(user_id=self.request.user.pk)
        context['title'] = 'import-task'

        if sid.avatar:
            context['avatar'] = sid.avatar.url
        return context

    def get_success_url(self):
        return '/getactivities/import-task/'


def getactivities(request):
    context = {
        'title': 'get-activities',
        'date_from': request.POST.get('start_date', None),
        'date_to': request.POST.get('end_date', None)
    }
    if request.method == "POST":
        start_date = datetime.strptime(context['date_from'], '%Y-%m-%d')
        end_date = datetime.strptime(context['date_to'], '%Y-%m-%d')
        if context['date_from'] is None or context['date_to'] is None:
            raise Http404()

        m = get_activities(user=request.user, start_date=start_date, end_date=end_date)
        messages.success(request, m)
        return redirect('getactivities:getactivities')
        # e, access_token = get_token(user=request.user)
        # if not e:
        #     """
        #     get activities
        #     """
        #     headers = {'Authorization': f'Bearer {access_token}'}
        #     params = {
        #         # 'after': int(datetime.strptime(context['date_from'], '%Y-%m-%d').timestamp()),
        #         # 'before': int(datetime.strptime(context['date_to'], '%Y-%m-%d').timestamp()),
        #         'after': int(start_date.timestamp()),
        #         'before': int(end_date.timestamp()),
        #     }
        #     url = f"{STRAVA_API['URLS']['athlete']}athlete/activities"
        #     e, activities = _requestStrava(url, headers, params, verify=False)
        #     if not e:
        #         for activity in activities:
        #             a, created = Activity.objects.get_or_create(id=activity.get('id'), user=request.user)
        #             a.name = activity.get('name')
        #             a.type = activity.get('type')
        #             a.start_date = activity.get('start_date')
        #             a.start_date_local = activity.get('start_date_local')
        #             a.save()
        #             params = {}
        #             """
        #             get activity detailed
        #             """
        #             url = f"{STRAVA_API['URLS']['athlete']}activities/{a.id}/?include_all_efforts=True"
        #             e, activity_detailed = _requestStrava(url, headers, params, verify=False)
        #             if not e:
        #                 m, created = Map.objects.get_or_create(activity=a)
        #                 m.polyline = activity_detailed.get('map').get('polyline')
        #                 m.save()
        #                 if "segment_efforts" in activity_detailed:
        #                     segment_efforts = activity_detailed.get("segment_efforts")
        #                     for se in segment_efforts:
        #                         segment, created = Segment.objects.get_or_create(
        #                             id=se.get('segment').get('id')
        #                         )
        #                         segment.name = se.get('segment').get('name')
        #                         segment.save()
        #                         # elements required for 'set_pr_rank' in models of SegmentEffort
        #                         obj, created = SegmentEffort.objects.get_or_create(
        #                             id=se.get('id'),
        #                             activity=a,
        #                             segment=segment,
        #                             elapsed_time=se.get('elapsed_time')
        #                         )
        #                         obj.start_date = se.get('start_date')
        #                         obj.start_date_local = se.get('start_date_local')
        #                         obj.distance = se.get('distance')
        #                         obj.save()
        #             else:
        #                 messages.warning(request, f'An error occurred while getting the activity {a.id}: {e}')
        #         messages.success(request, f"{len(activities)} activities were entered into the database")
        #         return redirect('getactivities:getactivities')
        # messages.warning(request, f'An error occurred while getting the activities: {e}')
    else:
        latestactity = Activity.objects.filter(user=request.user).order_by('start_date').last()
        if latestactity:
            date_from = latestactity.start_date.strftime('%Y-%m-%d')
        else:
            date_from = '2011-04-23'
        context['date_from'] = date_from
        context['date_to'] = date_from
    return render(request, 'getactivities/get-getactivities.html', context)


def _requestStrava(url, headers, params, verify=False):
    e = False
    data = requests.get(url, headers=headers, params=params, verify=verify).json()
    if 'errors' in data:
        e = formaterror(data['errors'])
    return e, data
