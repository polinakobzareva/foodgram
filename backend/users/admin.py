from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    search_fields = ('email', 'username')
    fieldsets = UserAdmin.fieldsets + (
        ('Аватарка', {'fields': ('avatar',)}),
    )
