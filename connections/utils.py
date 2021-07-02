from django.conf import settings
from django.shortcuts import get_object_or_404, HttpResponseRedirect

import requests
import json
import time

# from .models import StravaApp, Token
from .models import Token
from allauth.socialaccount.models import SocialApp

STRAVA_API = settings.STRAVA_API


def refresh_token(a, t):
    e = False
    # a = get_object_or_404(SocialApp, name=STRAVA_API['name'])
    payload = {
        'client_id': a.client_id,
        'client_secret': a.secret,           #a.client_secret,
        'refresh_token': t.refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    res = requests.post(f"{STRAVA_API['URLS']['oauth']}token", data=payload, verify=False).json()
    if 'errors' in res:
        e = formaterror(res['errors'])
    elif 'access_token' in res:
        t.access_token = res['access_token']
        t.refresh_token = res['refresh_token']
        t.expires_at = res['expires_at']
        t.expires_in = res['expires_in']
        t.token_type = res['token_type']
        t.save()
    else:
        e = 'unknown error'
    return e


def check_token():
    e = False
    a = get_object_or_404(SocialApp, name=STRAVA_API['name'])  # get_object_or_404(StravaApp, name=STRAVA_API)
    t, created = Token.objects.get_or_create(app=a)
    if int(time.time()) > t.expires_at:
        e = refresh_token(a, t)
    return e, t.access_token


def res(request, token_url, payload):
    result=True
    res = requests.post(token_url, data=payload, verify=False)
    if 'errors' in res.json():
        result=False
    return res, result


def formaterror(message):
    if type(message) == list:
        return json.dumps(message[0])
    else:
        return 'unknown error'


