from rest_framework import exceptions, permissions


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user is None or not getattr(request.user, 'is_authenticated', False):
            raise exceptions.NotAuthenticated('Требуется аутентификация')
        return True


class HasResourcePermission(permissions.BasePermission):
    message = 'Недостаточно прав для выполнения операции'

    def has_permission(self, request, view):
        if request.user is None or not getattr(request.user, 'is_authenticated', False):
            raise exceptions.NotAuthenticated('Требуется аутентификация')

        resource = getattr(view, 'resource', None)
        action = getattr(view, 'action_permission', None) or self._map_method(request.method)

        if not resource or not action:
            return False

        if not request.user.has_permission(resource, action):
            raise exceptions.PermissionDenied(self.message)

        return True

    @staticmethod
    def _map_method(method: str) -> str:
        mapping = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return mapping.get(method, 'read')
