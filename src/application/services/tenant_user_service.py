"""
认证服务 - 租户用户服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from saturn_mousehunter_shared.aop.decorators import measure
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.repositories import TenantUserRepo, UserRoleRepo, AuditLogRepo
from domain.models.auth_tenant_user import (
    TenantUserIn, TenantUserOut, TenantUserUpdate, TenantUserQuery,
    TenantUserLogin, TenantUserResponse
)
from domain.models.auth_user_role import UserType
from application.utils import PasswordUtils, JWTUtils

log = get_logger(__name__)


class TenantUserService:
    """租户用户服务"""

    def __init__(self,
                 tenant_user_repo: TenantUserRepo,
                 user_role_repo: UserRoleRepo,
                 audit_log_repo: AuditLogRepo,
                 jwt_utils: JWTUtils):
        self.tenant_user_repo = tenant_user_repo
        self.user_role_repo = user_role_repo
        self.audit_log_repo = audit_log_repo
        self.jwt_utils = jwt_utils

    @measure("service_tenant_user_create_seconds")
    async def create_tenant_user(self, user_data: TenantUserIn, created_by: str = None) -> TenantUserOut:
        """创建租户用户"""
        # 检查租户内用户名是否已存在
        existing_user = await self.tenant_user_repo.get_by_username(
            user_data.tenant_id, user_data.username
        )
        if existing_user:
            raise ValueError(f"租户内用户名 '{user_data.username}' 已存在")

        # 检查租户内邮箱是否已存在
        existing_email = await self.tenant_user_repo.get_by_email(
            user_data.tenant_id, user_data.email
        )
        if existing_email:
            raise ValueError(f"租户内邮箱 '{user_data.email}' 已存在")

        # 验证密码强度
        if user_data.password:
            is_strong, errors = PasswordUtils.validate_password_strength(user_data.password)
            if not is_strong:
                raise ValueError(f"密码强度不足: {'; '.join(errors)}")

            # 哈希密码
            user_data.password_hash = PasswordUtils.hash_password(user_data.password)

        # 创建用户
        tenant_user = await self.tenant_user_repo.create(user_data)

        # 记录审计日志
        await self.audit_log_repo.create({
            "user_id": created_by,
            "user_type": UserType.ADMIN,  # 通常由管理员创建
            "action": "CREATE_TENANT_USER",
            "resource": "tenant_user",
            "resource_id": tenant_user.id,
            "details": {
                "tenant_id": tenant_user.tenant_id,
                "username": tenant_user.username,
                "email": tenant_user.email
            },
            "success": True
        })

        log.info(f"Created tenant user: {tenant_user.username} in tenant: {tenant_user.tenant_id}")
        return tenant_user

    @measure("service_tenant_user_authenticate_seconds")
    async def authenticate(self, login_data: TenantUserLogin,
                          ip_address: str = None, user_agent: str = None) -> Optional[TenantUserResponse]:
        """租户用户认证"""
        # 支持用户名或邮箱登录
        tenant_user = None

        # 先尝试用户名
        if "@" not in login_data.username:
            tenant_user = await self.tenant_user_repo.get_by_username(
                login_data.tenant_id, login_data.username
            )

        # 如果未找到，尝试邮箱
        if not tenant_user and "@" in login_data.username:
            tenant_user = await self.tenant_user_repo.get_by_email(
                login_data.tenant_id, login_data.username
            )

        # 验证用户存在且密码正确
        if not tenant_user or not PasswordUtils.verify_password(
            login_data.password, tenant_user.password_hash if hasattr(tenant_user, 'password_hash') else ""
        ):
            # 记录失败的登录尝试
            await self.audit_log_repo.log_login_attempt(
                user_id=tenant_user.id if tenant_user else None,
                user_type=UserType.TENANT.value,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="无效的用户名或密码"
            )
            return None

        # 检查用户是否激活
        if not tenant_user.is_active:
            await self.audit_log_repo.log_login_attempt(
                user_id=tenant_user.id,
                user_type=UserType.TENANT.value,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="用户账户已被停用"
            )
            return None

        # 获取用户权限
        user_permissions = await self.user_role_repo.get_user_permissions(
            tenant_user.id, UserType.TENANT
        )

        # 创建JWT令牌（包含租户信息）
        token_data = self.jwt_utils.create_token_pair(
            subject=f"{tenant_user.tenant_id}:{tenant_user.username}",
            user_type=UserType.TENANT.value,
            user_id=tenant_user.id,
            permissions=user_permissions.permissions,
            roles=user_permissions.roles,
            additional_claims={"tenant_id": tenant_user.tenant_id}
        )

        # 更新最后登录时间
        await self.tenant_user_repo.update_last_login(tenant_user.id)

        # 记录成功登录
        await self.audit_log_repo.log_login_attempt(
            user_id=tenant_user.id,
            user_type=UserType.TENANT.value,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )

        log.info(f"Tenant user authenticated: {tenant_user.username} in tenant: {tenant_user.tenant_id}")

        return TenantUserResponse(
            user=tenant_user,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"]
        )

    @measure("service_tenant_user_get_seconds")
    async def get_tenant_user(self, user_id: str) -> Optional[TenantUserOut]:
        """获取租户用户"""
        return await self.tenant_user_repo.get_by_id(user_id)

    @measure("service_tenant_user_get_by_username_seconds")
    async def get_by_username(self, tenant_id: str, username: str) -> Optional[TenantUserOut]:
        """根据租户ID和用户名获取租户用户"""
        return await self.tenant_user_repo.get_by_username(tenant_id, username)

    @measure("service_tenant_user_update_seconds")
    async def update_tenant_user(self, user_id: str, update_data: TenantUserUpdate,
                                updated_by: str = None) -> Optional[TenantUserOut]:
        """更新租户用户"""
        # 获取现有用户
        existing_user = await self.tenant_user_repo.get_by_id(user_id)
        if not existing_user:
            raise ValueError("用户不存在")

        # 如果更新邮箱，检查租户内邮箱是否被其他用户使用
        if update_data.email and update_data.email != existing_user.email:
            existing_email = await self.tenant_user_repo.get_by_email(
                existing_user.tenant_id, update_data.email
            )
            if existing_email and existing_email.id != user_id:
                raise ValueError(f"租户内邮箱 '{update_data.email}' 已被其他用户使用")

        # 如果更新密码，验证密码强度
        if update_data.password:
            is_strong, errors = PasswordUtils.validate_password_strength(update_data.password)
            if not is_strong:
                raise ValueError(f"密码强度不足: {'; '.join(errors)}")
            update_data.password_hash = PasswordUtils.hash_password(update_data.password)

        # 更新用户
        updated_user = await self.tenant_user_repo.update(user_id, update_data)

        if updated_user:
            # 记录审计日志
            changes = {k: v for k, v in update_data.dict(exclude_unset=True).items()
                      if k not in ['password', 'password_hash']}
            if update_data.password:
                changes['password_updated'] = True

            await self.audit_log_repo.create({
                "user_id": updated_by,
                "user_type": UserType.TENANT if updated_by == user_id else UserType.ADMIN,
                "action": "UPDATE_TENANT_USER",
                "resource": "tenant_user",
                "resource_id": user_id,
                "details": changes,
                "success": True
            })

            log.info(f"Updated tenant user: {user_id}")

        return updated_user

    @measure("service_tenant_user_delete_seconds")
    async def delete_tenant_user(self, user_id: str, deleted_by: str = None) -> bool:
        """删除（停用）租户用户"""
        existing_user = await self.tenant_user_repo.get_by_id(user_id)
        if not existing_user:
            raise ValueError("用户不存在")

        success = await self.tenant_user_repo.delete(user_id)

        if success:
            # 记录审计日志
            await self.audit_log_repo.create({
                "user_id": deleted_by,
                "user_type": UserType.ADMIN,  # 通常由管理员删除
                "action": "DELETE_TENANT_USER",
                "resource": "tenant_user",
                "resource_id": user_id,
                "details": {
                    "tenant_id": existing_user.tenant_id,
                    "username": existing_user.username
                },
                "success": True
            })

            log.info(f"Deleted tenant user: {user_id}")

        return success

    @measure("service_tenant_user_list_seconds")
    async def list_tenant_users(self, query_params: TenantUserQuery) -> List[TenantUserOut]:
        """获取租户用户列表"""
        return await self.tenant_user_repo.list(query_params)

    @measure("service_tenant_user_count_seconds")
    async def count_tenant_users(self, query_params: TenantUserQuery) -> int:
        """获取租户用户总数"""
        return await self.tenant_user_repo.count(query_params)

    @measure("service_tenant_user_list_by_tenant_seconds")
    async def list_by_tenant(self, tenant_id: str, limit: int = 20, offset: int = 0) -> List[TenantUserOut]:
        """根据租户ID获取用户列表"""
        return await self.tenant_user_repo.list_by_tenant(tenant_id, limit, offset)

    @measure("service_tenant_user_change_password_seconds")
    async def change_password(self, user_id: str, old_password: str, new_password: str,
                             changed_by: str = None) -> bool:
        """修改密码"""
        # 获取用户
        tenant_user = await self.tenant_user_repo.get_by_id(user_id)
        if not tenant_user:
            raise ValueError("用户不存在")

        # 验证旧密码
        if not PasswordUtils.verify_password(old_password, getattr(tenant_user, 'password_hash', '')):
            raise ValueError("当前密码不正确")

        # 验证新密码强度
        is_strong, errors = PasswordUtils.validate_password_strength(new_password)
        if not is_strong:
            raise ValueError(f"新密码强度不足: {'; '.join(errors)}")

        # 更新密码
        password_hash = PasswordUtils.hash_password(new_password)
        update_data = TenantUserUpdate(password_hash=password_hash)
        updated_user = await self.tenant_user_repo.update(user_id, update_data)

        if updated_user:
            # 记录审计日志
            await self.audit_log_repo.create({
                "user_id": changed_by or user_id,
                "user_type": UserType.TENANT,
                "action": "CHANGE_PASSWORD",
                "resource": "tenant_user",
                "resource_id": user_id,
                "details": {"self_change": changed_by == user_id or changed_by is None},
                "success": True
            })

            log.info(f"Password changed for tenant user: {user_id}")
            return True

        return False

    @measure("service_tenant_user_reset_password_seconds")
    async def reset_password(self, user_id: str, new_password: str = None,
                            reset_by: str = None) -> str:
        """重置密码（管理员操作）"""
        tenant_user = await self.tenant_user_repo.get_by_id(user_id)
        if not tenant_user:
            raise ValueError("用户不存在")

        # 如果没有提供新密码，生成随机密码
        if not new_password:
            new_password = PasswordUtils.generate_password(12)

        # 验证新密码强度
        is_strong, errors = PasswordUtils.validate_password_strength(new_password)
        if not is_strong:
            raise ValueError(f"新密码强度不足: {'; '.join(errors)}")

        # 更新密码
        password_hash = PasswordUtils.hash_password(new_password)
        update_data = TenantUserUpdate(password_hash=password_hash)
        updated_user = await self.tenant_user_repo.update(user_id, update_data)

        if updated_user:
            # 记录审计日志
            await self.audit_log_repo.create({
                "user_id": reset_by,
                "user_type": UserType.ADMIN,
                "action": "RESET_PASSWORD",
                "resource": "tenant_user",
                "resource_id": user_id,
                "details": {
                    "tenant_id": tenant_user.tenant_id,
                    "username": tenant_user.username
                },
                "success": True
            })

            log.info(f"Password reset for tenant user: {user_id}")
            return new_password

        raise ValueError("密码重置失败")

    @measure("service_tenant_user_get_profile_seconds")
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户详细资料（包括角色权限）"""
        tenant_user = await self.tenant_user_repo.get_by_id(user_id)
        if not tenant_user:
            return None

        # 获取用户角色和权限
        user_permissions = await self.user_role_repo.get_user_permissions(
            user_id, UserType.TENANT
        )

        # 获取用户角色详情
        user_roles = await self.user_role_repo.get_user_roles(user_id, UserType.TENANT)

        return {
            "user": tenant_user,
            "permissions": user_permissions.permissions,
            "roles": [{"role_id": ur.role_id, "role_code": ur.role_code,
                      "role_name": ur.role_name} for ur in user_roles]
        }