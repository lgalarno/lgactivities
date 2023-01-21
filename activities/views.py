from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.views.generic import ListView, DetailView


from .models import Activity, SegmentEffort, StaredSegment, Segment
from .utils import update_segment

# Create your views here.

STRAVA_API = settings.STRAVA_API


class ActivityDetailsView(LoginRequiredMixin, DetailView):
    model = Activity
    template_name = 'activities/activity-details.html'

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = cache.get(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", None)
        print(obj)
        if not obj:
            obj = super(ActivityDetailsView, self).get_object(queryset)
            print(obj)
            cache.set(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['segments_efforts'] = self.object.get_all_segments()
        context['title'] = 'Activity'
        return context


class SegmentDetailsView(LoginRequiredMixin, DetailView):
    model = Segment
    template_name = 'activities/segment-details.html'

    def get_object(self, queryset=None):
        obj = cache.get(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", None)
        if not obj:
            obj = super(SegmentDetailsView, self).get_object(queryset)
            cache.set(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", obj)
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
        obj = cache.get(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", None)
        if not obj:
            obj = super(EffortDetailsView, self).get_object(queryset)
            cache.set(f"{self.model.__name__.lower()}-{self.kwargs['pk']}", obj)
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


# class ActivityListView(LoginRequiredMixin, ListView):
#     model = Activity
#     paginate_by = 10
#     template_name = "activities/activity-list-cbv.html"
#
#     # def get_queryset(self):
#     #     return Activity.objects.filter(user=self.request.user)
#
#     def get_queryset(self, **kwargs):
#         search_results = ActivityFilter(self.request.GET, self.queryset)
#         self.no_search_result = True if not search_results.qs else False
#         # Returns the default queryset if an empty queryset is returned by the django_filters
#         # You could as well return just the search result's queryset if you want to
#         return search_results.qs.distinct() or self.model.objects.all()
#
#     # def get_query_string(self):
#     #     query_string = self.request.META.get("QUERY_STRING", "")
#     #     # Get all queries excluding pages from the request's meta
#     #     validated_query_string = "&".join([x for x in re.findall(
#     #         r"(\w*=\w{1,})", query_string) if not "page=" in x])
#     #     # Avoid passing the query path to template if no search result is found using the previous query
#     #     return "&" + validated_query_string.lower() if (validated_query_string and not self.no_search_result) else ""
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['title'] = 'activity list'
#         context["no_search_result"] = self.no_search_result
#         # This is the query string which should be appended to the current page in your template for pagination, very critical
#         # context["query_string"] = self.get_query_string()
#         context['filter'] = ActivityFilter()
#         return context


# def activity_list(request):
#     # queryset_list = Activity.objects.filter(user=request.user)
#     print(request.GET)
#     print(request.META.get("QUERY_STRING", ""))
#
#     queryset_list = ActivityFilter(request.GET, queryset=Activity.objects.filter(user=request.user)).qs
#
#     query_string = request.META.get("QUERY_STRING", "")
#     validated_query_string = "&".join([x for x in re.findall(r"(\w*=\w{1,})", query_string) if not "page=" in x])
#
#     query_string = "&" + validated_query_string.lower() if (validated_query_string) else ""
#     print(query_string)
#
#     paginator = Paginator(queryset_list, 20) # Show 25 contacts per page
#     page_request_var = "page"  # naming more dynamics. see post_list.html
#     page = request.GET.get(page_request_var)
#     try:
#         queryset = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         queryset = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         queryset = paginator.page(paginator.num_pages)
#     context = {
#         'object_list': queryset,
#         'title': 'activity list',
#         'filter': ActivityFilter(),
#         'page_request_var': page_request_var,
#         "query_string": query_string,
#     }
#     return render(request, 'activities/activity-list-fbv.html', context)


# def activity_list(request):
#     queryset_list = Activity.objects.filter(user=request.user)
#     print(request.GET)
#     # q = request.GET.get("q")
#     if "q" in request.GET:
#         print('aaa')
#         filter_type = request.GET.get("filter_type")
#         if filter_type != "":
#             print('bbb')
#             queryset_list = queryset_list.filter(type__name=filter_type)
#
#         activity_search = request.GET.get("activity_search")
#         if activity_search != "":
#             print('ccc')
#             queryset_list = queryset_list.filter(name__icontains=activity_search)
#
#     paginator = Paginator(queryset_list, 20) # Show 25 contacts per page
#     page_request_var = "tab"  # naming more dynamics. see post_list.html
#     page = request.GET.get(page_request_var)
#     try:
#         queryset = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         queryset = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         queryset = paginator.page(paginator.num_pages)
#     context = {
#         'object_list': queryset,
#         'title': 'activity list',
#         'page_request_var': page_request_var,
#     }
#     return render(request, 'activites/activity-list-fbv.html', context)


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
