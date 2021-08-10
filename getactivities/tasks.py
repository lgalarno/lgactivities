from django.conf import settings

from celery import shared_task
from datetime import datetime
import requests

from activities.models import Activity, Map, Segment, SegmentEffort

from .utils import formaterror, get_token

STRAVA_API = settings.STRAVA_API


@shared_task
def getactivities_task(user = None, start_date=None, end_date=None):
    if start_date is None or end_date is None  or user is None:
        return False
    e, access_token = get_token(user = user)
    if not e:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'after': int(datetime.strptime(start_date,'%Y-%m-%d').timestamp()),
            'before': int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()),
        }
        url = f"{STRAVA_API['URLS']['athlete']}athlete/activities"
        e, activities = _requestStravaTask(url, headers, params, verify=False)
        if not e:
            for activity in activities:
                a, created = Activity.objects.get_or_create(
                    id=activity.get('id'),
                    user=user,
                    name=activity.get('name'),
                    type=activity.get('type'),
                    start_date=activity.get('start_date'),
                    start_date_local=activity.get('start_date_local'),
                )
                if created:
                    params = {}
                    url = f"{STRAVA_API['URLS']['athlete']}activities/{a.id}/?include_all_efforts=True"
                    e, activity_detailed = _requestStravaTask(url, headers, params, verify=False)
                    if not e:
                        m = Map(
                            activity=a,
                            polyline=activity_detailed['map']['polyline']
                        )
                        m.save()
                        if "segment_efforts" in activity_detailed:
                            segment_efforts = activity_detailed["segment_efforts"]
                            for se in segment_efforts:
                                segment, created = Segment.objects.get_or_create(
                                    id=se['segment']['id'],
                                    name=se['segment']['name']
                                )
                                obj = SegmentEffort(
                                    id=se.get('id'),
                                    activity=a,
                                    elapsed_time=se.get('elapsed_time'),
                                    start_date=se.get('start_date'),
                                    start_date_local=se.get('start_date_local'),
                                    distance=se.get('distance'),
                                    segment=segment,
                                )
                                obj.save()


def _requestStravaTask(url, headers, params, verify=False):
    e = False
    data = requests.get(url, headers=headers, params=params, verify=verify).json()
    if 'errors' in data:
        e = formaterror(data['errors'])
    return e, data
