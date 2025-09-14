"""
认证服务 - 角色Repository
"""
from datetime import datetime
from typing import List, Optional

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_role import RoleIn, RoleOut, RoleUpdate, RoleQuery, RoleWithPermissions

log = get_logger(__name__)

TABLE = "mh_auth_roles"


class RoleRepo:
    """角色Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_role_create_seconds")
    async def create(self, role_data: RoleIn) -> RoleOut:
        """创建角色"""
        role_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, role_name, role_code, description, scope,
            is_system_role, is_active, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            role_id,
            role_data.role_name,
            role_data.role_code,
            role_data.description,
            role_data.scope.value,
            role_data.is_system_role,
            role_data.is_active,
            now,
            now
        )

        log.info(f"Created role: {role_data.role_code}")
        return RoleOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_role_get_seconds")
    async def get_by_id(self, role_id: str) -> Optional[RoleOut]:
        """根据ID获取角色"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, role_id)

        if row:
            return RoleOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_role_get_by_code_seconds")
    async def get_by_code(self, role_code: str) -> Optional[RoleOut]:
        """根据角色编码获取角色"""
        query = f"SELECT * FROM {TABLE} WHERE role_code = $1"
        row = await self.dao.fetch_one(query, role_code)

        if row:
            return RoleOut.from_dict(dict(row))
        return None

    @measure("db_role_update_seconds")
    async def update(self, role_id: str, update_data: RoleUpdate) -> Optional[RoleOut]:
        """更新角色"""
        set_clauses = []
        params = []
        param_count = 1

        # 动态构建UPDATE语句
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != 'updated_at':
                if field == 'scope' and value:
                    # 处理枚举值
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(value.value)
                else:
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(value)
                param_count += 1

        if not set_clauses:
            return await self.get_by_id(role_id)

        # 添加更新时间
        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.now())
        param_count += 1

        # 添加WHERE条件
        params.append(role_id)

        query = f"""
        UPDATE {TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = ${param_count}
        RETURNING *
        """

        row = await self.dao.fetch_one(query, *params)
        if row:
            log.info(f"Updated role: {role_id}")
            return RoleOut.from_dict(dict(row))
        return None

    @measure("db_role_delete_seconds")
    async def delete(self, role_id: str) -> bool:
        """删除角色（软删除）"""
        # 先检查是否为系统角色
        role = await self.get_by_id(role_id)
        if role and role.is_system_role:
            log.warning(f"Cannot delete system role: {role_id}")
            return False

        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = $1
        WHERE id = $2 AND is_system_role = false
        """

        result = await self.dao.execute(query, datetime.now(), role_id)
        success = result > 0

        if success:
            log.info(f"Deleted role: {role_id}")

        return success

    @read_only_guard()
    @measure("db_role_list_seconds")
    async def list(self, query_params: RoleQuery) -> List[RoleOut]:
        """获取角色列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.role_name:
            conditions.append(f"role_name ILIKE ${param_count}")
            params.append(f"%{query_params.role_name}%")
            param_count += 1

        if query_params.role_code:
            conditions.append(f"role_code = ${param_count}")
            params.append(query_params.role_code)
            param_count += 1

        if query_params.scope:
            conditions.append(f"scope = ${param_count}")
            params.append(query_params.scope.value)
            param_count += 1

        if query_params.is_system_role is not None:
            conditions.append(f"is_system_role = ${param_count}")
            params.append(query_params.is_system_role)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        # 构建查询
        base_query = f"""
        SELECT * FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
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
        return [RoleOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_role_count_seconds")
    async def count(self, query_params: RoleQuery) -> int:
        """获取角色总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件（复用list方法的逻辑）
        if query_params.role_name:
            conditions.append(f"role_name ILIKE ${param_count}")
            params.append(f"%{query_params.role_name}%")
            param_count += 1

        if query_params.role_code:
            conditions.append(f"role_code = ${param_count}")
            params.append(query_params.role_code)
            param_count += 1

        if query_params.scope:
            conditions.append(f"scope = ${param_count}")
            params.append(query_params.scope.value)
            param_count += 1

        if query_params.is_system_role is not None:
            conditions.append(f"is_system_role = ${param_count}")
            params.append(query_params.is_system_role)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0

    @read_only_guard()
    @measure("db_role_get_with_permissions_seconds")
    async def get_with_permissions(self, role_id: str) -> Optional[RoleWithPermissions]:
        """获取角色及其权限"""
        # 先获取角色信息
        role = await self.get_by_id(role_id)
        if not role:
            return None

        # 获取角色权限
        query = f"""
        SELECT p.* FROM mh_auth_permissions p
        JOIN mh_auth_role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = $1
        ORDER BY p.permission_code
        """

        rows = await self.dao.fetch_all(query, role_id)
        from domain.models.auth_permission import PermissionOut
        permissions = [PermissionOut.from_dict(dict(row)) for row in rows]

        return RoleWithPermissions(
            **role.dict(),
            permissions=permissions
        )

    @read_only_guard()
    @measure("db_role_list_system_seconds")
    async def list_system_roles(self) -> List[RoleOut]:
        """获取所有系统角色"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE is_system_role = true AND is_active = true
        ORDER BY role_code
        """

        rows = await self.dao.fetch_all(query)
        return [RoleOut.from_dict(dict(row)) for row in rows]