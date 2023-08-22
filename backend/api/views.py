from django.db import IntegrityError
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from api.cart_file import shopping_cart_pdf
from api.filters import RecipeFilter, IngredientSearch
from api.pagination import LimitNumberPagination
from api.permissions import ReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    RecipeIntroSerializer,
    ShoppingCartSerializer,
)

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredient,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_class = [IsAdminUser | ReadOnly]
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminUser | ReadOnly]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientSearch


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    ordering_fields = ("pub_date",)
    ordering = ("pub_date",)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeCreateSerializer
        elif self.action in ("favorite", "shopping_cart"):
            return RecipeIntroSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), ]
        elif self.action in ("update", "partial_update",
                             "destroy", "download_shopping_cart"):
            return [IsOwnerOrReadOnly(), ]
        elif self.action in ("favorite", "shopping_cart"):
            return [IsAuthenticated(), ]
        return [AllowAny(), ]

    def add_item(self, model, serializer, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            item = model.objects.create(recipe=recipe, user=request.user)
            serializer = serializer(item)
        except IntegrityError:
            return Response(
                {"message": "Рецепт уже добавлен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def delete_item(self, model, request, pk=None):
        try:
            item = model.objects.get(recipe=pk, user=request.user)
            item.delete()
        except model.DoesNotExist:
            return Response(
                {"message": "Невозможно удалить, этого рецепта нет в списке"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["post"], detail=True)
    def favorite(self, request, pk=None):
        return self.add_item(Favorite, FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_item(Favorite, request, pk)

    @action(methods=["post"], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.add_item(ShoppingCart, ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_del(self, request, pk=None):
        return self.delete_item(ShoppingCart, request, pk)

    @action(methods=["get"], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shoppingcart__user=user)
        shopping_list = (
            RecipeIngredient.objects.filter(recipe__in=recipes)
            .values("ingredient")
            .annotate(total_amount=Sum("amount"))
        )
        response = shopping_cart_pdf(shopping_list)
        return response
