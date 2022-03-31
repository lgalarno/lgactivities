from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    PeriodicTasks,
)
from django.utils import timezone

import pytz

from num2words import num2words
import json

# Create your models here.

TASK_FREQUENCY = (
    (1, 'Daily'),
    (7, 'Weekly'),
    (30, 'Monthly'),
)


class ImportActivitiesTask(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name="import_activities_task",
                                on_delete=models.CASCADE)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    to_date = models.DateTimeField(blank=True, null=True)
    frequency = models.IntegerField(choices=TASK_FREQUENCY[1:3], default=30)
    n_intervals = models.IntegerField(blank=True, null=True)
    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}. Active: {self.active}"

    def enable_periodic_task(self, save=True):
        task_name = f'user-{self.user.username}-import'
        if not self.periodic_task:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=1,
                period='hours'
            )
            obj, _ = PeriodicTask.objects.get_or_create(
                interval=schedule,
                kwargs=json.dumps({
                    'user': self.user.pk,
                    'get_type': 'import'
                }),
                name=task_name,
                task='getactivities.tasks.get_activities_task'
            )
            obj.enabled = True
            obj.save()
            PeriodicTasks.update_changed()
            self.periodic_task = obj
            if save:
                self.save()
        return self.periodic_task

    def disable_periodic_task(self, save=True):
        if self.periodic_task:
            obj = self.periodic_task
            obj.delete()
            PeriodicTasks.update_changed()
            self.periodic_task = None
            if save:
                self.save()
        return self.periodic_task


@receiver(models.signals.pre_save, sender=ImportActivitiesTask)
def set_periodic_task(sender, instance, **kwargs):
    """
    """
    if instance.active:
        if instance.start_date > instance.to_date:
            instance.active = False

    if instance.active and not instance.periodic_task:
        '''
        No periodic task and we just enabled it.
        '''
        instance.enable_periodic_task(save=False)

    if instance.periodic_task and not instance.active:
        '''
        Remove periodic task and we just enabled it.
        '''
        instance.disable_periodic_task(save=False)


class SyncActivitiesTask(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name="sync_activities_task",
                                on_delete=models.CASCADE)
    start_date = models.DateTimeField(blank=True, null=True)
    from_date = models.DateTimeField(blank=True, null=True)
    to_date = models.DateTimeField(blank=True, null=True)
    frequency = models.IntegerField(choices=TASK_FREQUENCY, default=7)
    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL)
    crontab = models.ForeignKey(CrontabSchedule, null=True, blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}. Active: {self.active}"

    def enable_periodic_task(self, save=True):
        # only when Active is changed
        if self.periodic_task:
            self.disable_periodic_task(save=True)
        task_name = f'{self.user.username}-sync'
        descr = task_name + f" will run "
        h = self.start_date.hour
        m = self.start_date.minute
        if self.frequency == 30:
            d = self.start_date.day
            schedule = CrontabSchedule(
                day_of_month=d,
            )
            descr = descr + f'monthly, each {num2words(d, to="ordinal_num")} of the month at '
        elif self.frequency == 7:
            schedule = CrontabSchedule(
                day_of_week=self.start_date.weekday() + 1,  # Monday, 00:00
            )
            descr = descr + f'weekly, each {self.start_date.strftime("%A")} at '
        elif self.frequency == 1:
            schedule = CrontabSchedule()
            descr = descr + f'daily, at '
        schedule.hour = h
        schedule.minute = m
        tz = self.user.time_zone
        if not tz:
            tz = 'UTC'
        sd = timezone.localtime(self.start_date, pytz.timezone(tz))
        descr = descr + f'{sd.strftime("%H:%M")}'
        schedule.timezone = tz
        schedule.save()

        # try:
        #     print('try')
        #     ct = self.crontab
        #     ct.delete()
        #     obj = PeriodicTask.objects.get(name=task_name)
        #     print('found')
        #     obj.crontab = schedule
        #
        #     # obj.kwargs=json.dumps({
        #     #         'user': self.user.pk,
        #     #         'get_type': 'sync'
        #     #     }),
        #     # obj.name = task_name
        #     # obj.task = 'getactivities.tasks.get_activities_task'
        #     # obj.description = descr
        #     # obj.enabled = True
        # except:
        #     print("new")

        # delete old crontab
        ct = self.crontab
        if ct:
            ct.delete()
        obj = PeriodicTask(name=task_name,
                           crontab=schedule,
                           )
        obj.kwargs = json.dumps({
                'user': self.user.pk,
                'get_type': 'sync'
            })
        obj.name = task_name
        obj.task = 'getactivities.tasks.get_activities_task'
        obj.description = descr
        obj.enabled = True
        obj.save()
        self.periodic_task = obj
        self.crontab = schedule
        PeriodicTasks.update_changed()
        if save:
            self.save()
        return self.periodic_task

    def disable_periodic_task(self, save=True):
        if self.periodic_task:
            obj = self.periodic_task
            obj.delete()
            PeriodicTasks.update_changed()
            self.periodic_task = None
            if save:
                self.save()
        return self.periodic_task


@receiver(models.signals.pre_save, sender=SyncActivitiesTask)
def set_periodic_task(sender, instance, **kwargs):
    """
    enable or disable periodic_task when a SyncActivitiesTask instance is saved
    """
    if instance.active:
        instance.enable_periodic_task(save=False)
    if not instance.active:
        instance.disable_periodic_task(save=False)


class Task_log(models.Model):
    sync_task = models.OneToOneField(to=SyncActivitiesTask,
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True)
    import_task = models.OneToOneField(to=ImportActivitiesTask,
                                       on_delete=models.CASCADE,
                                       blank=True,
                                       null=True)
    log = models.CharField(max_length=255, blank=True, null=True)
