from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, RecipeIngredient
from rest_framework import status
from rest_framework.response import Response


def add_ingredients(ingredients, instance):
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(
            Ingredient,
            id=ingredient['id']
        )
        RecipeIngredient.objects.create(
            ingredient=current_ingredient,
            recipe=instance,
            amount=ingredient['amount']
        )


def create_object(serializer_name, request, obj, recipe='recipe'):
    serializer = serializer_name(
        data={'user': request.user.id, recipe: obj.id},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_object(model_name, request, recipe, error_message):
    if not model_name.objects.filter(
        user=request.user,
        recipe=recipe
    ).exists():
        return Response(
            {'errors': error_message}, status=status.HTTP_400_BAD_REQUEST
        )
    model_name.objects.filter(user=request.user, recipe=recipe).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)