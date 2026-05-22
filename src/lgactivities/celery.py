import os
from celery import Celery

# set the default Django settings_old module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgactivities.settings')

app = Celery('lgactivities')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
