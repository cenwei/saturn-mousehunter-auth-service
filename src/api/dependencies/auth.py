"""
认证服务 - FastAPI依赖项
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from application.utils import JWTUtils
from infrastructure.config import get_jwt_config

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前认证用户"""
    jwt_config = get_jwt_config()
    jwt_utils = JWTUtils(jwt_config)

    token = credentials.credentials
    user_info = jwt_utils.extract_user_info(token)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_info


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[dict]:
    """获取当前认证用户（可选，不会抛出异常）"""
    if not credentials:
        return None

    jwt_config = get_jwt_config()
    jwt_utils = JWTUtils(jwt_config)

    try:
        token = credentials.credentials
        user_info = jwt_utils.extract_user_info(token)
        return user_info
    except Exception:
        return None


async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """获取管理员用户"""
    if current_user.get("user_type") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


async def get_tenant_user(current_user: dict = Depends(get_current_user)) -> dict:
    """获取租户用户"""
    if current_user.get("user_type") != "TENANT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要租户用户权限"
        )
    return current_user


def require_permissions(required_permissions: List[str]):
    """要求特定权限"""
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        user_permissions = set(current_user.get("permissions", []))
        required_perms = set(required_permissions)

        if not required_perms.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user

    return permission_checker


def require_roles(required_roles: List[str]):
    """要求特定角色"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_roles = set(current_user.get("roles", []))
        required_role_set = set(required_roles)

        if not required_role_set.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="角色权限不足"
            )
        return current_user

    return role_checker