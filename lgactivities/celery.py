import os
from celery import Celery
from django.conf import settings

BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgactivities.settings')

app = Celery('lgactivities')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.broker_url = BASE_REDIS_URL

# this allows you to schedule items in the Django admin.
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
