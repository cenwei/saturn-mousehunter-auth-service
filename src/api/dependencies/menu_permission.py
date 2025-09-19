"""
认证服务 - 菜单权限验证中间件
"""
from typing import List, Callable
from functools import wraps

from fastapi import HTTPException, status
from saturn_mousehunter_shared.log.logger import get_logger
from application.services.menu_permission_service import MenuPermissionService
from domain.models.auth_user_role import UserType

log = get_logger(__name__)


def require_menu_permission(menu_permission: str):
    """
    菜单权限验证装饰器

    Args:
        menu_permission: 菜单权限编码，如 'menu:dashboard'
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中提取current_user（通过Depends注入）
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证用户"
                )

            # 检查菜单权限
            user_permissions = current_user.get('permissions', [])
            if menu_permission not in user_permissions:
                log.warning(
                    f"User {current_user.get('user_id')} denied access to menu "
                    f"requiring permission: {menu_permission}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少菜单访问权限: {menu_permission}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_menu_permissions(menu_permissions: List[str]):
    """
    多菜单权限验证装饰器

    Args:
        menu_permissions: 菜单权限编码列表
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证用户"
                )

            user_permissions = set(current_user.get('permissions', []))
            missing_permissions = []

            for permission in menu_permissions:
                if permission not in user_permissions:
                    missing_permissions.append(permission)

            if missing_permissions:
                log.warning(
                    f"User {current_user.get('user_id')} missing menu permissions: "
                    f"{missing_permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少菜单访问权限: {', '.join(missing_permissions)}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_menu_permission(menu_permissions: List[str]):
    """
    任意菜单权限验证装饰器（满足其中一个即可）

    Args:
        menu_permissions: 菜单权限编码列表
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证用户"
                )

            user_permissions = set(current_user.get('permissions', []))

            # 检查是否有任意一个权限
            has_permission = any(perm in user_permissions for perm in menu_permissions)

            if not has_permission:
                log.warning(
                    f"User {current_user.get('user_id')} missing any of menu permissions: "
                    f"{menu_permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少以下任意菜单访问权限: {', '.join(menu_permissions)}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


class MenuAccessValidator:
    """菜单访问验证器"""

    def __init__(self, menu_service: MenuPermissionService):
        self.menu_service = menu_service

    async def validate_menu_access(
        self,
        user_id: str,
        user_type: str,
        menu_id: str
    ) -> bool:
        """验证用户是否有菜单访问权限"""
        try:
            result = await self.menu_service.validate_menu_access(
                user_id,
                UserType(user_type),
                menu_id
            )
            return result.has_permission
        except Exception as e:
            log.error(f"Menu access validation failed: {str(e)}")
            return False

    async def validate_path_access(
        self,
        user_id: str,
        user_type: str,
        path: str
    ) -> bool:
        """根据路径验证菜单访问权限"""
        try:
            menu = self.menu_service.get_menu_by_path(path)
            if not menu:
                log.warning(f"Menu not found for path: {path}")
                return False

            if not menu.permission:
                # 无权限要求的菜单允许访问
                return True

            return await self.validate_menu_access(user_id, user_type, menu.id)
        except Exception as e:
            log.error(f"Path access validation failed: {str(e)}")
            return False


def create_menu_validator_dependency(menu_service: MenuPermissionService):
    """创建菜单验证器依赖"""
    validator = MenuAccessValidator(menu_service)

    def get_menu_validator() -> MenuAccessValidator:
        return validator

    return get_menu_validator