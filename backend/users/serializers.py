from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Subscription
from users.models import MyUser


class SignUpSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = MyUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class MeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = MyUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        if not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()
