from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'getactivities'

urlpatterns = [
    path('listactivities/', views.listactivities, name="listactivities"),
    path('getactivities/', login_required(views.getactivities), name="getactivities"),
    path('lastactivities/', login_required(views.lastactivities), name="lastactivities"),
]