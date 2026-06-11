from rest_framework import exceptions, permissions


class IsAdmin(permissions.BasePermission):
    message = 'Доступ только для администратора'

    def has_permission(self, request, view):
        if request.user is None or not getattr(request.user, 'is_authenticated', False):
            raise exceptions.NotAuthenticated('Требуется аутентификация')

        if not request.user.user_roles.filter(role__name='admin').exists():
            raise exceptions.PermissionDenied(self.message)

        return True
