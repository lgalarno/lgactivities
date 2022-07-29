from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

import requests
import json
from datetime import datetime, timedelta

from allauth.socialaccount.models import SocialApp, SocialToken

from activities.models import Activity, Map, Segment, SegmentEffort, ActivityType

import getactivities.tasks as tasks

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
    res = requests.post(f"{STRAVA_API['URLS']['oauth']}token", data=payload, verify=True).json()
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


def get_token(user=None):
    e = False
    sa = SocialApp.objects.get(name=STRAVA_API['name'])
    t = get_object_or_404(SocialToken.objects.filter(app=sa), account__user=user)  # only one social app
    if t.expires_at:
        if datetime.utcnow() > t.expires_at.replace(tzinfo=None):
            e = refresh_token(sa, t)
    else:
        e = refresh_token(sa, t)

    return e, t.token


def formaterror(message):
    if type(message) == list:
        return json.dumps(message[0])
    else:
        return 'unknown error'


#TODO remove leading spaces in name
def get_activities(user=None, start_date=None, end_date=None):
    if start_date is None or end_date is None or user is None:
        return False
    e, access_token = get_token(user=user)
    if not e:
        """
        get activities
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'after': int(start_date.timestamp()),
            'before': int(end_date.timestamp()),
        }
        url = f"{STRAVA_API['URLS']['athlete']}athlete/activities"
        e, activities = _requestStravaTask(url, headers, params, verify=True)
        if not e:
            for activity in activities:

                a, act_created = Activity.objects.get_or_create(id=activity.get('id'), user=user)
                a.name = activity.get('name')

                at, type_created = ActivityType.objects.get_or_create(name=activity.get('type'))
                if type_created:
                    at.color = "red"
                    at.icon = "images/activity-types/unknown.png"
                    new_activity_type_email(at=at.type, a=a.id, u=user.username)
                    at.save()
                a.type = at  # activity.get('type')
                a.start_date = activity.get('start_date')
                a.start_date_local = activity.get('start_date_local')
                a.save()
                if act_created:
                    """
                    get activity detailed 
                    """
                    params = {}
                    url = f"{STRAVA_API['URLS']['athlete']}activities/{a.id}/?include_all_efforts=True"
                    e, activity_detailed = _requestStravaTask(url, headers, params, verify=True)
                    if not e:
                        m, map_created = Map.objects.get_or_create(activity=a)
                        m.polyline = activity_detailed.get('map').get('polyline')
                        m.save()
                        if "segment_efforts" in activity_detailed:
                            segment_efforts = activity_detailed.get("segment_efforts")
                            for se in segment_efforts:
                                segment, segment_created = Segment.objects.get_or_create(
                                    id=se.get('segment').get('id')
                                )
                                segment.name = se.get('segment').get('name')
                                segment.save()
                                # elements required for 'set_pr_rank' in models of SegmentEffort
                                obj, effort_created = SegmentEffort.objects.get_or_create(
                                    id=se.get('id'),
                                    activity=a,
                                    segment=segment,
                                    elapsed_time=se.get('elapsed_time')
                                )
                                obj.start_date = se.get('start_date')
                                obj.start_date_local = se.get('start_date_local')
                                obj.distance = se.get('distance')
                                obj.save()

            return f"{len(activities)} new activities for {user.username}, from {datetime.date(start_date)} to {datetime.date(end_date)}  "
    return f"ERROR! User {user.username} - from {start_date} to {end_date}."


def new_activity_type_email(at=None, a=None, u=None):
    if at and a and u:
        mail_subject = 'lgactivities - New activity type'
        mail_body = f"""
        A new activity type was entered into the database of lgactivities and will require a new icon:

        Activity type: {at}
        Activity ID: {a}
        user: {u}

        This email was sent by lgactivities.
        """
        tasks.send_email.delay(to_email='lgalarno@outlook.com', mail_subject=mail_subject, mail_body=mail_body)


def _requestStravaTask(url, headers, params, verify=False):
    e = False
    data = requests.get(url, headers=headers, params=params, verify=verify).json()
    if 'errors' in data:
        e = formaterror(data['errors'])
    return e, data
