import django_filters
from cinema.models import Movie


class MovieFilter(django_filters.FilterSet):
    year__gt = django_filters.NumberFilter(field_name='year', lookup_expr='gt')
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    genre = django_filters.CharFilter(field_name='genre', lookup_expr='iexact')

    class Meta:
        model = Movie
        fields = ['category', 'genre', 'year__gt']
