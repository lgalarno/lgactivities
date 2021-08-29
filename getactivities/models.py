from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    PeriodicTasks,
)

import json

# Create your models here.

TASK_FREQUENCY = (
    (1, 'Daily'),
    (7, 'Weekly'),
    (30, 'Monthly'),
)


class ImportActivitiesTask(models.Model):
    user = models.OneToOneField(User, related_name="import_activities_task", on_delete=models.CASCADE)
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
    user = models.OneToOneField(User, related_name="sync_activities_task", on_delete=models.CASCADE)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    frequency = models.IntegerField(choices=TASK_FREQUENCY, default=7)
    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}. Active: {self.active}"

    def enable_periodic_task(self, save=True):
        task_name = f'user-{self.user.username}-sync-'
        if self.periodic_task:
            self.disable_periodic_task(save=True)
        if self.frequency == 30:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                day_of_month=1
            )
            task_name = task_name + 'Monthly'
        elif self.frequency == 7:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                day_of_week=1 # Monday, 00:00
            )
            task_name = task_name + 'Weekly'
        elif self.frequency == 1:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                hour=0
            )
            task_name = task_name + 'Daily'
        obj, _ = PeriodicTask.objects.get_or_create(
            kwargs=json.dumps({
                'user': self.user.pk,
            }),
            crontab=schedule,
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


@receiver(models.signals.pre_save, sender=SyncActivitiesTask)
def set_periodic_task(sender, instance, **kwargs):
    """
    """
    if instance.active:
        '''
        No periodic task and we just enabled it.
        '''
        instance.enable_periodic_task(save=False)
    if not instance.active:
        '''
        Remove periodic task and we just enabled it.
        '''
        instance.disable_periodic_task(save=False)
