from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

from .constants import SMALL_TEXT_AMOUNT


class Ingredient(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='Название ингредиента.',
        help_text='Здесь нужно ввести название ингредиента.',
    )
    measurement_unit = models.CharField(
        max_length=16,
        verbose_name='Измерительная величина.',
        help_text='Здесь нужно ввести измерительную величину.',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=SMALL_TEXT_AMOUNT,
        verbose_name='Имя тэга.',
        help_text='Здесь нужно задать имя тэга.'
    )
    color = ColorField(default='#FF0000')
    slug = models.SlugField(
        max_length=SMALL_TEXT_AMOUNT,
        unique=True,
        verbose_name='Слаг тэга',
        help_text='Здесь нужно задать уникальный слаг тэга.',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор.',
        related_name='recipes',
        help_text='Здесь нужно выбрать имя автора.',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Здесь нужно выбрать ингредиенты.',
        through='RecipeIngredient',
        through_fields=(
            'recipe',
            'ingredient'
        )
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги.',
        help_text='Здесь нужно выбрать тэги.'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение.',
        help_text='Здесь нужно добавить изображение.',
    )
    name = models.CharField(
        max_length=SMALL_TEXT_AMOUNT,
        verbose_name='Название рецепта.',
        help_text='Здесь нужно ввести название рецепта.',
    )
    text = models.TextField(
        verbose_name='Описание рецепта.',
        help_text='Здесь нужно ввести текст рецепта.',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(
            limit_value=1,
            message='Готовить меньше минуты - значит есть сырым!'
        )],
        verbose_name='Время приготовления.',
        help_text='Здесь нужно ввести время приготовления.',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт.',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты.',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(
            limit_value=1, message='Количество должно быть больше 0.'
        )],
        verbose_name='Количество ингредиента.',
    )

    class Meta:
        verbose_name = 'Ингредиенты для рецепта'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe_for_user'
            ),
        )
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe_for_user'
            ),
        )
        verbose_name = 'Корзина продуктов'
        verbose_name_plural = verbose_name
