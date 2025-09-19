"""
认证服务 - 权限Service
"""
from typing import List, Optional
from saturn_mousehunter_shared.log.logger import get_logger
from domain.models.auth_permission import PermissionIn, PermissionOut, PermissionUpdate, PermissionQuery
from infrastructure.repositories.permission_repo import PermissionRepo
from infrastructure.repositories.audit_log_repo import AuditLogRepo

log = get_logger(__name__)


class PermissionService:
    """权限服务"""

    def __init__(self, permission_repo: PermissionRepo, audit_repo: AuditLogRepo):
        self.permission_repo = permission_repo
        self.audit_repo = audit_repo

    async def create_permission(self, permission_data: PermissionIn, created_by: str) -> PermissionOut:
        """创建权限"""
        # 检查权限编码是否已存在
        existing_permission = await self.permission_repo.get_by_code(permission_data.permission_code)
        if existing_permission:
            raise ValueError(f"权限编码 {permission_data.permission_code} 已存在")

        # 创建权限
        permission = await self.permission_repo.create(permission_data)

        # 记录审计日志
        from domain.models.auth_audit_log import AuditLogIn, UserType
        audit_log = AuditLogIn(
            user_id=created_by,
            user_type=UserType.ADMIN,
            action="CREATE_PERMISSION",
            resource="permission",
            resource_id=permission.id,
            details={"permission_name": permission.permission_name, "permission_code": permission.permission_code},
            ip_address=None  # 在API层获取
        )
        await self.audit_repo.create(audit_log)

        log.info(f"Created permission {permission.permission_code} by {created_by}")
        return permission

    async def get_permission(self, permission_id: str) -> Optional[PermissionOut]:
        """获取权限信息"""
        return await self.permission_repo.get_by_id(permission_id)

    async def get_permission_by_code(self, permission_code: str) -> Optional[PermissionOut]:
        """根据编码获取权限"""
        return await self.permission_repo.get_by_code(permission_code)

    async def update_permission(self, permission_id: str, update_data: PermissionUpdate, updated_by: str) -> Optional[PermissionOut]:
        """更新权限"""
        # 检查权限是否存在
        existing_permission = await self.permission_repo.get_by_id(permission_id)
        if not existing_permission:
            return None

        # 系统权限不允许修改
        if existing_permission.is_system_permission:
            raise ValueError("系统权限不能修改")

        # 更新权限
        permission = await self.permission_repo.update(permission_id, update_data)

        if permission:
            # 记录审计日志
            from domain.models.auth_audit_log import AuditLogIn, UserType
            audit_log = AuditLogIn(
                user_id=updated_by,
                user_type=UserType.ADMIN,
                action="UPDATE_PERMISSION",
                resource="permission",
                resource_id=permission_id,
                details={"permission_name": permission.permission_name},
                ip_address=None
            )
            await self.audit_repo.create(audit_log)

            log.info(f"Updated permission {permission_id} by {updated_by}")

        return permission

    async def delete_permission(self, permission_id: str, deleted_by: str) -> bool:
        """删除权限"""
        # 检查是否为系统权限
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            return False

        if permission.is_system_permission:
            raise ValueError("系统权限不能删除")

        # 删除权限
        success = await self.permission_repo.delete(permission_id)

        if success:
            # 记录审计日志
            from domain.models.auth_audit_log import AuditLogIn, UserType
            audit_log = AuditLogIn(
                user_id=deleted_by,
                user_type=UserType.ADMIN,
                action="DELETE_PERMISSION",
                resource="permission",
                resource_id=permission_id,
                details={"permission_name": permission.permission_name, "permission_code": permission.permission_code},
                ip_address=None
            )
            await self.audit_repo.create(audit_log)

            log.info(f"Deleted permission {permission_id} by {deleted_by}")

        return success

    async def list_permissions(self, query_params: PermissionQuery) -> List[PermissionOut]:
        """获取权限列表"""
        return await self.permission_repo.list(query_params)

    async def count_permissions(self, query_params: PermissionQuery) -> int:
        """获取权限总数"""
        return await self.permission_repo.count(query_params)

    async def list_permissions_by_resource(self, resource: str) -> List[PermissionOut]:
        """根据资源获取权限列表"""
        return await self.permission_repo.list_by_resource(resource)

    async def list_system_permissions(self) -> List[PermissionOut]:
        """获取所有系统权限"""
        return await self.permission_repo.list_system_permissions()

    async def check_permission_exists(self, permission_code: str) -> bool:
        """检查权限是否存在"""
        return await self.permission_repo.check_permission_exists(permission_code)