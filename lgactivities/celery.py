import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgactivities.settings')

app = Celery('lgactivities')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# app.conf.broker_url = settings.REDIS_URL
#
# # this allows you to schedule items in the Django admin.
# app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
# app.conf.result_backend = "django-db"
app.conf.update(
    #broker_url=settings.REDIS_URL,
    broker_url=settings.RABBITMQ_URL,
    beat_scheduler='django_celery_beat.schedulers.DatabaseScheduler',
    result_backend="django-db",
)
