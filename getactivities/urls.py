from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import getactivities, lastactivity, ListactivitiesView

app_name = 'getactivities'

urlpatterns = [
    path('listactivities/', ListactivitiesView.as_view(), name="listactivities"),
    path('', login_required(getactivities), name="getactivities"),
    path('lastactivity/', login_required(lastactivity), name="lastactivity"),
]