from django_filters import rest_framework as filters
from django_filters import ModelMultipleChoiceFilter

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.CharFilter(field_name='author__username')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
        model = Recipe

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset