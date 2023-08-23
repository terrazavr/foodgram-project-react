from django.db import transaction
from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag)
from users.models import Subscribe, User
from users.serializers import UserInfoSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag
        lookup_field = "slug"


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit")

    class Meta:
        fields = ("id", "name", "measurement_unit", "amount")
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserInfoSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = request.user
        return (
            user.is_authenticated
            and Favorite.objects.filter(recipe=obj, user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_anonymous
            or ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        )


class RecipeIntroSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("user", "recipe")
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже добавлен в избранное",
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeIntroSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("user", "recipe")
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже добавлен в корзину",
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeIntroSerializer(instance.recipe, context=context).data


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )

    def validate_amount(self, amount):
        if amount == 0:
            raise serializers.ValidationError("Количество не может быть 0")
        return amount


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "ingredients", "tags",
                  "image", "name",
                  "text", "cooking_time")

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                "Не забудьте указать тег, чтобы быстрее искать рецепты"
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                "Без ингредиентов ничего не приготовить")
        unique_ingredients = set()
        duplicate_ingredients = []
        for ingredient in ingredients:
            if ingredient["id"] in unique_ingredients:
                duplicate_ingredients.append(ingredient["id"])
            else:
                unique_ingredients.add(ingredient["id"])
        if duplicate_ingredients:
            raise serializers.ValidationError(
                f"Ингредиент {duplicate_ingredients} уже есть в списке, "
                f"если в рецепте он используется дважды, "
                f"увеличьте количество существующего ингредиента"
            )
        return ingredients

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления не может быть меньше 1 минуты"
            )
        return value

    @staticmethod
    def create_ingredients(recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient_id=ingredient.get("id"),
                amount=ingredient["amount"],
                recipe=recipe,
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeSerializer(instance, context=context).data


class SubscribeGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeIntroSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (request.user.is_authenticated or Subscribe.objects.filter(
            user=request.user, author=obj.id).exists())

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        return RecipeIntroSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ("user", "author")
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны!",
            )
        ]

    def validate(self, data):
        author = data.get("author")
        user = self.context.get("request").user

        if user == author:
            raise serializers.ValidationError("Нельзя подписаться на себя.")

        return data

    def to_representation(self, instance):
        return SubscribeGetSerializer(
            instance.author, context={"request": self.context.get("request")}
        ).data
