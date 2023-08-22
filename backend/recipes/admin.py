from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    TagRecipe,
    ShoppingCart,
    Favorite,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "count_favorites")
    list_filter = ("author", "name", "tags")
    filter_horizontal = ("tags",)
    inlines = (RecipeIngredientsInLine,)

    def count_favorites(self, obj):
        return obj.favorite_set.count()

    count_favorites.short_description = "Added to favorites"


class IngredientResourse(resources.ModelResource):
    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResourse
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ("recipe", "tag")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user", "count_favorites")

    def count_favorites(self, obj):
        return obj.recipe.favorite_set.count()

    count_favorites.short_description = "Added to favorites"


admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
