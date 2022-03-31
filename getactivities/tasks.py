from django.conf import settings
from django.contrib.auth import get_user_model

from celery import shared_task
from dateutil.relativedelta import relativedelta

from .models import ImportActivitiesTask, SyncActivitiesTask
from .utils import get_activities

User = get_user_model()
STRAVA_API = settings.STRAVA_API


def _update_task_model(model=None):
    # today = datetime.utcnow().replace(tzinfo=pytz.utc)
    if model.frequency > 7:
        from_date = model.from_date + relativedelta(months=1)
        model.to_date = from_date + relativedelta(months=1)
    else:
        from_date = model.from_date + relativedelta(days=model.frequency)
        model.to_date = from_date + relativedelta(days=model.frequency)
    model.from_date = from_date
    model.save()


@shared_task
def get_activities_task(user=None, get_type=None):
    try:
        u = User.objects.get(pk=user)
        if get_type == 'import':
            get_task_model = ImportActivitiesTask.objects.get(user=u)
        elif get_type == 'sync':
            get_task_model = SyncActivitiesTask.objects.get(user=u)
        else:
            return f"ERROR! User {user} task type does not exist."
        g = get_activities(user=u, start_date=get_task_model.from_date, end_date=get_task_model.to_date)
        _update_task_model(get_task_model)
        return g
    except ImportActivitiesTask.DoesNotExist:
        return f"ERROR! User {user} task does not exist."


@shared_task
def add(x, y):
    '''
    Simple function only to check Celery with RabbitMQ as a Message Broker
    :param x:
    :param y:
    :return:
    '''
    return x + y


# @shared_task
# def import_activities_task(user=None):
#     try:
#         u = User.objects.get(pk=user)
#         import_task = ImportActivitiesTask.objects.get(user=u)
#         g = get_activities(user=u, start_date=import_task.start_date, end_date=import_task.end_date)
#         _update_task_model(import_task)
#         return g
#     except ImportActivitiesTask.DoesNotExist:
#         return f"ERROR! User {user} task does not exist."
#
#
# @shared_task
# def sync_activities_task(user=None):
#     try:
#         u = User.objects.get(pk=user)
#         sync_task = SyncActivitiesTask.objects.get(user=u)
#         g = get_activities(user=u, start_date=sync_task.start_date, end_date=sync_task.end_date)
#         _update_task_model(sync_task)
#         return g
#     except SyncActivitiesTask.DoesNotExist:
#         return f"ERROR! User {user} task does not exist."
