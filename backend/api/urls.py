from django.urls import path
from rest_framework.routers import DefaultRouter
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = "api"

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="ingredient")
router.register("recipes", RecipeViewSet, basename="recipe")

urlpatterns = [
    path(
        "recipes/download_shopping_list/",
        RecipeViewSet.as_view({"get": "download_shopping_cart"}),
        name="download_shopping_cart",
    )
]
urlpatterns += router.urls
