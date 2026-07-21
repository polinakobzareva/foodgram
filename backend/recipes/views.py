from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    IngredientSerializer, RecipeMinifiedSerializer,
    RecipeSerializer, TagSerializer
)
from .models import (Favorite, Recipe, Tag,
                     Ingredient, RecipeIngredient,
                     ShoppingCart)
from foodgram.permissions import AuthorCheckMixin
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return super().get_queryset()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(AuthorCheckMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeMixin:
    model = None
    serializer_class = None

    def get_recipe(self, pk):
        return get_object_or_404(Recipe, pk=pk)

    def post(self, request, pk):
        recipe = self.get_recipe(pk)
        _, created = self.model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(
            recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = self.get_recipe(pk)
        deleted, _ = self.model.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(RecipeMixin, APIView):
    model = Favorite
    serializer_class = RecipeMinifiedSerializer


class ShoppingCartView(RecipeMixin, APIView):
    model = ShoppingCart
    serializer_class = RecipeMinifiedSerializer


@api_view(['GET'])
def download_shopping_cart_view(request):
    cart_items = ShoppingCart.objects.filter(user=request.user)
    ingredients = {}
    for item in cart_items:
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=item.recipe
        ).select_related('ingredient')
        for i in recipe_ingredients:
            key = f'{i.ingredient.name} ({i.ingredient.measurement_unit})'
            if key in ingredients:
                ingredients[key] += i.amount
            else:
                ingredients[key] = i.amount
    text = ''
    for name, amount in ingredients.items():
        text += f'{name} — {amount}\n'
    return Response({'shopping_list': text})


@api_view(['GET'])
def get_link_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    short_link = request.build_absolute_uri(f'/s/{recipe.short_id}')
    return Response({'short-link': short_link})
