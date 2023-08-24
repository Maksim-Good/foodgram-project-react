from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers, validators
from users.models import Subscribe, User

from .utils import add_ingredients, is_int_and_more_than_zero


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriber.filter(subscrubing=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit',)
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('__all__')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer(read_only=True,)
    ingredients = serializers.SerializerMethodField(read_only=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values()
        for ingredient in ingredients:
            amount = get_object_or_404(
                RecipeIngredient,
                ingredient=ingredient['id'],
                recipe=obj
            ).amount
            ingredient['amount'] = amount
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_anonymous or user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_anonymous
            or user.shopping_cart.filter(recipe=obj).exists()
        )


class CreateRecipeSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta:
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe

    def validate(self, attrs):
        cooking_time = self.initial_data.get('cooking_time')
        is_int_and_more_than_zero(cooking_time, 'время готовки')
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients or not tags:
            raise ValidationError('Неполные данные.')
        ingrs = []
        for ingr in ingredients:
            ingr_id = ingr['id']
            if not Ingredient.objects.filter(id=ingr_id).exists():
                raise ValidationError('Несуществующий ингредиент.')
            is_int_and_more_than_zero(ingr['amount'], 'количество ингридиента')
            if ingr_id in ingrs:
                raise ValidationError('Нельзя добавлять один элемент дважды!')
            ingrs.append(ingr_id)
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists:
                raise ValidationError('Несуществующий тег.')
        attrs['ingredients'] = ingredients
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.add(*tags)
        add_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.add(*tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        add_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(instance, context={'request': request}).data


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('__all__')
        model = ShoppingCart
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок.'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('__all__')
        model = FavoriteRecipe
        validators = [
            validators.UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке избранного.'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class UserSubsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Subscribe
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'subscrubing'),
                message='Вы уже подписаны на этого пользователя!'
            )
        ]

    def validate(self, attrs):
        if attrs['user'] == attrs['subscrubing']:
            raise ValidationError('На себя подписываться нельзя!')
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubsListSerializer(
            instance.subscrubing,
            context={'request': request}
        ).data


class UserSubsListSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        return ShortRecipeSerializer(obj.recipes.all(), many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return request.user.subscriber.filter(subscrubing=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()
