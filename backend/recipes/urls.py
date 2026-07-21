from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteView,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartView,
    TagViewSet,
    download_shopping_cart_view,
    get_link_view,
)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart_view),
    path('', include(router.urls)),
    path('recipes/<int:pk>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartView.as_view()),
    path('recipes/<int:pk>/get-link/', get_link_view),
]
