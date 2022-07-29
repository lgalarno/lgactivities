import os
from celery import Celery

# set the default Django settings_old module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgactivities.settings')

app = Celery('lgactivities')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# app.conf.update(
#     broker_url=settings_old.RABBITMQ_URL,
#     beat_scheduler='django_celery_beat.schedulers.DatabaseScheduler',
#     result_backend="django-db",
#     #worker_pool="solo"
# )
