from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinValueValidator

from foodgram.constants import (
    MAX_LEN_CHARFIELD,
    MIN_COOK_TIME,
    MIN_AMOUNT
)
from users.models import User


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=MAX_LEN_CHARFIELD)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True, null=False)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_LEN_CHARFIELD)
    measurement_unit = models.CharField(max_length=MAX_LEN_CHARFIELD)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes")
    name = models.CharField(max_length=MAX_LEN_CHARFIELD)
    image = models.ImageField(upload_to="recipes/")
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_COOK_TIME,
                message="Время приготовления не может быть < 1 мин.")
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ('-pub_date',)

    def __str__(self):
        return f"{self.name, self.text}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE)

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message="Минимальное количество не может быть меньше чем 1")
        ]
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return (
            f"{self.ingredient.name} - "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Тег рецепте"
        verbose_name_plural = "Теги в рецептах"

    def __str__(self):
        return f"{self.recipe} присвоен тег {self.tag}."


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe_in_cart"
            ),
        ]

        def __str__(self):
            return f"{self.user} добавил {self.recipe} в корзину"


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="favorite_recipes"),
        ]

        def __str__(self):
            return f"{self.recipe} добавлен в избранное к {self.user}"
