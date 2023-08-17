from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientInLine,
    ]
    list_display = (
        'name',
        'author',
        'get_ingredients',
        'favorite',
    )
    search_fields = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(
        description='количество избранных',
    )
    def favorite(self, obj):
        return obj.favorites.count()

    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    get_ingredients.short_description = 'Ингредиенты'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        form.save_m2m()
        if not form.cleaned_data.get('ingredients'):
            super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    search_fields = ('title',)
    empty_value_display = '-пусто-'
