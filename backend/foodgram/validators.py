from rest_framework import serializers

from foodgram import constants


def validate_cooking_time(value):
    if int(value) < constants.TIME_MIN:
        raise serializers.ValidationError(
            f'Время не может быть меньше {constants.TIME_MIN}'
        )
    return value


def validate_ingredients(value):
    if not value:
        raise serializers.ValidationError('Добавте хотя бы один ингредиент')
    ids = [item['id'] for item in value]
    if len(ids) != len(set(ids)):
        raise serializers.ValidationError('Ингредиенты не должны повторяться')
    for item in value:
        if int(item.get('amount', 0)) < constants.INGREDIENTS_MIN:
            raise serializers.ValidationError(
                f'Количество не может быть меньше {constants.INGREDIENTS_MIN}')
    return value
