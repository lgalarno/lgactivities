from django.shortcuts import get_object_or_404, Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

import json
import polyline

from activities.models import Segment, Activity


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


class GetMapAPI(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, model_type=None, model_id=None, format=None):
        if model_type == 'segment':
            obj = get_object_or_404(Segment, pk=model_id)
        elif model_type == 'activity':
            obj = get_object_or_404(Activity, pk=model_id)
        else:
            raise Http404
        if obj.start_lat and obj.start_lng:
            center = f'[{obj.start_lat}, {obj.start_lng}]'
        else:
            center = '[46.87591, -71.28951]'
        segment_map = polyline.decode(obj.map.polyline)
        data = {
            'center': center,
            'coord': json.dumps(segment_map),
        }
        return Response(data)
