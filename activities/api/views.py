from django.shortcuts import get_object_or_404, HttpResponse, render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

import plotly.graph_objects as go
import datetime
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
        all_times = [e.get_time_str() for e in all_efforts]
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


class RecentEffortsChartData(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, segment_id=None):
        print('RecentEffortsChartData')
        segment = get_object_or_404(Segment, pk=segment_id)
        all_efforts = segment.get_all_efforts(user=request.user)
        all_times = [e.get_time() for e in all_efforts]
        all_dates = [e.start_date_local.strftime("%m/%d/%Y") for e in all_efforts]
        best_perf_index = all_times.index(min(all_times))
        activity_urls = [e.activity.get_absolute_url() for e in all_efforts]
        activity_names = [e.activity.name for e in all_efforts]
        mock_date = datetime.datetime(2020, 1, 8, 0, 0, 0)
        y_datetime = [mock_date + t for t in all_times]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=all_dates,
            y=y_datetime,
            mode='markers',
            name="",
            text=activity_names,
            hoverinfo='all'
        ))
        fig.add_trace(go.Scatter(
            x=[all_dates[best_perf_index]],
            y=[y_datetime[best_perf_index]],
            mode='markers',
            hoverinfo='skip',
            marker={
                "color": 'rgba(0, 0, 0, 0)',
                "size": 20,
                "line": {
                    "color": 'rgb(255, 0, 0)',
                    "width": 2
                }
            }
        )
        )
        fig.update_layout(
            hovermode='closest',
            template="none",
            yaxis={
                "tickformat": '%H:%M:%S'
            },
            xaxis={
                "autorange": True
            },
            showlegend=False
        )
        fig.add_shape(
            type="line",
            xref='paper',
            x0=0,
            y0=y_datetime[best_perf_index],
            x1=1,
            y1=y_datetime[best_perf_index],
            line={
                "color": 'rgb(255, 0, 0)',
                "width": 1,
                "dash": 'dot'
            },
        )
        context = {
            "chart": fig.to_html(),
            "activity_urls": "activity_urls",
        }

        return render(request, 'activities/partials/efforts_chart.html', context)
        # return HttpResponse(fig.to_html())


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
