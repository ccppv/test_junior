from rest_framework import exceptions, permissions


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user is None or not getattr(request.user, 'is_authenticated', False):
            raise exceptions.NotAuthenticated('Требуется аутентификация')
        return True
