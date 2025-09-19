"""
认证服务 - 管理员用户服务
"""
from typing import List, Optional, Dict, Any

from saturn_mousehunter_shared.aop.decorators import measure
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.repositories import AdminUserRepo, UserRoleRepo, AuditLogRepo
from domain.models.auth_admin_user import (
    AdminUserIn, AdminUserOut, AdminUserUpdate, AdminUserQuery,
    AdminUserLogin, AdminUserResponse
)
from domain.models.auth_user_role import UserType
from domain.models.auth_audit_log import AuditLogIn
from application.utils import PasswordUtils, JWTUtils

log = get_logger(__name__)


class AdminUserService:
    """管理员用户服务"""

    def __init__(self,
                 admin_user_repo: AdminUserRepo,
                 user_role_repo: UserRoleRepo,
                 audit_log_repo: AuditLogRepo,
                 jwt_utils: JWTUtils):
        self.admin_user_repo = admin_user_repo
        self.user_role_repo = user_role_repo
        self.audit_log_repo = audit_log_repo
        self.jwt_utils = jwt_utils

    @measure("service_admin_user_create_seconds")
    async def create_admin_user(self, user_data: AdminUserIn, created_by: str = None) -> AdminUserOut:
        """创建管理员用户"""
        # 检查用户名是否已存在
        existing_user = await self.admin_user_repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError(f"用户名 '{user_data.username}' 已存在")

        # 检查邮箱是否已存在
        existing_email = await self.admin_user_repo.get_by_email(user_data.email)
        if existing_email:
            raise ValueError(f"邮箱 '{user_data.email}' 已存在")

        # 验证密码强度
        if user_data.password:
            is_strong, errors = PasswordUtils.validate_password_strength(user_data.password)
            if not is_strong:
                raise ValueError(f"密码强度不足: {'; '.join(errors)}")

            # 哈希密码
            user_data.password_hash = PasswordUtils.hash_password(user_data.password)

        # 创建用户
        admin_user = await self.admin_user_repo.create(user_data)

        # 记录审计日志
        await self.audit_log_repo.create(AuditLogIn(
            user_id=created_by,
            user_type=UserType.ADMIN,
            action="CREATE_ADMIN_USER",
            resource="admin_user",
            resource_id=admin_user.id,
            details={"username": admin_user.username, "email": admin_user.email},
            success=True
        ))

        log.info(f"Created admin user: {admin_user.username} (ID: {admin_user.id})")
        return admin_user

    @measure("service_admin_user_authenticate_seconds")
    async def authenticate(self, login_data: AdminUserLogin,
                          ip_address: str = None, user_agent: str = None) -> Optional[AdminUserResponse]:
        """管理员用户认证"""
        # 支持用户名或邮箱登录
        admin_user = None

        # 先尝试用户名
        if "@" not in login_data.username:
            admin_user = await self.admin_user_repo.get_by_username_for_auth(login_data.username)

        # 如果未找到，尝试邮箱
        if not admin_user and "@" in login_data.username:
            admin_user = await self.admin_user_repo.get_by_email_for_auth(login_data.username)

        # 验证用户存在且密码正确
        if not admin_user or not PasswordUtils.verify_password(
            login_data.password, admin_user.password_hash
        ):
            # 记录失败的登录尝试
            await self.audit_log_repo.log_login_attempt(
                user_id=admin_user.id if admin_user else None,
                user_type=UserType.ADMIN.value,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="无效的用户名或密码"
            )
            return None

        # 检查用户是否激活
        if not admin_user.is_active:
            await self.audit_log_repo.log_login_attempt(
                user_id=admin_user.id,
                user_type=UserType.ADMIN.value,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="用户账户已被停用"
            )
            return None

        # 获取用户权限
        user_permissions = await self.user_role_repo.get_user_permissions(
            admin_user.id, UserType.ADMIN
        )

        # 创建JWT令牌
        token_data = self.jwt_utils.create_token_pair(
            subject=admin_user.username,
            user_type=UserType.ADMIN.value,
            user_id=admin_user.id,
            permissions=user_permissions.permissions,
            roles=user_permissions.roles
        )

        # 更新最后登录时间
        await self.admin_user_repo.update_last_login(admin_user.id)

        # 记录成功登录
        await self.audit_log_repo.log_login_attempt(
            user_id=admin_user.id,
            user_type=UserType.ADMIN.value,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )

        log.info(f"Admin user authenticated: {admin_user.username}")

        # 转换为外部安全模型（不包含password_hash）
        safe_user = AdminUserOut(
            id=admin_user.id,
            username=admin_user.username,
            email=admin_user.email,
            full_name=admin_user.full_name,
            is_active=admin_user.is_active,
            is_superuser=admin_user.is_superuser,
            user_type=admin_user.user_type,
            last_login_at=admin_user.last_login_at,
            created_at=admin_user.created_at,
            updated_at=admin_user.updated_at
        )

        return AdminUserResponse(
            user=safe_user,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"]
        )

    @measure("service_admin_user_get_seconds")
    async def get_admin_user(self, user_id: str) -> Optional[AdminUserOut]:
        """获取管理员用户"""
        return await self.admin_user_repo.get_by_id(user_id)

    @measure("service_admin_user_get_by_username_seconds")
    async def get_by_username(self, username: str) -> Optional[AdminUserOut]:
        """根据用户名获取管理员用户"""
        return await self.admin_user_repo.get_by_username(username)

    @measure("service_admin_user_update_seconds")
    async def update_admin_user(self, user_id: str, update_data: AdminUserUpdate,
                               updated_by: str = None) -> Optional[AdminUserOut]:
        """更新管理员用户"""
        try:
            # 获取现有用户
            existing_user = await self.admin_user_repo.get_by_id(user_id)
            if not existing_user:
                return None

            # 如果更新邮箱，检查邮箱是否被其他用户使用
            if update_data.email and update_data.email != existing_user.email:
                existing_email = await self.admin_user_repo.get_by_email(update_data.email)
                if existing_email and existing_email.id != user_id:
                    raise ValueError(f"邮箱 '{update_data.email}' 已被其他用户使用")

            # 如果更新密码，验证密码强度并哈希
            if update_data.password:
                is_strong, errors = PasswordUtils.validate_password_strength(update_data.password)
                if not is_strong:
                    raise ValueError(f"密码强度不足: {'; '.join(errors)}")
                update_data.password_hash = PasswordUtils.hash_password(update_data.password)
                # 清除原始密码字段，避免传递到数据库
                update_data.password = None

            # 更新用户
            updated_user = await self.admin_user_repo.update(user_id, update_data)

            if updated_user:
                # 记录审计日志
                changes = {k: v for k, v in update_data.dict(exclude_unset=True).items()
                          if k not in ['password', 'password_hash'] and v is not None}
                if update_data.password_hash:
                    changes['password_updated'] = True

                await self.audit_log_repo.create(AuditLogIn(
                    user_id=updated_by,
                    user_type=UserType.ADMIN,
                    action="UPDATE_ADMIN_USER",
                    resource="admin_user",
                    resource_id=user_id,
                    details=changes,
                    success=True
                ))

                log.info(f"Updated admin user: {user_id}")

            return updated_user

        except Exception as e:
            log.error(f"Failed to update admin user {user_id}: {str(e)}")
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"更新用户失败: {str(e)}")

    @measure("service_admin_user_delete_seconds")
    async def delete_admin_user(self, user_id: str, deleted_by: str = None) -> bool:
        """删除（停用）管理员用户"""
        existing_user = await self.admin_user_repo.get_by_id(user_id)
        if not existing_user:
            raise ValueError("用户不存在")

        success = await self.admin_user_repo.delete(user_id)

        if success:
            # 记录审计日志
            await self.audit_log_repo.create(AuditLogIn(
                user_id=deleted_by,
                user_type=UserType.ADMIN,
                action="DELETE_ADMIN_USER",
                resource="admin_user",
                resource_id=user_id,
                details={"username": existing_user.username},
                success=True
            ))

            log.info(f"Deleted admin user: {user_id}")

        return success

    @measure("service_admin_user_list_seconds")
    async def list_admin_users(self, query_params: AdminUserQuery) -> List[AdminUserOut]:
        """获取管理员用户列表"""
        return await self.admin_user_repo.list(query_params)

    @measure("service_admin_user_count_seconds")
    async def count_admin_users(self, query_params: AdminUserQuery) -> int:
        """获取管理员用户总数"""
        return await self.admin_user_repo.count(query_params)

    @measure("service_admin_user_change_password_seconds")
    async def change_password(self, user_id: str, old_password: str, new_password: str,
                             changed_by: str = None) -> bool:
        """修改密码"""
        # 获取用户（包含密码哈希以验证旧密码）
        admin_user = await self._get_user_with_password_hash(user_id)
        if not admin_user:
            raise ValueError("用户不存在")

        # 验证旧密码
        if not PasswordUtils.verify_password(old_password, admin_user.password_hash):
            raise ValueError("当前密码不正确")

        # 验证新密码强度
        is_strong, errors = PasswordUtils.validate_password_strength(new_password)
        if not is_strong:
            raise ValueError(f"新密码强度不足: {'; '.join(errors)}")

        # 更新密码
        password_hash = PasswordUtils.hash_password(new_password)
        update_data = AdminUserUpdate(password_hash=password_hash)
        updated_user = await self.admin_user_repo.update(admin_user.id, update_data)

        if updated_user:
            # 记录审计日志
            await self.audit_log_repo.create(AuditLogIn(
                user_id=changed_by or admin_user.id,
                user_type=UserType.ADMIN,
                action="CHANGE_PASSWORD",
                resource="admin_user",
                resource_id=admin_user.id,
                details={"self_change": changed_by == admin_user.id or changed_by is None},
                success=True
            ))

            log.info(f"Password changed for admin user: {admin_user.id}")
            return True

        return False

    async def _get_user_with_password_hash(self, user_id: str):
        """内部方法：获取包含密码哈希的用户信息"""
        # 首先尝试通过ID获取
        user = await self.admin_user_repo.get_by_id_for_auth(user_id)
        if user:
            return user

        # 如果用户ID是用户名格式，尝试通过用户名获取
        user = await self.admin_user_repo.get_by_username_for_auth(user_id)
        if user:
            return user

        # 如果用户ID是email格式，尝试通过邮箱获取
        if "@" in user_id:
            return await self.admin_user_repo.get_by_email_for_auth(user_id)

        return None

    @measure("service_admin_user_reset_password_seconds")
    async def reset_password(self, user_id: str, new_password: str = None,
                            reset_by: str = None) -> str:
        """重置密码（管理员操作）"""
        admin_user = await self.admin_user_repo.get_by_id(user_id)
        if not admin_user:
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
        update_data = AdminUserUpdate(password_hash=password_hash)
        updated_user = await self.admin_user_repo.update(user_id, update_data)

        if updated_user:
            # 记录审计日志
            await self.audit_log_repo.create(AuditLogIn(
                user_id=reset_by,
                user_type=UserType.ADMIN,
                action="RESET_PASSWORD",
                resource="admin_user",
                resource_id=user_id,
                details={"username": admin_user.username},
                success=True
            ))

            log.info(f"Password reset for admin user: {user_id}")
            return new_password

        raise ValueError("密码重置失败")

    @measure("service_admin_user_get_profile_seconds")
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户详细资料（包括角色权限）"""
        admin_user = await self.admin_user_repo.get_by_id(user_id)
        if not admin_user:
            return None

        # 获取用户角色和权限
        user_permissions = await self.user_role_repo.get_user_permissions(
            user_id, UserType.ADMIN
        )

        # 获取用户角色详情
        user_roles = await self.user_role_repo.get_user_roles(user_id, UserType.ADMIN)

        return {
            "user": admin_user,
            "permissions": user_permissions.permissions,
            "roles": [{"role_id": ur.role_id, "role_code": ur.role_code,
                      "role_name": ur.role_name} for ur in user_roles]
        }