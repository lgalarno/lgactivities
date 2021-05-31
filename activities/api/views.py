from django.shortcuts import get_object_or_404, Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

import json
import polyline
import datetime

from activities.models import Segment, Activity, Map


class SegmentStaringAPIToggle(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, segment_id=None, format=None):
        obj = get_object_or_404(Segment, pk=segment_id)
        s = obj.staring
        if s:
            obj.staring = False
            staring = False
        else:
            obj.staring = True
            staring = True
        obj.save()
        data = {
            'staring': staring
        }
        return Response(data)

# TODO Plot RecentEffortsData
class RecentEffortsDataAPI(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, segment_id=None, format=None):
        segment = get_object_or_404(Segment, pk=segment_id)
        all_efforts = segment.get_all_efforts()
        all_times = [e.get_time() for e in all_efforts]
        all_dates = [e.start_date_local.strftime("%m/%d/%Y") for e in all_efforts]
        best_perf_index = all_times.index(min(all_times))

        data = {
            'all_dates': all_dates,
            'all_times': all_times,
            'best_perf_time': all_times[best_perf_index],
            'best_perf_date': all_dates[best_perf_index],
            'best_perf_index': best_perf_index
        }
        return Response(data)


class GetMapDataAPI(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, model_type=None, model_id=None, format=None):
        obj = get_object_or_404(Map, pk=model_id)
        # if model_type == 'segment':
        #     obj = get_object_or_404(Segment, pk=model_id)
        # elif model_type == 'activity':
        #     obj = get_object_or_404(Activity, pk=model_id)
        # else:
        #     raise Http404
        # if obj.start_lat and obj.start_lng:
        #     center = f'[{obj.start_lat}, {obj.start_lng}]'
        # else:
        # center = '[46.87591, -71.28951]'
        segment_map = polyline.decode(obj.polyline)
        data = {
            # 'center': center,
            'coord': json.dumps(segment_map),
        }
        return Response(data)
