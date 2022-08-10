from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.views.generic import ListView, DetailView

from .models import Activity, SegmentEffort, StaredSegment, ActivityType, Segment
from .utils import update_segment

# Create your views here.

STRAVA_API = settings.STRAVA_API


class ActivityDetailsView(LoginRequiredMixin, DetailView):
    model = Activity
    template_name = 'activities/activity-details.html'

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = cache.get('%s-%s' % (self.model.__name__.lower(), self.kwargs['pk']), None)
        if not obj:
            obj = super(ActivityDetailsView, self).get_object(queryset)
            cache.set('%s-%s' % (self.model.__name__.lower(), self.kwargs['pk']), obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['segments_efforts'] = self.object.get_all_segments()
        context['title'] = 'Activity'
        return context


# TODO filter by activity type
class SegmentDetailsView(LoginRequiredMixin, DetailView):
    model = Segment
    template_name = 'activities/segment-details.html'

    # def get_queryset(self):
    #     return Segment.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = cache.get('%s-%s' % (self.model.__name__.lower(), self.kwargs['pk']), None)
        if not obj:
            obj = super(SegmentDetailsView, self).get_object(queryset)
            cache.set('%s-%s' % (self.model.__name__.lower(), self.kwargs['pk']), obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        efforts = self.object.get_all_efforts(user=self.request.user)
        update_segment(u=self.request.user, segment=self.object)
        context['efforts'] = efforts
        context['pb'] = self.object.get_best_effort(user=self.request.user)
        context['staring'] = self.object.is_stared(user=self.request.user)
        context['title'] = 'Segment'
        return context


class EffortDetailsView(LoginRequiredMixin, DetailView):
    model = SegmentEffort
    template_name = 'activities/effort-details.html'

    def get_object(self, queryset=None):
        obj = cache.get('%s-%s' % (self.model.__name__.lower(), self.kwargs['pk']), None)
        if not obj:
            obj = super(EffortDetailsView, self).get_object(queryset)
            cache.set('%s-%s' % (self.model.__name__.lower(), self.kwargs['pk']), obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        # update segment if new kom, Qom, updated
        s = Segment.objects.get(id=self.object.segment.id)
        update_segment(u=self.request.user, segment=s)
        context['efforts'] = self.object.segment.get_all_efforts(user=self.request.user)
        context['staring'] = self.object.segment.is_stared(user=self.request.user)
        context['title'] = 'segment details'
        return context


class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = "activities/activity-list.html"

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'activity list'
        return context


class SegmentListView(LoginRequiredMixin, ListView):
    model = Segment
    template_name = "activities/segment-list.html"

    def get_queryset(self):
        s = Segment.objects.filter(segmenteffort__activity__user=self.request.user).distinct()
        return s

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'segment list'
        ss = StaredSegment.objects.filter(user=self.request.user)
        ssids = [s.segment for s in ss]
        context['stared_segment'] = ssids
        return context


# def effort_details(request, pk):
#     this_effort = get_object_or_404(SegmentEffort, pk=pk)
#     # segment = get_object_or_404(Segment, pk=this_effort.segment_id)
#     e, access_token = get_token(user=request.user)
#     if not e:
#         header = {'Authorization': f'Bearer {access_token}'}
#         param = {}
#         url = f"{STRAVA_API['URLS']['athlete']}segments/{this_effort.segment_id}"
#         segment_detail = requests.get(url, headers=header, params=param, verify=False).json()
#         if 'errors' in segment_detail:
#             e = formaterror(segment_detail['errors'])
#             messages.warning(request, f'An error occurred while getting the segment: {e}')
#             return HttpResponseRedirect('/')
#         else:
#             segment = this_effort.segment.update_from_strava(segment_detail=segment_detail)
#             m, created = Map.objects.get_or_create(segment=segment)
#             if created:
#                 m.polyline = segment_detail['map']['polyline']
#                 m.save()
#
#         efforts = segment.get_all_efforts(user=request.user)
#         context = {
#             'activity': this_effort.activity,
#             'this_effort': this_effort,
#             'segment': this_effort.segment,
#             'efforts': efforts,
#             'staring': segment.is_stared(user=request.user),
#             'title': 'segment details'
#         }
#         return render(request, 'activities/effort-details.html', context)
#     else:
#         messages.warning(request, f'An error occurred while getting the segment: {e}')
#         return HttpResponseRedirect('/')


class StaredSegmentsListView(LoginRequiredMixin, ListView):
    model = StaredSegment
    template_name = "activities/stared_segments.html"

    def get_queryset(self):
        return StaredSegment.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'stared segments'
        return context
