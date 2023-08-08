from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    TagRecipe,
)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    # фильтрация
    list_filter = ('author', 'name', 'tag')


class IngredientResourse(resources.ModelResource):

    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResourse
    list_display = ('name', 'measurement_unit')
    # фильтрация
    list_filter = ('name', )


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(TagRecipe, TagRecipeAdmin)
