from django.contrib import admin
from .models import (RecipeIngredient, Tag,
                     Favorite, Ingredient, Recipe,
                     ShoppingCart, Subscription)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)

    def favorite_count(self, obj):
        return obj.favorites.count()
    favorite_count.short_description = 'Количество добавивших в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
