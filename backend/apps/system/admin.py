from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Permission, Role, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'first_name', 'last_name', 'department',
        'title', 'is_active', 'date_joined',
    ]
    list_filter = ['is_active', 'department', 'roles']
    search_fields = ['username', 'first_name', 'last_name', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('phone', 'department', 'title', 'avatar', 'roles'),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    filter_horizontal = ['permissions']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'module', 'action']
    list_filter = ['module', 'action']
    search_fields = ['name', 'code']
