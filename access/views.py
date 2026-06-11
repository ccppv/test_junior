from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from access.models import Permission, Role, UserRole
from access.permissions import IsAdmin
from access.serializers import (
    AssignRoleSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserRoleSerializer,
)
from users.permissions import IsAuthenticated


class PermissionListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        permissions_qs = Permission.objects.all().order_by('resource', 'action')
        serializer = PermissionSerializer(permissions_qs, many=True)
        return Response(serializer.data)


class RoleListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        roles = Role.objects.prefetch_related('permissions').all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, role_id):
        try:
            role = Role.objects.prefetch_related('permissions').get(id=role_id)
        except Role.DoesNotExist:
            return Response({'detail': 'Роль не найдена'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    def patch(self, request, role_id):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({'detail': 'Роль не найдена'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoleSerializer(role).data)


class UserRoleListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        user_roles = UserRole.objects.select_related('user', 'role').all()
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_role = serializer.save()
        return Response(
            UserRoleSerializer(user_role).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        if not user_id or not role_id:
            return Response(
                {'detail': 'Укажите user_id и role_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = UserRole.objects.filter(user_id=user_id, role_id=role_id).delete()
        if not deleted:
            return Response({'detail': 'Назначение не найдено'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
