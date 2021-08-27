from django.conf import settings
from django.contrib.auth.models import User

from celery import shared_task
from dateutil.relativedelta import relativedelta

from .models import ImportActivitiesTask, SyncActivitiesTask
from .utils import get_activities

STRAVA_API = settings.STRAVA_API


def _update_task_model(model=None):
    # today = datetime.utcnow().replace(tzinfo=pytz.utc)
    if model.frequency > 7:
        start_date = model.start_date + relativedelta(months=1)
        model.end_date = start_date + relativedelta(months=1)
    else:
        start_date = model.start_date + relativedelta(days=model.frequency)
        model.end_date = start_date + relativedelta(days=model.frequency)
    model.start_date = start_date
    model.save()


@shared_task
def import_activities_task(user=None):
    try:
        u = User.objects.get(pk=user)
        import_task = ImportActivitiesTask.objects.get(user=u)
        # if not fetch_task.active:
        #     fetch_task.disable_periodic_task()
        #     return "Task done!"
        get_activities(user=user, start_date=import_task.start_date, end_date=import_task.end_date)
        _update_task_model(import_task)
    except ImportActivitiesTask.DoesNotExist:
        return f"ERROR! User {user} task does not exist."


@shared_task
def get_activities_task(user=None):
    try:
        u = User.objects.get(pk=user)
        get_task = SyncActivitiesTask.objects.get(user=u)
        get_activities(user=user, start_date=get_task.start_date, end_date=get_task.end_date)
        _update_task_model(get_task)
    except SyncActivitiesTask.DoesNotExist:
        return f"ERROR! User {user} task does not exist."
