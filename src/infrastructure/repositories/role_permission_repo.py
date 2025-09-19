"""
认证服务 - 角色权限关系Repository
"""
from datetime import datetime
from typing import List, Optional

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_role_permission import (
    RolePermissionIn, RolePermissionOut, RolePermissionQuery,
    RolePermissionAssignment
)

log = get_logger(__name__)

TABLE = "mh_auth_role_permissions"


class RolePermissionRepo:
    """角色权限关系Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_role_permission_create_seconds")
    async def create(self, role_permission_data: RolePermissionIn) -> RolePermissionOut:
        """创建角色权限关系"""
        role_permission_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, role_id, permission_id, created_at
        ) VALUES (
            $1, $2, $3, $4
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            role_permission_id,
            role_permission_data.role_id,
            role_permission_data.permission_id,
            now
        )

        # 获取详细信息
        role_permission = RolePermissionOut.from_dict(dict(row))
        details = await self._get_role_permission_details(role_permission.role_id, role_permission.permission_id)
        if details:
            role_permission.role_name = details.get('role_name')
            role_permission.role_code = details.get('role_code')
            role_permission.permission_name = details.get('permission_name')
            role_permission.permission_code = details.get('permission_code')

        log.info(f"Created role permission: role={role_permission_data.role_id}, permission={role_permission_data.permission_id}")
        return role_permission

    @read_only_guard()
    @measure("db_role_permission_get_seconds")
    async def get_by_id(self, role_permission_id: str) -> Optional[RolePermissionOut]:
        """根据ID获取角色权限关系"""
        query = f"""
        SELECT rp.*, r.role_name, r.role_code, p.permission_name, p.permission_code
        FROM {TABLE} rp
        LEFT JOIN mh_auth_roles r ON rp.role_id = r.id
        LEFT JOIN mh_auth_permissions p ON rp.permission_id = p.id
        WHERE rp.id = $1
        """
        row = await self.dao.fetch_one(query, role_permission_id)

        if row:
            return RolePermissionOut.from_dict(dict(row))
        return None

    @measure("db_role_permission_delete_seconds")
    async def delete(self, role_permission_id: str) -> bool:
        """删除角色权限关系"""
        query = f"DELETE FROM {TABLE} WHERE id = $1"
        result = await self.dao.execute(query, role_permission_id)
        success = result > 0

        if success:
            log.info(f"Deleted role permission: {role_permission_id}")

        return success

    @read_only_guard()
    @measure("db_role_permission_list_seconds")
    async def list(self, query_params: RolePermissionQuery) -> List[RolePermissionOut]:
        """获取角色权限关系列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.role_id:
            conditions.append(f"rp.role_id = ${param_count}")
            params.append(query_params.role_id)
            param_count += 1

        if query_params.permission_id:
            conditions.append(f"rp.permission_id = ${param_count}")
            params.append(query_params.permission_id)
            param_count += 1

        # 构建查询
        base_query = f"""
        SELECT rp.*, r.role_name, r.role_code, p.permission_name, p.permission_code
        FROM {TABLE} rp
        LEFT JOIN mh_auth_roles r ON rp.role_id = r.id
        LEFT JOIN mh_auth_permissions p ON rp.permission_id = p.id
        WHERE {' AND '.join(conditions)}
        ORDER BY r.role_code, p.permission_code
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
        return [RolePermissionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_role_permission_get_by_role_seconds")
    async def get_permissions_by_role(self, role_id: str) -> List[RolePermissionOut]:
        """获取角色的所有权限"""
        query = f"""
        SELECT rp.*, r.role_name, r.role_code, p.permission_name, p.permission_code
        FROM {TABLE} rp
        LEFT JOIN mh_auth_roles r ON rp.role_id = r.id
        LEFT JOIN mh_auth_permissions p ON rp.permission_id = p.id
        WHERE rp.role_id = $1
        ORDER BY p.permission_code
        """

        rows = await self.dao.fetch_all(query, role_id)
        return [RolePermissionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_role_permission_get_by_permission_seconds")
    async def get_roles_by_permission(self, permission_id: str) -> List[RolePermissionOut]:
        """获取拥有某权限的所有角色"""
        query = f"""
        SELECT rp.*, r.role_name, r.role_code, p.permission_name, p.permission_code
        FROM {TABLE} rp
        LEFT JOIN mh_auth_roles r ON rp.role_id = r.id
        LEFT JOIN mh_auth_permissions p ON rp.permission_id = p.id
        WHERE rp.permission_id = $1
        ORDER BY r.role_code
        """

        rows = await self.dao.fetch_all(query, permission_id)
        return [RolePermissionOut.from_dict(dict(row)) for row in rows]

    @measure("db_role_permission_assign_permissions_seconds")
    async def assign_permissions(self, assignment: RolePermissionAssignment) -> List[RolePermissionOut]:
        """批量分配权限给角色"""
        role_permissions = []

        async with self.dao.transaction():
            for permission_id in assignment.permission_ids:
                # 检查是否已存在
                existing = await self._check_role_permission_exists(assignment.role_id, permission_id)

                if not existing:
                    role_permission_data = RolePermissionIn(
                        role_id=assignment.role_id,
                        permission_id=permission_id
                    )
                    role_permission = await self.create(role_permission_data)
                    role_permissions.append(role_permission)
                else:
                    log.info(f"Role permission already exists: role={assignment.role_id}, permission={permission_id}")

        return role_permissions

    @measure("db_role_permission_revoke_permissions_seconds")
    async def revoke_permissions(self, role_id: str, permission_ids: List[str]) -> int:
        """批量撤销角色权限"""
        if not permission_ids:
            return 0

        placeholders = ', '.join(f'${i+2}' for i in range(len(permission_ids)))
        query = f"""
        DELETE FROM {TABLE}
        WHERE role_id = $1 AND permission_id IN ({placeholders})
        """

        params = [role_id] + permission_ids
        result = await self.dao.execute(query, *params)

        log.info(f"Revoked {result} permissions from role: {role_id}")
        return result

    @measure("db_role_permission_replace_permissions_seconds")
    async def replace_role_permissions(self, role_id: str, permission_ids: List[str]) -> List[RolePermissionOut]:
        """替换角色的所有权限"""
        async with self.dao.transaction() as conn:
            # 删除现有权限
            delete_query = f"DELETE FROM {TABLE} WHERE role_id = $1"
            await conn.execute(delete_query, role_id)

            # 添加新权限
            role_permissions = []
            for permission_id in permission_ids:
                role_permission_data = RolePermissionIn(
                    role_id=role_id,
                    permission_id=permission_id
                )
                role_permission = await self.create(role_permission_data)
                role_permissions.append(role_permission)

            log.info(f"Replaced permissions for role {role_id}, new count: {len(permission_ids)}")
            return role_permissions

    @read_only_guard()
    @measure("db_role_permission_check_exists_seconds")
    async def _check_role_permission_exists(self, role_id: str, permission_id: str) -> bool:
        """检查角色权限关系是否存在"""
        query = f"""
        SELECT 1 FROM {TABLE}
        WHERE role_id = $1 AND permission_id = $2
        """
        row = await self.dao.fetch_one(query, role_id, permission_id)
        return row is not None

    @read_only_guard()
    @measure("db_role_permission_get_details_seconds")
    async def _get_role_permission_details(self, role_id: str, permission_id: str) -> Optional[dict]:
        """获取角色权限详细信息"""
        query = """
        SELECT r.role_name, r.role_code, p.permission_name, p.permission_code
        FROM mh_auth_roles r, mh_auth_permissions p
        WHERE r.id = $1 AND p.id = $2
        """
        row = await self.dao.fetch_one(query, role_id, permission_id)
        return dict(row) if row else None

    @read_only_guard()
    @measure("db_role_permission_count_seconds")
    async def count(self, query_params: RolePermissionQuery) -> int:
        """获取角色权限关系总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.role_id:
            conditions.append(f"role_id = ${param_count}")
            params.append(query_params.role_id)
            param_count += 1

        if query_params.permission_id:
            conditions.append(f"permission_id = ${param_count}")
            params.append(query_params.permission_id)
            param_count += 1

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0