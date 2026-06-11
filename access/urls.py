from django.urls import path

from access.views import (
    PermissionListView,
    RoleDetailView,
    RoleListView,
    UserRoleListView,
)

urlpatterns = [
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/<int:role_id>/', RoleDetailView.as_view(), name='role-detail'),
    path('user-roles/', UserRoleListView.as_view(), name='user-role-list'),
]
