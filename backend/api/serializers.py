from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from foodgram.constants import (INGREDIENTS_MIN, TAG_MIN, TIME_MIN)
from recipes.models import (Ingredient, Recipe,
                            RecipeIngredient, Tag)


User = get_user_model()


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.subscribers.filter(author=obj).exists())


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=INGREDIENTS_MIN)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.favorites.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.shopping_carts.filter(user=request.user).exists())

    def get_ingredients(self, obj):
        ingredients = obj.recipeingredient_set.select_related('ingredient')
        return [{
            'id': item.ingredient.id,
            'name': item.ingredient.name,
            'measurement_unit': item.ingredient.measurement_unit,
            'amount': item.amount
        } for item in ingredients]


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=TIME_MIN)
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'image', 'name',
                  'text', 'cooking_time', 'ingredients')

    def validate(self, data):
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                {'tags': f'Нужен хотя бы {TAG_MIN} тег'})
        if len(tags) != len(set(tag.id for tag in tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'})
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': f'Нужен хотя бы {INGREDIENTS_MIN} ингредиент'})
        ids = [item['id'] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться'})
        return data

    def validate_image(self, value):
        if self.instance is None and not value:
            raise serializers.ValidationError('Нужна картинка')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.recipeingredient_set.all().delete()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients_data
        )


class SubscriptionSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + ('recipes',
                                                       'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        if request:
            limit = request.query_params.get('recipes_limit')
            if limit:
                try:
                    limit = int(limit)
                    recipes = recipes[:limit]
                except (ValueError, TypeError):
                    pass
        return RecipeMinifiedSerializer(recipes, many=True,
                                        context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
