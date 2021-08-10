from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView

import requests
from datetime import datetime

from activities.models import Activity, Map, Segment, SegmentEffort

from .utils import formaterror, get_token

STRAVA_API = settings.STRAVA_API
# Create your views here.


def getactivities(request):
    if request.method == "POST":
        context = {}
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
        print(start_date)
        print(end_date)
        if start_date is None or end_date is None:
            raise Http404()
        e, access_token = get_token(user = request.user)
        if not e:
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'after': int(datetime.strptime(start_date,'%Y-%m-%d').timestamp()),
                'before': int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()),
            }
            url = f"{STRAVA_API['URLS']['athlete']}athlete/activities"
            e, activities = _requestStrava(url, headers, params, verify=False)
            if not e:
                for activity in activities:
                    a, created = Activity.objects.get_or_create(
                        id=activity.get('id'),
                        user=request.user,
                        name=activity.get('name'),
                        type=activity.get('type'),
                        start_date=activity.get('start_date'),
                        start_date_local=activity.get('start_date_local'),
                    )
                    if created:
                        params = {}
                        url = f"{STRAVA_API['URLS']['athlete']}activities/{a.id}/?include_all_efforts=True"
                        e, activity_detailed = _requestStrava(url, headers, params, verify=False)
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
                        else:
                            messages.warning(request, f'An error occurred while getting the activity {a.id}: {e}')
                messages.success(request, f"{len(activities)} activities were entered into the database")
                return redirect('getactivities:getactivities')
            else:
                messages.warning(request, f'An error occurred while getting the activity: {e}')
        else:
            messages.warning(request, f'An error occurred while getting the activity: {e}')
            context = {
                'date_from': start_date,
                'date_to': end_date
            }
    else:
        latestactity = Activity.objects.filter(user=request.user).order_by('start_date').last()
        if latestactity:
            date_from = latestactity.start_date.strftime('%Y-%m-%d')
        else:
            date_from = '2011-04-23'
        context = {
            'date_from': date_from,
            'date_to': date_from
        }
    context['title'] = 'get-activity'
    return render(request, 'getactivities/get-getactivities.html', context)


class ListactivitiesView(ListView):
    model = Activity
    template_name = 'getactivities/list-activities.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'list-activities'
        return context


