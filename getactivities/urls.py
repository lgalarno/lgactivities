from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import getactivities, GetActivitiesTaskView

app_name = 'getactivities'

urlpatterns = [
    path('', login_required(getactivities), name="getactivities"),
    path('task/', GetActivitiesTaskView.as_view(), name="task_view"),
]
