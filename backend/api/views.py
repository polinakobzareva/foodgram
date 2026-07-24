from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.fields import Base64ImageField
from recipes.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FoodgramUserSerializer,
    IngredientSerializer,
    RecipeMinifiedSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.models import User


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (AllowAny(),)
        return super().get_permissions()

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        if request.method == 'PUT':
            field = Base64ImageField()
            request.user.avatar = field.to_internal_value(
                request.data.get('avatar'))
            request.user.save()
            return Response({'avatar': request.user.avatar.url})
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        authors = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = FoodgramUserSerializer(page,
                                                many=True,
                                                context={'request': request})
            data = serializer.data
            for item in data:
                item['recipes'] = []
                item['recipes_count'] = 0
            return self.get_paginated_response(data)
        serializer = FoodgramUserSerializer(authors,
                                            many=True,
                                            context={'request': request})
        data = serializer.data
        for item in data:
            item['recipes'] = []
            item['recipes_count'] = 0
        return Response(data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if request.user == author:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            _, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = FoodgramUserSerializer(author,
                                                context={'request': request})
            data = serializer.data
            data['recipes'] = []
            data['recipes_count'] = 0
            return Response(data, status=status.HTTP_201_CREATED)
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=author
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return super().get_queryset()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to_relation(self, request, model, pk):
        recipe = self.get_object()
        _, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeMinifiedSerializer(recipe,
                                              context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_relation(self, request, model, pk):
        recipe = self.get_object()
        deleted, _ = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(request, Favorite, pk)
        return self._remove_from_relation(request, Favorite, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(request, ShoppingCart, pk)
        return self._remove_from_relation(request, ShoppingCart, pk)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).select_related('ingredient')

        shopping_list = {}
        for item in recipe_ingredients:
            name = item.ingredient.name
            unit = item.ingredient.measurement_unit
            key = f'{name} ({unit})'
            if key in shopping_list:
                shopping_list[key] += item.amount
            else:
                shopping_list[key] = item.amount

        text = ''
        for key in sorted(shopping_list):
            text += f'{key} — {shopping_list[key]}\n'
        response = HttpResponse('\n'.join(text), content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(
            reverse('short-link', kwargs={'short_id': recipe.short_id})
        )
        return Response({'short-link': short_link})

    @action(detail=False, methods=['get'], url_path='s/<str:short_id>')
    def redirect_short_link(self, request, short_id=None):
        recipe = get_object_or_404(Recipe, short_id=short_id)
        serializer = RecipeReadSerializer(recipe, context={'request': request})
        return Response(serializer.data)