def lastactivity(request):
    context = {}
    # e, access_token = check_token()
    e, access_token = get_token(user=request.user)
    if not e:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'per_page': 1, 'page': 1}
        url = f"{STRAVA_API['URLS']['athlete']}athlete/activities"
        e, my_dataset = _requestStrava(url, headers, params, verify=False)
        #my_dataset = [{'resource_state': 2, 'athlete': {'id': 1490709, 'resource_state': 1}, 'name': 'Download - Honister Pass - The LakeDistrict UK', 'distance': 20752.3, 'moving_time': 3259, 'elapsed_time': 3259, 'total_elevation_gain': 575.9, 'type': 'VirtualRide', 'id': 5249323025, 'external_id': '8f1f455a-b295-412f-94aa-56c695e0ee13.fit', 'upload_id': 5592830717, 'start_date': '2021-05-06T02:27:35Z', 'start_date_local': '2021-05-05T22:27:35Z', 'timezone': '(GMT-05:00) America/Montreal', 'utc_offset': -14400.0, 'start_latlng': [54.517349, -3.149054], 'end_latlng': [54.602111, -3.191687], 'location_city': None, 'location_state': None, 'location_country': 'Canada', 'start_latitude': 54.517349, 'start_longitude': -3.149054, 'achievement_count': 15, 'kudos_count': 0, 'comment_count': 0, 'athlete_count': 1, 'photo_count': 0, 'map': {'id': 'a5249323025', 'summary_polyline': 'k|vkIr`fRlGvF|AvGPpD`B~DlC|OfAvBdBnBRl@NjAThLZfHXjCHnBCbCS`FF`GQbAwBtDQhBe@nAa@n@cDfCQf@B`EP|C?p@SfBJzEJzBh@dFDvACpCU~E@bE[lCZtFtAzJVlAl@xA\\nBMjABd@`@jAhAn@Rb@XvDfB`HBp@ApFJ|@f@bBF`C_@vBiApB[|AY|HHdEHj@^l@zAxEd@b@d@dAnAfM?lEK^wDzF}A~AwD`F]r@Q`A[~@w@pAo@lBy@bBm@vBaAvAWx@e@fC_ArAkAtDm@t@c@ASNuA|DoErIYd@qAdAYd@gBtEkBjG}AxCkClGcA`Bq@~BGpCaAlDe@~DEpCPvDGpDm@hFNlDSjD?jBZpEKtEW`DAzAH`B`@jE?lCW|BCnA^lFBxGOfDFdCQnG?xFq@lLPvFeAnGkA|Hu@`BqFbGoB`Hi@rCw@jA]~B_@bAc@b@a@DcEq@mAl@Yl@}@jDg@|CYx@sDlDgA`@[V_BbEqA~BuAnDm@b@}Am@a@@[Xi@zCsAtDqAxHeAfD{@nBs@xCgD|Jg@fDw@pC_@xCkAvCe@fBoA|CwD`Gq@`@uD`AeArAgDxCwAzCmA`AO\\q@rDc@b@e@@OQY{@YeBGoC]{D]}As@k@kCKY[YcASiAYgD_AmGs@{CY_Ci@oG_@gJu@uD}DiL}A{Dg@_Bc@mAc@kBCsAa@cEPeTEiFGkA]eBw@uAIc@Fy@XgAf@w@pAkAFa@O}@u@mB}AeNa@gBiAuCwCiFu@sBwBgCqGaOeGiO_B_GmBwEe@{AwDeH{DmJ{EkM_AqAeFiFaFuDwGgHsBiBmB}BcBs@OQOwAGA_@jBK@]m@_AaF[yDm@yByAuHw@aMGsFi@oG{AcKy@qH{@gCr@cMVeDJ[l@q@`@oAR_BD}AM_BiCkNOwASy@kAoCeBaDaAmAoFgLuByHmCiHu@oCWc@_@K[Bm@f@UAEM`@eEW{C]gBgBeFwBcDcBsE{A_DmCmCmA_@yJBqEXsOtDi@`@_@x@y@rDeBp@kEnCiCM{@a@mCQ}GyA}CBeCZsD|@{@?{@OyBgAuFkBaCuAoEoDsAu@}@_DgAqBeA_AaBo@eF{EmA}AoBaAuA_@yBSqBdAsBj@aAt@w@lAyAtDeEfFy@zAOn@u@jGcA~@c@rAIpBHvDO~@qAtB}@X}AjA', 'resource_state': 2}, 'trainer': False, 'commute': False, 'manual': False, 'private': False, 'visibility': 'everyone', 'flagged': False, 'gear_id': None, 'from_accepted_tag': False, 'upload_id_str': '5592830717', 'average_speed': 6.368, 'max_speed': 24.5, 'average_cadence': 57.0, 'average_temp': 0, 'average_watts': 191.7, 'weighted_average_watts': 197, 'kilojoules': 624.8, 'device_watts': True, 'has_heartrate': True, 'average_heartrate': 155.0, 'max_heartrate': 169.0, 'heartrate_opt_out': False, 'display_hide_heartrate_option': True, 'max_watts': 499, 'elev_high': 364.0, 'elev_low': 89.0, 'pr_count': 3, 'total_photo_count': 0, 'has_kudoed': False}]
        if not e:
            activityID = my_dataset[0]['id']
            params = {}
            url = f"{STRAVA_API['URLS']['athlete']}activities/{activityID}"
            # activity = requests.get(url, headers=header, params=param, verify=False).json()
            e, activity = _requestStrava(url, headers, params, verify=False)
            context = activity
        else:
            messages.warning(request, 'An error occurred while getting the activity: ' + e)
    else:
        messages.warning(request, 'An error occurred while refreshing the code: ' + e)

    context['title'] = 'last-activity'
    return render(request, 'getactivities/last-activities.html', context)


def _requestStrava(url, headers, params, verify=False):
    e = False
    data = requests.get(url, headers=headers, params=params, verify=verify).json()
    if 'errors' in data:
        e = formaterror(data['errors'])
    return e, data
