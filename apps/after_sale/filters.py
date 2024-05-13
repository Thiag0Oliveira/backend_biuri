import django_filters

from apps.service_core import models


class GenericFilter(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter()


    class Meta:
        model = models.Attendance
        fields = ['status', 'type']

