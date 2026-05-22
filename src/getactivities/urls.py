from django.contrib.auth.decorators import login_required
from django.urls import path

from getactivities import views
from .views import ImportActivitiesTaskView, SyncActivitiesTaskView

app_name = 'getactivities'

urlpatterns = [
    path('', login_required(views.getactivities), name="getactivities"),
    path('import-task/', ImportActivitiesTaskView.as_view(), name="import_task_view"),
    path('sync-task/', SyncActivitiesTaskView.as_view(), name="sync_task_view"),
]
