import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.CharFilter(method='filter_tags')
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
        )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_tags(self, queryset, name, value):
        if value:
            tags_list = value.split(',')
            return queryset.filter(tags__slug__in=tags_list).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if value == '1' and request and request.user.is_authenticated:
            return queryset.filter(favorites__user=request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if value == '1' and request and request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=request.user)
        return queryset
