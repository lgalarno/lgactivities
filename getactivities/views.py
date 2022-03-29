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
import pytz

from activities.models import Activity

# from profiles.models import StravaProfile

from .models import ImportActivitiesTask, SyncActivitiesTask
from .utils import formaterror, get_activities

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
            attrs={'type': 'date',
                   'min': datetime.today().date()
                   }
        )
        return form

    def form_valid(self, form):
        instance = form.save(commit=False)
        now = datetime.now().replace(microsecond=0)
        instance.start_date = instance.start_date.combine(instance.start_date, now.time()) + relativedelta(hours=+1)
        instance.to_date = instance.start_date
        if instance.frequency == 30:
            if instance.start_date.day > 28:
                #TODO send message in js if dom >28 and frequency == 30
                messages.error(self.request, "Since the day of month is > 28, we adjusted the task to run on the 28th of each month. Note that the next synchronisation will only happen next month. You may want to change the starting date.")
                sd = instance.start_date + relativedelta(months=+1)
                instance.start_date = sd.replace(day=28)
                instance.to_date = instance.start_date

            #instance.start_date = datetime(instance.start_date.year, instance.start_date.month, day=1)
            instance.from_date = instance.start_date + relativedelta(months=-1)
            # instance.end_date = instance.start_date + relativedelta(months=1)
        elif instance.frequency == 7:
            # set the start date to the previous Monday (datetime day 0)
            #d = instance.start_date.weekday()
            #instance.start_date = instance.start_date + relativedelta(days=-d)
            instance.from_date = instance.start_date + relativedelta(weeks=-1)
        elif instance.frequency == 1:
            instance.from_date = instance.start_date + relativedelta(days=-1)
            # instance.end_date = instance.start_date + relativedelta(days=instance.frequency)
        m = ''
        if instance.active:
            # m = f"The first run is schedule on {instance.end_date.strftime('%Y-%m-%d')} at 00:00h " \
            #     f"to get activities from  {instance.start_date.strftime('%Y-%m-%d')} to " \
            #     f"{(instance.end_date + relativedelta(days=-1)).strftime('%Y-%m-%d')}"
            m = f"The first run is schedule on {instance.start_date.strftime('%Y-%m-%d')} at {instance.start_date.strftime('%H:%M:%S')} " \
                f"to get activities from {instance.from_date.strftime('%Y-%m-%d')} to " \
                f"{instance.to_date.strftime('%Y-%m-%d')}"
        messages.success(self.request, f"Your task has been registered. {m}")
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
    else:
        latestactity = Activity.objects.filter(user=request.user).order_by('start_date').last()
        if latestactity:
            date_from = (latestactity.start_date + relativedelta(days=1)).strftime('%Y-%m-%d')
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
