"""
认证服务 - 角色Service
"""
from typing import List, Optional
from saturn_mousehunter_shared.log.logger import get_logger
from domain.models.auth_role import RoleIn, RoleOut, RoleUpdate, RoleQuery, RoleWithPermissions
from infrastructure.repositories.role_repo import RoleRepo
from infrastructure.repositories.audit_log_repo import AuditLogRepo

log = get_logger(__name__)


class RoleService:
    """角色服务"""

    def __init__(self, role_repo: RoleRepo, audit_repo: AuditLogRepo):
        self.role_repo = role_repo
        self.audit_repo = audit_repo

    async def create_role(self, role_data: RoleIn, created_by: str) -> RoleOut:
        """创建角色"""
        # 检查角色编码是否已存在
        existing_role = await self.role_repo.get_by_code(role_data.role_code)
        if existing_role:
            raise ValueError(f"角色编码 {role_data.role_code} 已存在")

        # 创建角色
        role = await self.role_repo.create(role_data)

        # 记录审计日志
        from domain.models.auth_audit_log import AuditLogIn, UserType
        audit_log = AuditLogIn(
            user_id=created_by,
            user_type=UserType.ADMIN,
            action="CREATE_ROLE",
            resource="role",
            resource_id=role.id,
            details={"role_name": role.role_name, "role_code": role.role_code},
            ip_address=None  # 在API层获取
        )
        await self.audit_repo.create(audit_log)

        log.info(f"Created role {role.role_code} by {created_by}")
        return role

    async def get_role(self, role_id: str) -> Optional[RoleOut]:
        """获取角色信息"""
        return await self.role_repo.get_by_id(role_id)

    async def get_role_by_code(self, role_code: str) -> Optional[RoleOut]:
        """根据编码获取角色"""
        return await self.role_repo.get_by_code(role_code)

    async def get_role_with_permissions(self, role_id: str) -> Optional[RoleWithPermissions]:
        """获取角色及其权限"""
        return await self.role_repo.get_with_permissions(role_id)

    async def update_role(self, role_id: str, update_data: RoleUpdate, updated_by: str) -> Optional[RoleOut]:
        """更新角色"""
        # 检查角色是否存在
        existing_role = await self.role_repo.get_by_id(role_id)
        if not existing_role:
            return None

        # 系统角色不允许修改某些字段
        if existing_role.is_system_role:
            # 系统角色只允许修改描述和激活状态
            filtered_update = RoleUpdate(
                description=update_data.description,
                is_active=update_data.is_active
            )
            update_data = filtered_update

        # 更新角色
        role = await self.role_repo.update(role_id, update_data)

        if role:
            # 记录审计日志
            from domain.models.auth_audit_log import AuditLogIn, UserType
            audit_log = AuditLogIn(
                user_id=updated_by,
                user_type=UserType.ADMIN,
                action="UPDATE_ROLE",
                resource="role",
                resource_id=role_id,
                details={"role_name": role.role_name},
                ip_address=None
            )
            await self.audit_repo.create(audit_log)

            log.info(f"Updated role {role_id} by {updated_by}")

        return role

    async def delete_role(self, role_id: str, deleted_by: str) -> bool:
        """删除角色（软删除）"""
        # 检查是否为系统角色
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            return False

        if role.is_system_role:
            raise ValueError("系统角色不能删除")

        # 检查是否有用户正在使用此角色
        # TODO: 这里可以添加检查逻辑

        success = await self.role_repo.delete(role_id)

        if success:
            # 记录审计日志
            from domain.models.auth_audit_log import AuditLogIn, UserType
            audit_log = AuditLogIn(
                user_id=deleted_by,
                user_type=UserType.ADMIN,
                action="DELETE_ROLE",
                resource="role",
                resource_id=role_id,
                details={"role_name": role.role_name, "role_code": role.role_code},
                ip_address=None
            )
            await self.audit_repo.create(audit_log)

            log.info(f"Deleted role {role_id} by {deleted_by}")

        return success

    async def list_roles(self, query_params: RoleQuery) -> List[RoleOut]:
        """获取角色列表"""
        return await self.role_repo.list(query_params)

    async def count_roles(self, query_params: RoleQuery) -> int:
        """获取角色总数"""
        return await self.role_repo.count(query_params)

    async def list_system_roles(self) -> List[RoleOut]:
        """获取所有系统角色"""
        return await self.role_repo.list_system_roles()