import django_filters

from .models import Activity, ActivityType


# def types(request):
#     print(request)
#     if request is None:
#         return ActivityType.objects.none()
#
#     a = Activity.objects.filter(user=request.user)
#     t = a.type_set.all()
#     print(request.user)
#     return t


class ActivityFilter(django_filters.FilterSet):
    type__name = django_filters.ModelChoiceFilter(lookup_expr='iexact', label='Type', queryset=ActivityType.objects.all())
    name = django_filters.CharFilter(lookup_expr='icontains', label='Activity')
    # start_date_local = django_filters.DateTimeFilter(lookup_expr='year__iexact', label='Year')
    # start_date_local = django_filters.DateTimeFilter(lookup_expr='year__gte', label='>= Year')
    # start_date_local = django_filters.DateTimeFilter(lookup_expr='year__lte', label='<= Year')

    class Meta:
        model = Activity
        fields = {
            'start_date_local': ['year__iexact', 'year__gte', 'year__lte']
            }
