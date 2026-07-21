from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from .views import (MyUserViewSet,
                    avatar_view, subscribe_view, subscriptions_view)

router = DefaultRouter()
router.register('users', MyUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/avatar/', avatar_view),
    path('users/subscriptions/', subscriptions_view),
    path('users/<int:pk>/subscribe/', subscribe_view),
]
