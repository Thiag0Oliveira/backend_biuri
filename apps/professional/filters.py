import django_filters

from . import models


class GenericFilter(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter()


    class Meta:
        model = models.Professional
        fields = ['executive', 'full_name', 'category', 'gender','categorias', 'professional_enabled', 'professional_enabled_executive','status', 'is_test', 'created']


class PortfolioFilter(django_filters.FilterSet):

    class Meta:
        model = models.Professional
        fields = ['executive', 'category', 'gender', 'categorias']