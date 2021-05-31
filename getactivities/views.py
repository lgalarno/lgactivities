from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect, reverse

import time
import requests
from datetime import datetime

from connections.utils import formaterror, check_token

from activities.models import Activity, Map, Segment, SegmentEffort
from connections.models import StravaApp, Token

STRAVA_API = settings.STRAVA_API

# Create your views here.


def getactivities(request):
    if request.method == "POST":
        context = {}
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
        if start_date is None or end_date is None:
            raise Http404()
        e, access_token = check_token()
        if e is True:
            header = {'Authorization': f'Bearer {access_token}'}
            param = {
                'after': int(datetime.strptime(start_date,'%Y-%m-%d').timestamp()),
                'before': int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()),
            }
            url = f"{settings.STRAVA_URLS['athlete']}athlete/activities"
            activities = requests.get(url, headers=header, params=param, verify=False).json()

            if 'errors' in activities:
                e = formaterror(activities['errors'])
                messages.warning(request, f'An error occurred while getting the activity: {e}')
            else:
                for activity in activities:
                    a, created = Activity.objects.get_or_create(
                        id=activity['id'],
                        name=activity['name'],
                        type=activity['type'],
                        start_lat=activity['start_latlng'][0],
                        start_lng=activity['start_latlng'][1],
                        start_date=activity['start_date'],
                        start_date_local=activity['start_date_local'],
                    )
                    if created:
                        param = {}
                        url = f"{settings.STRAVA_URLS['athlete']}activities/{a.id}"
                        activity_detailed = requests.get(url, headers=header, params=param, verify=False).json()
                        if 'errors' in activity_detailed:
                            e = formaterror(activities['errors'])
                            messages.warning(request, f'An error occurred while getting the activity {a.id}: {e}')
                        else:
                            # polyline= get_polyline(activity['map'])
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
                                        id=se['id'],
                                        activity=a,
                                        elapsed_time=se['elapsed_time'],
                                        start_date=se['start_date'],
                                        start_date_local=se['start_date_local'],
                                        distance=se['distance'],
                                        segment=segment,
                                    )
                                    obj.save()
                print(activities)
                messages.success(request, f"{len(activities)} activities were entered into the database")
                return redirect('getactivities:getactivities')

        else:
            messages.warning(request, 'An error occurred while getting the activity: ' + e)
            context = {
                'date_from': start_date,
                'date_to': end_date
            }
    else:
        latestactity = Activity.objects.order_by('start_date').last()
        if latestactity:
            date_from = latestactity.start_date.strftime('%Y-%m-%d')
        else:
            date_from = '2011-04-23'
        context = {
            'date_from': date_from,
            'date_to': date_from
        }
    return render(request, 'getactivities/get.html', context)


def listactivities(request):
    context = {}
    return render(request, 'getactivities/list.html', context)

