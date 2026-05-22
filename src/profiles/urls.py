from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import EditProfile

app_name = 'profiles'

urlpatterns = [
    path('edit/', login_required(EditProfile.as_view()), name="EditProfile"),
]
