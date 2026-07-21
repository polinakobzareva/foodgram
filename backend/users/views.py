from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from recipes.models import Subscription
from recipes.serializers import Base64ImageField
from .models import MyUser
from .serializers import MeSerializer, SignUpSerializer


class MyUserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return SignUpSerializer
        return MeSerializer


@api_view(['PUT', 'DELETE'])
def avatar_view(request):
    if request.method == 'PUT':
        field = Base64ImageField()
        request.user.avatar = field.to_internal_value(
            request.data.get('avatar'))
        request.user.save()
        return Response({'avatar': request.user.avatar.url})
    request.user.avatar.delete(save=True)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def subscriptions_view(request):
    subs = request.user.subscriptions.all()
    authors = [sub.author for sub in subs]
    serializer = MeSerializer(authors, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST', 'DELETE'])
def subscribe_view(request, pk):
    author = get_object_or_404(MyUser, pk=pk)
    if request.method == 'POST':
        if request.user == author:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        _, created = Subscription.objects.get_or_create(
            user=request.user,
            author=author
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = MeSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    deleted, _ = Subscription.objects.filter(
        user=request.user,
        author=author
    ).delete()
    if not deleted:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)
