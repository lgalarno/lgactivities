from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

import json
import polyline

from activities.models import Segment, Map, StaredSegment


class SegmentStaringAPIToggle(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, segment_id=None):
        obj = get_object_or_404(Segment, pk=segment_id)
        s, created = StaredSegment.objects.get_or_create(
            segment=obj,
            user=request.user
        )
        if created:
            staring = True
        else:
            staring = False
            s.delete()
        data = {
            'staring': staring
        }
        return Response(data)


class RecentEffortsDataAPI(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, segment_id=None):
        segment = get_object_or_404(Segment, pk=segment_id)
        all_efforts = segment.get_all_efforts(user=request.user)
        all_times = [e.get_time() for e in all_efforts]
        all_dates = [e.start_date_local.strftime("%m/%d/%Y") for e in all_efforts]
        best_perf_index = all_times.index(min(all_times))
        activity_url = [e.activity.get_absolute_url() for e in all_efforts]
        activity_names = [e.activity.name for e in all_efforts]
        data = {
            'all_dates': all_dates,
            'all_times': all_times,
            'best_perf_index': best_perf_index,
            'activity_url': activity_url,
            'activity_names': activity_names,
        }
        return Response(data)


class GetMapDataAPI(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, model_id=None):
        obj = get_object_or_404(Map, pk=model_id)
        segment_map = polyline.decode(obj.polyline)
        data = {
            'coord': json.dumps(segment_map),
        }
        return Response(data)
