# Generated by Django 3.2.3 on 2023-08-11 13:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_rename_tag_recipe_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, message="Время приготовления не может быть < 1 мин."
                    )
                ]
            ),
        ),
    ]
