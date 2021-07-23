from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.views.generic import UpdateView

from allauth.socialaccount.models import SocialAccount

from .models import StravaProfile
from .forms import UserProfileForm, StravaProfileForm

# Create your views here.


class EditProfile(UpdateView):
    model = User
    # form_class = UserProfileForm
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


# def edit_profile(request):
#     u = get_object_or_404(User, pk=request.user.pk)
#     sau = get_object_or_404(SocialAccount, user_id=request.user.pk)
#     context = {
#         "title": "-edit_profile",
#         "StravaID": sau.uid}
#     if request.method == 'POST':
#         user_form = UserProfileForm(request.POST, instance=u)
#         strava_form = StravaProfileForm(request.POST, instance=u.user)
#         if user_form.is_valid() and strava_form.is_valid():
#             user_form.save()
#             strava_form.save()
#             messages.success(request, 'Profile has been updated.')
#         context["user_profile_form"] = user_form
#         context["strava_profile_form"] = strava_form
#         return render(request, 'edit_profile.html', context)
#
#     context["user_profile_form"] = UserProfileForm(instance=u)
#     context["strava_profile_form"] = StravaProfileForm(instance=u.user)
#     return render(request, 'edit_profile.html', context)
