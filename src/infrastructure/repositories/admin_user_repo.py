"""
认证服务 - 管理员用户Repository
使用新的表前缀: mh_auth_admin_users
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_admin_user import AdminUserIn, AdminUserOut, AdminUserUpdate, AdminUserQuery

log = get_logger(__name__)

# 使用mh_auth_前缀
TABLE = "mh_auth_admin_users"


class AdminUserRepo:
    """管理员用户Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_admin_user_create_seconds")
    async def create(self, user_data: AdminUserIn) -> AdminUserOut:
        """创建管理员用户"""
        user_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, username, email, password_hash, full_name,
            is_active, is_superuser, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            user_id,
            user_data.username,
            user_data.email,
            user_data.password_hash,
            user_data.full_name,
            user_data.is_active,
            user_data.is_superuser,
            now,
            now
        )

        log.info(f"Created admin user: {user_data.username}")
        return AdminUserOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_admin_user_get_seconds")
    async def get_by_id(self, user_id: str) -> Optional[AdminUserOut]:
        """根据ID获取管理员用户"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, user_id)

        if row:
            return AdminUserOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_admin_user_get_by_username_seconds")
    async def get_by_username(self, username: str) -> Optional[AdminUserOut]:
        """根据用户名获取管理员用户"""
        query = f"SELECT * FROM {TABLE} WHERE username = $1"
        row = await self.dao.fetch_one(query, username)

        if row:
            return AdminUserOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_admin_user_get_by_email_seconds")
    async def get_by_email(self, email: str) -> Optional[AdminUserOut]:
        """根据邮箱获取管理员用户"""
        query = f"SELECT * FROM {TABLE} WHERE email = $1"
        row = await self.dao.fetch_one(query, email)

        if row:
            return AdminUserOut.from_dict(dict(row))
        return None

    @measure("db_admin_user_update_seconds")
    async def update(self, user_id: str, update_data: AdminUserUpdate) -> Optional[AdminUserOut]:
        """更新管理员用户"""
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
            return await self.get_by_id(user_id)

        # 添加更新时间
        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.now())
        param_count += 1

        # 添加WHERE条件
        params.append(user_id)

        query = f"""
        UPDATE {TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = ${param_count}
        RETURNING *
        """

        row = await self.dao.fetch_one(query, *params)
        if row:
            log.info(f"Updated admin user: {user_id}")
            return AdminUserOut.from_dict(dict(row))
        return None

    @measure("db_admin_user_delete_seconds")
    async def delete(self, user_id: str) -> bool:
        """删除管理员用户（软删除）"""
        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = $1
        WHERE id = $2
        """

        result = await self.dao.execute(query, datetime.now(), user_id)
        success = result > 0

        if success:
            log.info(f"Deleted admin user: {user_id}")

        return success

    @read_only_guard()
    @measure("db_admin_user_list_seconds")
    async def list(self, query_params: AdminUserQuery) -> List[AdminUserOut]:
        """获取管理员用户列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.is_superuser is not None:
            conditions.append(f"is_superuser = ${param_count}")
            params.append(query_params.is_superuser)
            param_count += 1

        if query_params.username:
            conditions.append(f"username ILIKE ${param_count}")
            params.append(f"%{query_params.username}%")
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
        return [AdminUserOut.from_dict(dict(row)) for row in rows]

    @measure("db_admin_user_update_last_login_seconds")
    async def update_last_login(self, user_id: str) -> bool:
        """更新最后登录时间"""
        query = f"""
        UPDATE {TABLE}
        SET last_login_at = $1, updated_at = $1
        WHERE id = $2
        """

        now = datetime.now()
        result = await self.dao.execute(query, now, user_id)
        return result > 0

    @read_only_guard()
    @measure("db_admin_user_count_seconds")
    async def count(self, query_params: AdminUserQuery) -> int:
        """获取管理员用户总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件 (复用list方法的逻辑)
        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.is_superuser is not None:
            conditions.append(f"is_superuser = ${param_count}")
            params.append(query_params.is_superuser)
            param_count += 1

        if query_params.username:
            conditions.append(f"username ILIKE ${param_count}")
            params.append(f"%{query_params.username}%")
            param_count += 1

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0