"""
认证服务 - 用户角色关系Repository
"""
from datetime import datetime
from typing import List, Optional

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_user_role import (
    UserRoleIn, UserRoleOut, UserRoleUpdate, UserRoleQuery,
    UserRoleAssignment, UserPermissions, UserType
)

log = get_logger(__name__)

TABLE = "mh_auth_user_roles"


class UserRoleRepo:
    """用户角色关系Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_user_role_create_seconds")
    async def create(self, user_role_data: UserRoleIn) -> UserRoleOut:
        """创建用户角色关系"""
        user_role_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, user_id, user_type, role_id, granted_by,
            granted_at, expires_at, is_active
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            user_role_id,
            user_role_data.user_id,
            user_role_data.user_type.value,
            user_role_data.role_id,
            user_role_data.granted_by,
            now,
            user_role_data.expires_at,
            user_role_data.is_active
        )

        # 获取角色信息
        user_role = UserRoleOut.from_dict(dict(row))
        role_info = await self._get_role_info(user_role_data.role_id)
        if role_info:
            user_role.role_name = role_info.get('role_name')
            user_role.role_code = role_info.get('role_code')

        log.info(f"Created user role: user={user_role_data.user_id}, role={user_role_data.role_id}")
        return user_role

    @read_only_guard()
    @measure("db_user_role_get_seconds")
    async def get_by_id(self, user_role_id: str) -> Optional[UserRoleOut]:
        """根据ID获取用户角色关系"""
        query = f"""
        SELECT ur.*, r.role_name, r.role_code
        FROM {TABLE} ur
        LEFT JOIN mh_auth_roles r ON ur.role_id = r.id
        WHERE ur.id = $1
        """
        row = await self.dao.fetch_one(query, user_role_id)

        if row:
            return UserRoleOut.from_dict(dict(row))
        return None

    @measure("db_user_role_update_seconds")
    async def update(self, user_role_id: str, update_data: UserRoleUpdate) -> Optional[UserRoleOut]:
        """更新用户角色关系"""
        set_clauses = []
        params = []
        param_count = 1

        # 动态构建UPDATE语句
        for field, value in update_data.dict(exclude_unset=True).items():
            set_clauses.append(f"{field} = ${param_count}")
            params.append(value)
            param_count += 1

        if not set_clauses:
            return await self.get_by_id(user_role_id)

        # 添加WHERE条件
        params.append(user_role_id)

        query = f"""
        UPDATE {TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = ${param_count}
        RETURNING *
        """

        row = await self.dao.fetch_one(query, *params)
        if row:
            log.info(f"Updated user role: {user_role_id}")
            user_role = UserRoleOut.from_dict(dict(row))
            # 获取角色信息
            role_info = await self._get_role_info(user_role.role_id)
            if role_info:
                user_role.role_name = role_info.get('role_name')
                user_role.role_code = role_info.get('role_code')
            return user_role
        return None

    @measure("db_user_role_delete_seconds")
    async def delete(self, user_role_id: str) -> bool:
        """删除用户角色关系"""
        query = f"DELETE FROM {TABLE} WHERE id = $1"
        result = await self.dao.execute(query, user_role_id)
        success = result > 0

        if success:
            log.info(f"Deleted user role: {user_role_id}")

        return success

    @read_only_guard()
    @measure("db_user_role_list_seconds")
    async def list(self, query_params: UserRoleQuery) -> List[UserRoleOut]:
        """获取用户角色关系列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.user_id:
            conditions.append(f"ur.user_id = ${param_count}")
            params.append(query_params.user_id)
            param_count += 1

        if query_params.user_type:
            conditions.append(f"ur.user_type = ${param_count}")
            params.append(query_params.user_type.value)
            param_count += 1

        if query_params.role_id:
            conditions.append(f"ur.role_id = ${param_count}")
            params.append(query_params.role_id)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"ur.is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        # 处理过期时间
        if not query_params.include_expired:
            conditions.append("(ur.expires_at IS NULL OR ur.expires_at > NOW())")

        # 构建查询
        base_query = f"""
        SELECT ur.*, r.role_name, r.role_code
        FROM {TABLE} ur
        LEFT JOIN mh_auth_roles r ON ur.role_id = r.id
        WHERE {' AND '.join(conditions)}
        ORDER BY ur.granted_at DESC
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
        return [UserRoleOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_user_role_get_user_roles_seconds")
    async def get_user_roles(self, user_id: str, user_type: UserType, include_expired: bool = False) -> List[UserRoleOut]:
        """获取用户的所有角色"""
        conditions = ["ur.user_id = $1", "ur.user_type = $2", "ur.is_active = true"]
        params = [user_id, user_type.value]

        if not include_expired:
            conditions.append("(ur.expires_at IS NULL OR ur.expires_at > NOW())")

        query = f"""
        SELECT ur.*, r.role_name, r.role_code
        FROM {TABLE} ur
        LEFT JOIN mh_auth_roles r ON ur.role_id = r.id
        WHERE {' AND '.join(conditions)}
        ORDER BY ur.granted_at DESC
        """

        rows = await self.dao.fetch_all(query, *params)
        return [UserRoleOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_user_role_get_user_permissions_seconds")
    async def get_user_permissions(self, user_id: str, user_type: UserType) -> UserPermissions:
        """获取用户的所有权限"""
        query = f"""
        SELECT DISTINCT p.permission_code, r.role_code
        FROM {TABLE} ur
        JOIN mh_auth_roles r ON ur.role_id = r.id
        JOIN mh_auth_role_permissions rp ON r.id = rp.role_id
        JOIN mh_auth_permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = $1
          AND ur.user_type = $2
          AND ur.is_active = true
          AND r.is_active = true
          AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
        ORDER BY p.permission_code, r.role_code
        """

        rows = await self.dao.fetch_all(query, user_id, user_type.value)

        permissions = []
        roles = []
        for row in rows:
            if row['permission_code'] not in permissions:
                permissions.append(row['permission_code'])
            if row['role_code'] not in roles:
                roles.append(row['role_code'])

        return UserPermissions(
            user_id=user_id,
            user_type=user_type,
            permissions=permissions,
            roles=roles
        )

    @measure("db_user_role_assign_roles_seconds")
    async def assign_roles(self, assignment: UserRoleAssignment, granted_by: Optional[str] = None) -> List[UserRoleOut]:
        """批量分配角色给用户"""
        user_roles = []

        async with self.dao.transaction() as conn:
            for role_id in assignment.role_ids:
                # 检查是否已存在
                existing = await self._check_user_role_exists(
                    assignment.user_id, assignment.user_type, role_id
                )

                if not existing:
                    user_role_data = UserRoleIn(
                        user_id=assignment.user_id,
                        user_type=assignment.user_type,
                        role_id=role_id,
                        granted_by=granted_by,
                        expires_at=assignment.expires_at
                    )
                    user_role = await self.create(user_role_data)
                    user_roles.append(user_role)
                else:
                    log.info(f"User role already exists: user={assignment.user_id}, role={role_id}")

        return user_roles

    @measure("db_user_role_revoke_roles_seconds")
    async def revoke_roles(self, user_id: str, user_type: UserType, role_ids: List[str]) -> int:
        """批量撤销用户角色"""
        if not role_ids:
            return 0

        placeholders = ', '.join(f'${i+3}' for i in range(len(role_ids)))
        query = f"""
        UPDATE {TABLE}
        SET is_active = false
        WHERE user_id = $1 AND user_type = $2 AND role_id IN ({placeholders})
        """

        params = [user_id, user_type.value] + role_ids
        result = await self.dao.execute(query, *params)

        log.info(f"Revoked {result} roles for user: {user_id}")
        return result

    @read_only_guard()
    @measure("db_user_role_check_exists_seconds")
    async def _check_user_role_exists(self, user_id: str, user_type: UserType, role_id: str) -> bool:
        """检查用户角色关系是否存在"""
        query = f"""
        SELECT 1 FROM {TABLE}
        WHERE user_id = $1 AND user_type = $2 AND role_id = $3 AND is_active = true
        """
        row = await self.dao.fetch_one(query, user_id, user_type.value, role_id)
        return row is not None

    @read_only_guard()
    @measure("db_user_role_get_role_info_seconds")
    async def _get_role_info(self, role_id: str) -> Optional[dict]:
        """获取角色信息"""
        query = "SELECT role_name, role_code FROM mh_auth_roles WHERE id = $1"
        row = await self.dao.fetch_one(query, role_id)
        return dict(row) if row else None

    @read_only_guard()
    @measure("db_user_role_count_seconds")
    async def count(self, query_params: UserRoleQuery) -> int:
        """获取用户角色关系总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件（复用list方法的逻辑）
        if query_params.user_id:
            conditions.append(f"user_id = ${param_count}")
            params.append(query_params.user_id)
            param_count += 1

        if query_params.user_type:
            conditions.append(f"user_type = ${param_count}")
            params.append(query_params.user_type.value)
            param_count += 1

        if query_params.role_id:
            conditions.append(f"role_id = ${param_count}")
            params.append(query_params.role_id)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if not query_params.include_expired:
            conditions.append("(expires_at IS NULL OR expires_at > NOW())")

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0