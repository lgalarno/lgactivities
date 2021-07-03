from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, HttpResponseRedirect, HttpResponse

import requests

from .utils import formaterror
from .models import Token
from allauth.socialaccount.models import SocialApp

# Create your views here.

STRAVA_API = settings.STRAVA_API


def requestcode(request):
    a = get_object_or_404(SocialApp, name=STRAVA_API['name'])  # get_object_or_404(StravaApp, name=STRAVA_API)
    auth_url = f"{STRAVA_API['URLS']['oauth']}authorize?client_id={a.client_id}&response_type=code&redirect_uri=http://{STRAVA_API['callback_domain']}/connection/exchange_token&approval_prompt=auto&scope=read,activity:read_all"
    return HttpResponseRedirect(auth_url)


def exchange_token(request):
    error = request.GET.get('error')
    code = request.GET.get('code')
    if code:
        a = get_object_or_404(SocialApp, name=STRAVA_API['name'])  # get_object_or_404(StravaApp, name=STRAVA_API)
        payload = {
            'client_id': a.client_id,
            'client_secret': a.secret,
            'code': code,
            'grant_type': "authorization_code",
            'f': 'json'
        }
        res = requests.post(f"{STRAVA_API['URLS']['oauth']}token", data=payload, verify=False).json()
        if 'errors' in res:
            e = formaterror(res['errors'])
            messages.warning(request, 'An error occurred while getting the activity: ' + e)
        elif 'access_token' in res:
            t, created = Token.objects.get_or_create(app=a)
            t.code = code
            t.scope = request.GET.get('scope')
            t.access_token = res['access_token']
            t.refresh_token = res['refresh_token']
            t.expires_at = res['expires_at']
            t.expires_in = res['expires_in']
            t.token_type = res['token_type']
            t.save()
            if 'nextpage' in request.session:
                go_next = request.session.pop('nextpage', None)
                return HttpResponseRedirect(go_next)
    elif error:
        messages.warning(request, 'An error occurred while accessing the code: ' + error)
    return HttpResponseRedirect('/')
