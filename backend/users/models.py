from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import EMAIL_MAX_LENGTH, USER_NAME_MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True,
                              verbose_name='Электронная почта')
    avatar = models.ImageField(upload_to='users/avatars/',
                               blank=True, null=True,
                               verbose_name='Аватарка')
    first_name = models.CharField(max_length=USER_NAME_MAX_LENGTH,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=USER_NAME_MAX_LENGTH,
                                 verbose_name='Фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
