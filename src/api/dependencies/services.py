"""
认证服务 - 服务层依赖注入
"""
from fastapi import Depends
from application.services import AdminUserService, TenantUserService
from application.utils import JWTUtils
from infrastructure.repositories import AdminUserRepo, TenantUserRepo, UserRoleRepo, AuditLogRepo
from infrastructure.config import get_jwt_config
from infrastructure.config import get_app_config


async def get_tenant_user_repo() -> TenantUserRepo:
    """获取租户用户仓库"""
    config = get_app_config()
    return TenantUserRepo(config.database_url)


async def get_admin_user_repo() -> AdminUserRepo:
    """获取管理员用户仓库"""
    config = get_app_config()
    return AdminUserRepo(config.database_url)


async def get_user_role_repo() -> UserRoleRepo:
    """获取用户角色仓库"""
    config = get_app_config()
    return UserRoleRepo(config.database_url)


async def get_audit_log_repo() -> AuditLogRepo:
    """获取审计日志仓库"""
    config = get_app_config()
    return AuditLogRepo(config.database_url)


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