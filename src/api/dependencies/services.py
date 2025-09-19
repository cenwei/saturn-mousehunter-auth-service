"""
认证服务 - 服务层依赖注入
"""
from fastapi import Depends
from application.services import AdminUserService, TenantUserService
from application.services.role_service import RoleService
from application.services.permission_service import PermissionService
from application.services.menu_permission_service import MenuPermissionService
from application.utils import JWTUtils
from infrastructure.repositories import AdminUserRepo, TenantUserRepo, UserRoleRepo, AuditLogRepo, RoleRepo, PermissionRepo
from infrastructure.config import get_jwt_config
from api.dependencies.dao import get_dao


async def get_tenant_user_repo() -> TenantUserRepo:
    """获取租户用户仓库"""
    dao = get_dao()
    return TenantUserRepo(dao)


async def get_admin_user_repo() -> AdminUserRepo:
    """获取管理员用户仓库"""
    dao = get_dao()
    return AdminUserRepo(dao)


async def get_user_role_repo() -> UserRoleRepo:
    """获取用户角色仓库"""
    dao = get_dao()
    return UserRoleRepo(dao)


async def get_audit_log_repo() -> AuditLogRepo:
    """获取审计日志仓库"""
    dao = get_dao()
    return AuditLogRepo(dao)


async def get_role_repo() -> RoleRepo:
    """获取角色仓库"""
    dao = get_dao()
    return RoleRepo(dao)


async def get_permission_repo() -> PermissionRepo:
    """获取权限仓库"""
    dao = get_dao()
    return PermissionRepo(dao)


async def get_jwt_utils() -> JWTUtils:
    """获取JWT工具"""
    jwt_config = get_jwt_config()
    return JWTUtils(jwt_config)


async def get_admin_user_service(
    admin_user_repo: AdminUserRepo = Depends(get_admin_user_repo),
    user_role_repo: UserRoleRepo = Depends(get_user_role_repo),
    audit_log_repo: AuditLogRepo = Depends(get_audit_log_repo),
    jwt_utils: JWTUtils = Depends(get_jwt_utils),
) -> AdminUserService:
    """获取管理员用户服务"""
    return AdminUserService(
        admin_user_repo=admin_user_repo,
        user_role_repo=user_role_repo,
        audit_log_repo=audit_log_repo,
        jwt_utils=jwt_utils
    )


async def get_tenant_user_service(
    tenant_user_repo: TenantUserRepo = Depends(get_tenant_user_repo),
    user_role_repo: UserRoleRepo = Depends(get_user_role_repo),
    audit_log_repo: AuditLogRepo = Depends(get_audit_log_repo),
    jwt_utils: JWTUtils = Depends(get_jwt_utils),
) -> TenantUserService:
    """获取租户用户服务"""
    return TenantUserService(
        tenant_user_repo=tenant_user_repo,
        user_role_repo=user_role_repo,
        audit_log_repo=audit_log_repo,
        jwt_utils=jwt_utils
    )


async def get_role_service(
    role_repo: RoleRepo = Depends(get_role_repo),
    audit_log_repo: AuditLogRepo = Depends(get_audit_log_repo),
) -> RoleService:
    """获取角色服务"""
    return RoleService(
        role_repo=role_repo,
        audit_repo=audit_log_repo
    )


async def get_permission_service(
    permission_repo: PermissionRepo = Depends(get_permission_repo),
    audit_log_repo: AuditLogRepo = Depends(get_audit_log_repo),
) -> PermissionService:
    """获取权限服务"""
    return PermissionService(
        permission_repo=permission_repo,
        audit_repo=audit_log_repo
    )


async def get_menu_permission_service(
    user_role_repo: UserRoleRepo = Depends(get_user_role_repo),
) -> MenuPermissionService:
    """获取菜单权限服务"""
    return MenuPermissionService(
        user_role_repo=user_role_repo
    )