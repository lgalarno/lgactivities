from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from allauth.socialaccount.models import SocialAccount

from .models import StravaProfile
from getactivities.models import SyncActivitiesTask, ImportActivitiesTask, Task_log
# Create your views here.


class EditProfile(UpdateView):
    model = User
    fields = ['email', 'username', 'first_name', 'last_name']
    template_name = 'edit_profile.html'

    def get_object(self):
        obj = get_object_or_404(User, pk=self.request.user.pk)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'edit_profile'
        u = self.get_object()
        # try:
        #     if u.sync_activities_task.active:
        #         context['sync'] = SyncActivitiesTask.objects.get(user=u)
        # except:
        #     pass
        # try:
        #     if u.import_activities_task.active:
        #         context['import'] = ImportActivitiesTask.objects.get(user=u)
        # except:
        #     pass
        sau = SocialAccount.objects.get(user=u)
        sid = StravaProfile.objects.get(user=u)
        context['StravaID'] = sau.uid
        context['city'] = sid.city
        context['country'] = sid.country
        if sid.avatar:
            context['avatar'] = sid.avatar.url
        return context

    def get_success_url(self):
        return '/profile/edit/'
