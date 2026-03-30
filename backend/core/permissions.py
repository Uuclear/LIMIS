from __future__ import annotations

from typing import Any, Sequence

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class LimsModulePermission(BasePermission):
    """
    在 ViewSet 上设置 `lims_module = 'commission'` 等，按 HTTP 方法映射到
    view/create/edit/delete；对 @action 可通过 `lims_action_permission` 覆盖。
    未设置 lims_module 时仅校验登录（兼容旧接口）。
    """

    message = '无此模块操作权限'

    _method_action: dict[str, str] = {
        'GET': 'view',
        'HEAD': 'view',
        'OPTIONS': 'view',
        'POST': 'create',
        'PUT': 'edit',
        'PATCH': 'edit',
        'DELETE': 'delete',
    }

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, 'is_superuser', False):
            return True

        module = getattr(view, 'lims_module', None)
        if not module:
            return True

        action_override = getattr(view, 'lims_action_permission', None)
        if action_override:
            action = action_override
        else:
            va = getattr(view, 'action', None)
            mapped = getattr(view, 'lims_action_map', None) or {}
            if isinstance(mapped, dict) and va in mapped:
                action = mapped[va]
            elif request.method in self._method_action:
                action = self._method_action[request.method]
            else:
                action = 'view'

        if hasattr(request.user, 'has_lims_permission'):
            return bool(request.user.has_lims_permission(module, action))
        return False


class IsAuthenticated(BasePermission):
    message = '请先登录'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated)


class RoleBasedPermission(BasePermission):
    """
    Set `required_roles` on the view, e.g. required_roles = ['admin', 'lab_manager'].
    Superusers always pass.
    """
    message = '角色权限不足'

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        required_roles: Sequence[str] = getattr(view, 'required_roles', [])
        if not required_roles:
            return True

        user_roles = self._get_user_roles(request.user)
        return bool(set(required_roles) & set(user_roles))

    def _get_user_roles(self, user: Any) -> list[str]:
        if hasattr(user, 'roles'):
            return [r.code if hasattr(r, 'code') else str(r) for r in user.roles.all()]
        if hasattr(user, 'role'):
            return [user.role] if isinstance(user.role, str) else [str(user.role)]
        return []


class ModulePermission(BasePermission):
    """
    Set `module_code` and optional `action_map` on the view.
    action_map defaults to HTTP-method -> action string mapping.
    """
    message = '无此模块操作权限'

    default_action_map: dict[str, str] = {
        'GET': 'view',
        'POST': 'add',
        'PUT': 'change',
        'PATCH': 'change',
        'DELETE': 'delete',
    }

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        module_code: str | None = getattr(view, 'module_code', None)
        if not module_code:
            return True

        action_map: dict[str, str] = getattr(view, 'action_map', self.default_action_map)
        action = action_map.get(request.method, 'view')

        return self._check_permission(request.user, module_code, action)

    def _check_permission(self, user: Any, module: str, action: str) -> bool:
        if hasattr(user, 'has_module_permission'):
            return user.has_module_permission(module, action)

        perm_string = f'{module}.{action}'
        return user.has_perm(perm_string)
