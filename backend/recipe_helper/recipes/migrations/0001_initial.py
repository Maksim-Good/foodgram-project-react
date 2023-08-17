# Generated by Django 3.2 on 2023-08-05 05:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Здесь нужно ввести название ингредиента.",
                        max_length=64,
                        verbose_name="Название ингредиента.",
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(
                        help_text="Здесь нужно ввести измерительную величину.",
                        max_length=16,
                        verbose_name="Измерительная величина.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="Здесь нужно добавить изображение.",
                        upload_to="recipes/images/",
                        verbose_name="Изображение.",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Здесь нужно ввести название рецепта.",
                        max_length=200,
                        verbose_name="Название рецепта.",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Здесь нужно ввести текст рецепта.",
                        verbose_name="Описание рецепта.",
                    ),
                ),
                (
                    "cooking_time",
                    models.PositiveIntegerField(
                        help_text="Здесь нужно ввести время приготовления.",
                        verbose_name="Время приготовления.",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата публикации"
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        help_text="Здесь нужно выбрать имя автора.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ["-pub_date"],
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Здесь нужно задать имя тэга.",
                        max_length=200,
                        verbose_name="Имя тэга.",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        help_text="Здесь нужно задать цвет тэга в HEX.",
                        max_length=7,
                        verbose_name="Цвет тэга в HEX.",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Здесь нужно задать уникальный слаг тэга.",
                        max_length=200,
                        unique=True,
                        verbose_name="Слаг тэга",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тэг",
                "verbose_name_plural": "Тэги",
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_cart",
                        to="recipes.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_cart",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Корзина продуктов",
                "verbose_name_plural": "Корзина продуктов",
            },
        ),
        migrations.CreateModel(
            name="RecipeIngredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveIntegerField(verbose_name="Количество ингредиента."),
                ),
                (
                    "ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_ingredients",
                        to="recipes.ingredient",
                        verbose_name="Ингредиенты.",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_ingredients",
                        to="recipes.recipe",
                        verbose_name="Рецепт.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиенты для рецепта",
                "verbose_name_plural": "Ингредиенты для рецепта",
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                help_text="Здесь нужно выбрать ингредиенты.",
                related_name="recipes",
                through="recipes.RecipeIngredient",
                to="recipes.Ingredient",
                verbose_name="Ингредиенты",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                help_text="Здесь нужно выбрать тэги.",
                related_name="recipes",
                to="recipes.Tag",
                verbose_name="Тэги.",
            ),
        ),
        migrations.CreateModel(
            name="FavoriteRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="recipes.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Любимый рецепт",
                "verbose_name_plural": "Любимые рецепты",
            },
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_cart_recipe_for_user"
            ),
        ),
        migrations.AddConstraint(
            model_name="favoriterecipe",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite_recipe_for_user"
            ),
        ),
    ]