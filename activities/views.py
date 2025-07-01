from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render
from django.views.generic import ListView, DetailView

import os

from .models import Activity, SegmentEffort, StaredSegment, Segment
from .utils import fit_to_csv, virtualride_in_fit
from getactivities.utils import update_segment, get_activity

# Create your views here.


class ActivityDetailsView(LoginRequiredMixin, DetailView):
    model = Activity
    template_name = 'activities/activity-details.html'

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = cache.get(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", None)
        if not obj:
            obj = super(ActivityDetailsView, self).get_object(queryset)
            cache.set(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['segments_efforts'] = self.object.get_all_segments()
        context['title'] = 'Activity'
        return context


def refresh_activity(request, pk):
    a = get_activity(request.user, pk)
    context = {
        'object': a,
        'segments_efforts': a.get_all_segments()
    }
    return render(request, 'activities/activity-details.html', context)


class SegmentDetailsView(LoginRequiredMixin, DetailView):
    model = Segment
    template_name = 'activities/segment-details.html'

    def get_object(self, queryset=None):
        obj = cache.get(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", None)
        if not obj:
            obj = super(SegmentDetailsView, self).get_object(queryset)
            update_segment(u=self.request.user, segment=obj)
            obj.refresh_from_db()
            cache.set(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        efforts = self.object.get_all_efforts(user=self.request.user)
        context['efforts'] = efforts
        context['pb'] = self.object.get_best_effort(user=self.request.user)
        context['staring'] = self.object.is_stared(user=self.request.user)
        context['title'] = 'Segment'
        return context


class EffortDetailsView(LoginRequiredMixin, DetailView):
    model = SegmentEffort
    template_name = 'activities/effort-details.html'

    def get_object(self, queryset=None):
        obj = cache.get(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", None)
        if not obj:
            obj = super(EffortDetailsView, self).get_object(queryset)
            # update segment if new kom, Qom, updated
            s = Segment.objects.get(id=obj.segment.id)
            update_segment(u=self.request.user, segment=s)
            obj.refresh_from_db()
            cache.set(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
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


# def repair_tacx_activity(request):
#     suggested = True
#     lookups = Q(user=request.user) and \
#               (Q(name__icontains='Chianti') | Q(name__icontains='Download') | Q(name__icontains='Grossglockner') | Q(name__icontains='Amstel') | Q(name__icontains='TACX'))
#     activities = Activity.objects.filter(lookups).exclude(type__name='VirtualRide')
#     if not activities:
#         suggested = False
#         activities = Activity.objects.filter(user=request.user).exclude(type__name='VirtualRide')
#     context = {'title': 'stared segments',
#                'activities': activities,
#                'suggested': suggested
#                }
#     return render(request, 'activities/tacx-to-virtual-list.html', context)


def fit_file_utils(request):
    if request.method == "POST":
        fit_file = request.FILES['fit_file']
        if fit_file:
            fs = FileSystemStorage()
            fn = os.path.join('files', fit_file.name)  # fit_file.name
            fs.save(fn, fit_file)
            fp = os.path.join(fs.location, fn)
            if 'to_csv' in request.POST:

                new_file, r = fit_to_csv(fp)
                if r:
                    f = open(new_file, 'rb').read()
                    response = HttpResponse(
                        f,
                        content_type='text/csv',
                        headers={'Content-Disposition': f"attachment; filename = {os.path.basename(new_file)}"},
                    )

                else:
                    return HttpResponseServerError(f"<h1>Server Error (500): {new_file}</h1>")
            elif 'to_virtual' in request.POST:
                new_file, r = virtualride_in_fit(fp)
                if r:
                    response = HttpResponse(
                        open(new_file, 'rb').read(),
                        content_type='application/fit ',
                        headers={'Content-Disposition': f"attachment; filename = {os.path.basename(new_file)}"},
                    )
                else:
                    return HttpResponseServerError(f"<h1>Server Error (500): {new_file}</h1>")
            else:
                raise Http404
            fs.delete(fn)
            os.remove(new_file)
            return response
            #
    context = {'title': 'tacx to virtual ride'
               }
    return render(request, 'activities/fit-file-utils.html', context)


# def tacx_to_virtual_list(request):
#     suggested = True
#     lookups = Q(user=request.user) and \
#               (Q(name__icontains='Chianti') | Q(name__icontains='Download') | Q(name__icontains='Grossglockner') | Q(name__icontains='Amstel') | Q(name__icontains='TACX'))
#     activities = Activity.objects.filter(lookups).exclude(type__name='VirtualRide')
#     if not activities:
#         suggested = False
#         activities = Activity.objects.filter(user=request.user).exclude(type__name='VirtualRide')
#     context = {'title': 'tacx to virtual-list',
#                'activities': activities,
#                'suggested': suggested
#                }
#     return render(request, 'activities/tacx-to-virtual-list.html', context)
#
#
# def tacx_to_virtual(request, pk):
#     # url = f'https://www.strava.com/activities/{pk}/export_original'
#     # r = requests.get(url)
#     get_fit_file(request.user, pk)
#     # print(r.status_code)
#     # if r.status_code == 200:
#     #     # save attached file
#     #     # create a new instance of FileSystemStorage
#     #     # fs = FileSystemStorage()
#     #     # file = fs.save('temp.fit', r.content)
#     #     # # the fileurl variable now contains the url to the file. This can be used to serve the file when needed.
#     #     # fileurl = fs.url(file)
#     #
#     #     with open('/media/luc/DataFast/owncloud/public_html/lgactivities/media/files/temp.fit', 'wb') as f:
#     #         f.write(r.content)
#
#     context = {'title': 'tacx to virtual ride'
#                }
#     return render(request, 'activities/tacx-to-virtual-list.html', context)
