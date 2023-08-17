from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer, UserSubsCreateSerializer,
                          UserSubsListSerializer)
from .utils import create_object, delete_object


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subscribes = self.paginate_queryset(
            User.objects.filter(subscrubing__user=request.user)
        )
        return self.get_paginated_response(
            UserSubsListSerializer(subscribes, many=True).data
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = get_object_or_404(User, id=id)
        if request.method == 'POST':
            return create_object(
                UserSubsCreateSerializer, request, user, 'subscrubing'
            )

        if request.method == 'DELETE':
            error_message = 'Вы не подписаны на этого пользователя.'
            if not Subscribe.objects.filter(
                user=request.user,
                subscrubing=user
            ).exists():
                return Response(
                    {'errors': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.filter(
                user=request.user,
                subscrubing=user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AuthorOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AuthorOrReadOnly, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    create_serializer_class = CreateRecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return self.serializer_class
        return self.create_serializer_class

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_object(ShoppingCartSerializer, request, recipe)

        if request.method == 'DELETE':
            error_message = 'В списке покупок нет этого рецепта'
            return delete_object(ShoppingCart, request, recipe, error_message)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        wishlist = ['Список покупок: \n']
        for ingredient in ingredients:
            name = ingredient.get('ingredient__name')
            unit = ingredient.get('ingredient__measurement_unit')
            amount = ingredient.get('amount')
            wishlist.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(wishlist, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_object(FavoriteSerializer, request, recipe)

        if request.method == 'DELETE':
            error_message = 'Этот рецепт не в избранном.'
            return delete_object(
                FavoriteRecipe, request, recipe, error_message
            )