def lastactivities(request):
    context = {}
    e, access_token = check_token()
    if e is True:
        header = {'Authorization': f'Bearer {access_token}'}
        param = {'per_page': 1, 'page': 1}
        my_dataset = requests.get(f"{settings.STRAVA_URLS['athlete']}athlete/activities", headers=header, params=param, verify=False).json()
        #my_dataset = [{'resource_state': 2, 'athlete': {'id': 1490709, 'resource_state': 1}, 'name': 'Download - Honister Pass - The LakeDistrict UK', 'distance': 20752.3, 'moving_time': 3259, 'elapsed_time': 3259, 'total_elevation_gain': 575.9, 'type': 'VirtualRide', 'id': 5249323025, 'external_id': '8f1f455a-b295-412f-94aa-56c695e0ee13.fit', 'upload_id': 5592830717, 'start_date': '2021-05-06T02:27:35Z', 'start_date_local': '2021-05-05T22:27:35Z', 'timezone': '(GMT-05:00) America/Montreal', 'utc_offset': -14400.0, 'start_latlng': [54.517349, -3.149054], 'end_latlng': [54.602111, -3.191687], 'location_city': None, 'location_state': None, 'location_country': 'Canada', 'start_latitude': 54.517349, 'start_longitude': -3.149054, 'achievement_count': 15, 'kudos_count': 0, 'comment_count': 0, 'athlete_count': 1, 'photo_count': 0, 'map': {'id': 'a5249323025', 'summary_polyline': 'k|vkIr`fRlGvF|AvGPpD`B~DlC|OfAvBdBnBRl@NjAThLZfHXjCHnBCbCS`FF`GQbAwBtDQhBe@nAa@n@cDfCQf@B`EP|C?p@SfBJzEJzBh@dFDvACpCU~E@bE[lCZtFtAzJVlAl@xA\\nBMjABd@`@jAhAn@Rb@XvDfB`HBp@ApFJ|@f@bBF`C_@vBiApB[|AY|HHdEHj@^l@zAxEd@b@d@dAnAfM?lEK^wDzF}A~AwD`F]r@Q`A[~@w@pAo@lBy@bBm@vBaAvAWx@e@fC_ArAkAtDm@t@c@ASNuA|DoErIYd@qAdAYd@gBtEkBjG}AxCkClGcA`Bq@~BGpCaAlDe@~DEpCPvDGpDm@hFNlDSjD?jBZpEKtEW`DAzAH`B`@jE?lCW|BCnA^lFBxGOfDFdCQnG?xFq@lLPvFeAnGkA|Hu@`BqFbGoB`Hi@rCw@jA]~B_@bAc@b@a@DcEq@mAl@Yl@}@jDg@|CYx@sDlDgA`@[V_BbEqA~BuAnDm@b@}Am@a@@[Xi@zCsAtDqAxHeAfD{@nBs@xCgD|Jg@fDw@pC_@xCkAvCe@fBoA|CwD`Gq@`@uD`AeArAgDxCwAzCmA`AO\\q@rDc@b@e@@OQY{@YeBGoC]{D]}As@k@kCKY[YcASiAYgD_AmGs@{CY_Ci@oG_@gJu@uD}DiL}A{Dg@_Bc@mAc@kBCsAa@cEPeTEiFGkA]eBw@uAIc@Fy@XgAf@w@pAkAFa@O}@u@mB}AeNa@gBiAuCwCiFu@sBwBgCqGaOeGiO_B_GmBwEe@{AwDeH{DmJ{EkM_AqAeFiFaFuDwGgHsBiBmB}BcBs@OQOwAGA_@jBK@]m@_AaF[yDm@yByAuHw@aMGsFi@oG{AcKy@qH{@gCr@cMVeDJ[l@q@`@oAR_BD}AM_BiCkNOwASy@kAoCeBaDaAmAoFgLuByHmCiHu@oCWc@_@K[Bm@f@UAEM`@eEW{C]gBgBeFwBcDcBsE{A_DmCmCmA_@yJBqEXsOtDi@`@_@x@y@rDeBp@kEnCiCM{@a@mCQ}GyA}CBeCZsD|@{@?{@OyBgAuFkBaCuAoEoDsAu@}@_DgAqBeA_AaBo@eF{EmA}AoBaAuA_@yBSqBdAsBj@aAt@w@lAyAtDeEfFy@zAOn@u@jGcA~@c@rAIpBHvDO~@qAtB}@X}AjA', 'resource_state': 2}, 'trainer': False, 'commute': False, 'manual': False, 'private': False, 'visibility': 'everyone', 'flagged': False, 'gear_id': None, 'from_accepted_tag': False, 'upload_id_str': '5592830717', 'average_speed': 6.368, 'max_speed': 24.5, 'average_cadence': 57.0, 'average_temp': 0, 'average_watts': 191.7, 'weighted_average_watts': 197, 'kilojoules': 624.8, 'device_watts': True, 'has_heartrate': True, 'average_heartrate': 155.0, 'max_heartrate': 169.0, 'heartrate_opt_out': False, 'display_hide_heartrate_option': True, 'max_watts': 499, 'elev_high': 364.0, 'elev_low': 89.0, 'pr_count': 3, 'total_photo_count': 0, 'has_kudoed': False}]
        if 'errors' in my_dataset:
            e = formaterror(my_dataset['errors'])
            messages.warning(request, 'An error occurred while getting the activity: ' + e)
        else:
            activityID = my_dataset[0]['id']
            param = {}
            url = f"{settings.STRAVA_URLS['athlete']}activities/{activityID}"
            activity = requests.get(url, headers=header, params=param, verify=False).json()
            context = activity
    else:
        messages.warning(request, 'An error occurred while refreshing the code: ' + e)
    return render(request, 'getactivities/last.html', context)
