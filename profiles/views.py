from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from allauth.socialaccount.models import SocialAccount

from .models import StravaProfile

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
        sau = SocialAccount.objects.get(user_id=self.request.user.pk)
        sid = StravaProfile.objects.get(user_id=self.request.user.pk)
        context['StravaID'] = sau.uid
        context['city'] = sid.city
        context['country'] = sid.country
        if sid.avatar:
            context['avatar'] = sid.avatar.url
        return context

    def get_success_url(self):
        return '/profile/edit/'
