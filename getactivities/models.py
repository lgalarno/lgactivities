from django.contrib.auth.models import User
from django.db import models

from django_celery_beat.models import (
    CrontabSchedule, # IntervalSchedule
    PeriodicTask,
    PeriodicTasks,
)

# Create your models here.

TASK_FREQUENCY = (
    (1, 'Daily'),
    (7, 'Weekly'),
    (30, 'Monthly'),
)

class GetActivitiesTask(models.Model):
    user = models.OneToOneField(User, related_name="get_activities_task", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    frequency = models.IntegerField(choices=TASK_FREQUENCY, default=7)
    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}. Active: {self.active}"
