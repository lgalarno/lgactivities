from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

import requests
import json
from datetime import datetime, timedelta

from allauth.socialaccount.models import SocialApp, SocialToken

STRAVA_API = settings.STRAVA_API


def refresh_token(sa, t):
    e = False
    payload = {
        'client_id': sa.client_id,
        'client_secret': sa.secret,
        'refresh_token': t.token_secret,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    res = requests.post(f"{STRAVA_API['URLS']['oauth']}token", data=payload, verify=False).json()
    if 'errors' in res:
        e = formaterror(res['errors'])
    elif 'access_token' in res:
        t.token = res['access_token']
        t.token_secret = res['refresh_token']
        t.expires_at = timezone.now() + timedelta(seconds=int(res['expires_in']))
        t.save()
    else:
        e = 'unknown error'
    return e


def get_token(user = None):
    e = False
    sa = SocialApp.objects.get(name=STRAVA_API['name'])
    t = get_object_or_404(SocialToken.objects.filter(app=sa), account__user=user)  # only one social app
    if datetime.utcnow() > t.expires_at.replace(tzinfo=None):
        e = refresh_token(sa, t)
    return e, t.token


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
