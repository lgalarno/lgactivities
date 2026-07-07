from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import UpdateView

from allauth.socialaccount.models import SocialAccount

from .forms import CustomAuthenticationForm
from .models import User

# Create your views here.


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("calendarapp:calendar_view")
    else:
        form = CustomAuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "profiles/login.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login")
    return render(request, "profiles/logout.html", {})


class EditProfile(UpdateView):
    model = User
    fields = ['email', 'username', 'first_name', 'last_name', 'time_zone']
    template_name = 'profiles/edit_profile.html'
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
