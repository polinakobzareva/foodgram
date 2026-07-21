from rest_framework.exceptions import PermissionDenied


class AuthorCheckMixin:
    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Невозможно изменить(чужой рецепт)')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Невозможно удалить(чужой рецепт')
        instance.delete()
