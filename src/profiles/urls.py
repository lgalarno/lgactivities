from django.contrib.auth.decorators import login_required
from django.urls import path

from profiles import views
from .views import EditProfile


app_name = 'profiles'

urlpatterns = [
    path('edit/', login_required(EditProfile.as_view()), name="EditProfile"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
]
