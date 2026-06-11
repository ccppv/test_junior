from django.core.management.base import BaseCommand

from access.models import Permission, Role, RolePermission, UserRole
from users.models import User


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми пользователями, ролями и разрешениями'

    def handle(self, *args, **options):
        self.stdout.write('Создание разрешений...')

        permissions_data = [
            ('orders:read', 'orders', 'read', 'Просмотр заказов'),
            ('orders:create', 'orders', 'create', 'Создание заказов'),
            ('orders:update', 'orders', 'update', 'Изменение заказов'),
            ('orders:delete', 'orders', 'delete', 'Удаление заказов'),
            ('products:read', 'products', 'read', 'Просмотр товаров'),
            ('products:create', 'products', 'create', 'Создание товаров'),
            ('reports:read', 'reports', 'read', 'Просмотр отчётов'),
            ('access:manage', 'access', 'manage', 'Управление ролями и правами'),
        ]

        permissions = {}
        for codename, resource, action, description in permissions_data:
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'resource': resource,
                    'action': action,
                    'description': description,
                },
            )
            permissions[codename] = perm

        self.stdout.write('Создание ролей...')

        roles_data = {
            'admin': list(permissions.values()),
            'manager': [
                permissions['orders:read'],
                permissions['orders:create'],
                permissions['orders:update'],
                permissions['products:read'],
                permissions['reports:read'],
            ],
            'viewer': [
                permissions['orders:read'],
                permissions['products:read'],
                permissions['reports:read'],
            ],
            'user': [],
        }

        roles = {}
        for role_name, perms in roles_data.items():
            role, _ = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': f'Роль {role_name}'},
            )
            RolePermission.objects.filter(role=role).delete()
            for perm in perms:
                RolePermission.objects.create(role=role, permission=perm)
            roles[role_name] = role

        self.stdout.write('Создание пользователей...')

        users_data = [
            ('admin@example.com', 'admin123', 'Иван', 'Админов', 'Иванович', 'admin'),
            ('manager@example.com', 'manager123', 'Пётр', 'Менеджеров', '', 'manager'),
            ('viewer@example.com', 'viewer123', 'Анна', 'Наблюдателева', '', 'viewer'),
            ('user@example.com', 'user123', 'Сергей', 'Пользователев', '', 'user'),
        ]

        for email, password, first_name, last_name, patronymic, role_name in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'patronymic': patronymic,
                },
            )
            if created:
                user.set_password(password)
                user.save()
            UserRole.objects.get_or_create(user=user, role=roles[role_name])
            self.stdout.write(f'  {email} / {password} -> {role_name}')

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
