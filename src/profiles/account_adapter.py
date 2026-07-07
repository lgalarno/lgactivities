from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.signals import pre_social_login
from allauth.utils import get_user_model
from django.conf import settings
from django.dispatch import receiver
from django.shortcuts import redirect

from profiles.models import User

# change yourproject.exceptions accordingly
# from yourproject.exceptions import EmailNotFoundException


class MyLoginAccountAdapter(DefaultAccountAdapter):
    """
    Overrides allauth.account.adapter.DefaultAccountAdapter.ajax_response to avoid changing
    the HTTP status_code to 400
    """

    def get_login_redirect_url(self, request):
        """
        get the redirect login
        """
        if request.user.is_authenticated:
            return settings.LOGIN_REDIRECT_URL.format(id=request.user.id)
        else:
            return "/"


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Overrides allauth.socialaccount.adapter.DefaultSocialAccountAdapter.pre_social_login to
    perform some actions right after successful login
    """

    def pre_social_login(self, request, sociallogin):
        print('AAAAAAAAAAAAAAAAAAAA')
        pass  # TODOFuture: To perform some actions right after successful login


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """Login and redirect
    This is done in order to tackle the situation where user's email retrieved
    from one provider is different from already existing email in the database
    (e.g facebook and google both use same email-id). Specifically, this is done to
    tackle following issues:
    * https://github.com/pennersr/django-allauth/issues/215

    """
    print('BBBBBBBBBBBBBBBBBBB')
    print(sociallogin.account.extra_data)

    user = User.objects.filter(email="lgalarno@gmail.com")
    print(user)
    perform_login(request, user, email_verification="optional")
    print('CCCCCCCCCCCCC')
    raise ImmediateHttpResponse(
        redirect(settings.LOGIN_REDIRECT_URL.format(id=request.user.id))
    )
