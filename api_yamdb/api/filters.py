import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр для произведений."""
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')
