from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    avatar = models.ImageField(upload_to='users/avatars/',
                               blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
