from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from allauth.socialaccount.models import SocialAccount

from .models import User

# Create your views here.


class EditProfile(UpdateView):
    model = User
    fields = ['email', 'username', 'first_name', 'last_name', 'time_zone']
    template_name = 'edit_profile.html'
    success_message = 'Changes successfully saved'

    def get_object(self):
        obj = get_object_or_404(User, pk=self.request.user.pk)
        return obj

    def form_valid(self, form):
        messages.success(self.request, f"Your profile has been saved.")  # {m}")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'edit_profile'
        u = self.get_object()
        sau = SocialAccount.objects.get(user=u)
        context['StravaID'] = sau.uid
        context['city'] = sau.extra_data.get("city")
        context['country'] = sau.extra_data.get("country")
        if u.avatar:
            context['avatar'] = u.avatar.url
        return context

    def get_success_url(self):
        return '/profile/edit/'
