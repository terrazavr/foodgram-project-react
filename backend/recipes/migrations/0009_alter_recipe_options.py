# Generated by Django 3.2.3 on 2023-08-21 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230821_0425'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]
