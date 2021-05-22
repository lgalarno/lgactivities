from django.conf import settings
from django.shortcuts import get_object_or_404

import requests
import json
import time

from .models import StravaApp, Token

STRAVA_API = settings.STRAVA_API


# not a view, but here for convenience regarding imports
def refresh_token(a, t):
    payload = {
        'client_id': a.client_id,
        'client_secret': a.client_secret,
        'refresh_token': t.refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    res = requests.post(f"{settings.STRAVA_URLS['oauth']}token", data=payload, verify=False).json()
    if 'errors' in res:
        e = formaterror(res['errors'])
    elif 'access_token' in res:
        t.access_token = res['access_token']
        t.refresh_token = res['refresh_token']
        t.expires_at = res['expires_at']
        t.expires_in = res['expires_in']
        t.token_type = res['token_type']
        t.save()
        e = True
    else:
        e = 'unknown error'
    return e


def check_token():
    a = get_object_or_404(StravaApp, name=STRAVA_API)
    t = Token.objects.get(app=a)
    if int(time.time()) > t.expires_at:
        e = refresh_token(a, t)
    else:
        e = True

    return e, t.access_token


def res(request, token_url, payload):
    result=True
    res = requests.post(token_url, data=payload, verify=False)
    if 'errors' in res.json():
        result=False
        #messages.warning(request, res.json()['errors'])
    return res, result


def formaterror(message):
    if type(message) == list:
        return json.dumps(message[0])
    else:
        return 'unknown error'


