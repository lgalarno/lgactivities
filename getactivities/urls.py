from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import getactivities, ImportActivitiesTaskView, SyncActivitiesTaskView

app_name = 'getactivities'

urlpatterns = [
    path('', login_required(getactivities), name="getactivities"),
    path('import-task/', ImportActivitiesTaskView.as_view(), name="import_task_view"),
    path('sync-task/', SyncActivitiesTaskView.as_view(), name="sync_task_view"),
]
