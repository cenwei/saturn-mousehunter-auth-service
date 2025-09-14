"""
认证服务 - 权限Repository
"""
from datetime import datetime
from typing import List, Optional

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_permission import PermissionIn, PermissionOut, PermissionUpdate, PermissionQuery

log = get_logger(__name__)

TABLE = "mh_auth_permissions"


class PermissionRepo:
    """权限Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_permission_create_seconds")
    async def create(self, permission_data: PermissionIn) -> PermissionOut:
        """创建权限"""
        permission_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, permission_name, permission_code, resource, action,
            description, is_system_permission, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            permission_id,
            permission_data.permission_name,
            permission_data.permission_code,
            permission_data.resource,
            permission_data.action,
            permission_data.description,
            permission_data.is_system_permission,
            now,
            now
        )

        log.info(f"Created permission: {permission_data.permission_code}")
        return PermissionOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_permission_get_seconds")
    async def get_by_id(self, permission_id: str) -> Optional[PermissionOut]:
        """根据ID获取权限"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, permission_id)

        if row:
            return PermissionOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_permission_get_by_code_seconds")
    async def get_by_code(self, permission_code: str) -> Optional[PermissionOut]:
        """根据权限编码获取权限"""
        query = f"SELECT * FROM {TABLE} WHERE permission_code = $1"
        row = await self.dao.fetch_one(query, permission_code)

        if row:
            return PermissionOut.from_dict(dict(row))
        return None

    @measure("db_permission_update_seconds")
    async def update(self, permission_id: str, update_data: PermissionUpdate) -> Optional[PermissionOut]:
        """更新权限"""
        # 先检查是否为系统权限
        permission = await self.get_by_id(permission_id)
        if permission and permission.is_system_permission:
            log.warning(f"Cannot update system permission: {permission_id}")
            return permission

        set_clauses = []
        params = []
        param_count = 1

        # 动态构建UPDATE语句
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != 'updated_at':
                set_clauses.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1

        if not set_clauses:
            return await self.get_by_id(permission_id)

        # 添加更新时间
        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.now())
        param_count += 1

        # 添加WHERE条件
        params.append(permission_id)

        query = f"""
        UPDATE {TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = ${param_count} AND is_system_permission = false
        RETURNING *
        """

        row = await self.dao.fetch_one(query, *params)
        if row:
            log.info(f"Updated permission: {permission_id}")
            return PermissionOut.from_dict(dict(row))
        return permission  # 返回原权限（系统权限不可修改）

    @measure("db_permission_delete_seconds")
    async def delete(self, permission_id: str) -> bool:
        """删除权限（物理删除，仅限非系统权限）"""
        # 先检查是否为系统权限
        permission = await self.get_by_id(permission_id)
        if permission and permission.is_system_permission:
            log.warning(f"Cannot delete system permission: {permission_id}")
            return False

        # 先删除角色权限关联
        delete_role_permissions_query = """
        DELETE FROM mh_auth_role_permissions
        WHERE permission_id = $1
        """
        await self.dao.execute(delete_role_permissions_query, permission_id)

        # 删除权限
        query = f"""
        DELETE FROM {TABLE}
        WHERE id = $1 AND is_system_permission = false
        """

        result = await self.dao.execute(query, permission_id)
        success = result > 0

        if success:
            log.info(f"Deleted permission: {permission_id}")

        return success

    @read_only_guard()
    @measure("db_permission_list_seconds")
    async def list(self, query_params: PermissionQuery) -> List[PermissionOut]:
        """获取权限列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.permission_name:
            conditions.append(f"permission_name ILIKE ${param_count}")
            params.append(f"%{query_params.permission_name}%")
            param_count += 1

        if query_params.resource:
            conditions.append(f"resource = ${param_count}")
            params.append(query_params.resource)
            param_count += 1

        if query_params.action:
            conditions.append(f"action = ${param_count}")
            params.append(query_params.action)
            param_count += 1

        if query_params.is_system_permission is not None:
            conditions.append(f"is_system_permission = ${param_count}")
            params.append(query_params.is_system_permission)
            param_count += 1

        # 构建查询
        base_query = f"""
        SELECT * FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        ORDER BY resource, action, permission_code
        """

        # 添加分页
        if query_params.limit:
            base_query += f" LIMIT ${param_count}"
            params.append(query_params.limit)
            param_count += 1

        if query_params.offset:
            base_query += f" OFFSET ${param_count}"
            params.append(query_params.offset)

        rows = await self.dao.fetch_all(base_query, *params)
        return [PermissionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_permission_count_seconds")
    async def count(self, query_params: PermissionQuery) -> int:
        """获取权限总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件（复用list方法的逻辑）
        if query_params.permission_name:
            conditions.append(f"permission_name ILIKE ${param_count}")
            params.append(f"%{query_params.permission_name}%")
            param_count += 1

        if query_params.resource:
            conditions.append(f"resource = ${param_count}")
            params.append(query_params.resource)
            param_count += 1

        if query_params.action:
            conditions.append(f"action = ${param_count}")
            params.append(query_params.action)
            param_count += 1

        if query_params.is_system_permission is not None:
            conditions.append(f"is_system_permission = ${param_count}")
            params.append(query_params.is_system_permission)
            param_count += 1

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0

    @read_only_guard()
    @measure("db_permission_list_by_resource_seconds")
    async def list_by_resource(self, resource: str) -> List[PermissionOut]:
        """根据资源获取权限列表"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE resource = $1
        ORDER BY action, permission_code
        """

        rows = await self.dao.fetch_all(query, resource)
        return [PermissionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_permission_list_system_seconds")
    async def list_system_permissions(self) -> List[PermissionOut]:
        """获取所有系统权限"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE is_system_permission = true
        ORDER BY resource, action, permission_code
        """

        rows = await self.dao.fetch_all(query)
        return [PermissionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_permission_check_exists_seconds")
    async def check_permission_exists(self, permission_code: str) -> bool:
        """检查权限是否存在"""
        query = f"SELECT 1 FROM {TABLE} WHERE permission_code = $1"
        row = await self.dao.fetch_one(query, permission_code)
        return row is not None