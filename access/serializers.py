from rest_framework import serializers

from access.models import Permission, Role, RolePermission, UserRole
from users.models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'resource', 'action', 'description']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_ids']

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance = super().update(instance, validated_data)

        if permission_ids is not None:
            RolePermission.objects.filter(role=instance).delete()
            for perm_id in permission_ids:
                RolePermission.objects.create(role=instance, permission_id=perm_id)

        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_email', 'role', 'role_name']


class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate(self, attrs):
        if not User.objects.filter(id=attrs['user_id'], is_active=True).exists():
            raise serializers.ValidationError({'user_id': 'Пользователь не найден'})
        if not Role.objects.filter(id=attrs['role_id']).exists():
            raise serializers.ValidationError({'role_id': 'Роль не найдена'})
        return attrs

    def create(self, validated_data):
        user_role, _ = UserRole.objects.get_or_create(
            user_id=validated_data['user_id'],
            role_id=validated_data['role_id'],
        )
        return user_role
