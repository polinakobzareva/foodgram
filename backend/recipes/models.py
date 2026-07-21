from django.contrib.auth import get_user_model

from django.db import models
import uuid
from foodgram.constants import (
    TAG_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    short_id = models.CharField(max_length=8, unique=True, blank=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = uuid.uuid4().hex[:6]
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'


class Favorite(models.Model):
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
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'


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
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
