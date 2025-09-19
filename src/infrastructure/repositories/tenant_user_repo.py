"""
认证服务 - 租户用户Repository
"""
from datetime import datetime
from typing import List, Optional

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_tenant_user import TenantUserIn, TenantUserOut, TenantUserUpdate, TenantUserQuery

log = get_logger(__name__)

TABLE = "mh_auth_tenant_users"


class TenantUserRepo:
    """租户用户Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_tenant_user_create_seconds")
    async def create(self, user_data: TenantUserIn) -> TenantUserOut:
        """创建租户用户"""
        user_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, tenant_id, username, email, password_hash, full_name,
            is_active, is_tenant_admin, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            user_id,
            user_data.tenant_id,
            user_data.username,
            user_data.email,
            user_data.password_hash,
            user_data.full_name,
            user_data.is_active,
            user_data.is_tenant_admin,
            now,
            now
        )

        log.info(f"Created tenant user: {user_data.username} for tenant: {user_data.tenant_id}")
        return TenantUserOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_tenant_user_get_seconds")
    async def get_by_id(self, user_id: str) -> Optional[TenantUserOut]:
        """根据ID获取租户用户"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, user_id)

        if row:
            return TenantUserOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_tenant_user_get_by_username_seconds")
    async def get_by_username(self, tenant_id: str, username: str) -> Optional[TenantUserOut]:
        """根据租户ID和用户名获取租户用户"""
        query = f"SELECT * FROM {TABLE} WHERE tenant_id = $1 AND username = $2"
        row = await self.dao.fetch_one(query, tenant_id, username)

        if row:
            return TenantUserOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_tenant_user_get_by_email_seconds")
    async def get_by_email(self, tenant_id: str, email: str) -> Optional[TenantUserOut]:
        """根据租户ID和邮箱获取租户用户"""
        query = f"SELECT * FROM {TABLE} WHERE tenant_id = $1 AND email = $2"
        row = await self.dao.fetch_one(query, tenant_id, email)

        if row:
            return TenantUserOut.from_dict(dict(row))
        return None

    @measure("db_tenant_user_update_seconds")
    async def update(self, user_id: str, update_data: TenantUserUpdate) -> Optional[TenantUserOut]:
        """更新租户用户"""
        set_clauses = []
        params = []
        param_count = 1

        # 动态构建UPDATE语句，只更新非None的字段
        for field, value in update_data.dict(exclude_unset=True).items():
            if field not in ['updated_at', 'password'] and value is not None:
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

        try:
            row = await self.dao.fetch_one(query, *params)
            if row:
                log.info(f"Updated tenant user: {user_id}")
                return TenantUserOut.from_dict(dict(row))
            return None
        except Exception as e:
            log.error(f"Failed to update tenant user {user_id}: {str(e)}")
            raise

    @measure("db_tenant_user_delete_seconds")
    async def delete(self, user_id: str) -> bool:
        """删除租户用户（软删除）"""
        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = $1
        WHERE id = $2
        """

        result = await self.dao.execute(query, datetime.now(), user_id)
        success = result > 0

        if success:
            log.info(f"Deleted tenant user: {user_id}")

        return success

    @read_only_guard()
    @measure("db_tenant_user_list_seconds")
    async def list(self, query_params: TenantUserQuery) -> List[TenantUserOut]:
        """获取租户用户列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.tenant_id:
            conditions.append(f"tenant_id = ${param_count}")
            params.append(query_params.tenant_id)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.is_tenant_admin is not None:
            conditions.append(f"is_tenant_admin = ${param_count}")
            params.append(query_params.is_tenant_admin)
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
        return [TenantUserOut.from_dict(dict(row)) for row in rows]

    @measure("db_tenant_user_update_last_login_seconds")
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
    @measure("db_tenant_user_count_seconds")
    async def count(self, query_params: TenantUserQuery) -> int:
        """获取租户用户总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件（复用list方法的逻辑）
        if query_params.tenant_id:
            conditions.append(f"tenant_id = ${param_count}")
            params.append(query_params.tenant_id)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.is_tenant_admin is not None:
            conditions.append(f"is_tenant_admin = ${param_count}")
            params.append(query_params.is_tenant_admin)
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

    @read_only_guard()
    @measure("db_tenant_user_list_by_tenant_seconds")
    async def list_by_tenant(self, tenant_id: str, limit: int = 20, offset: int = 0) -> List[TenantUserOut]:
        """根据租户ID获取用户列表"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE tenant_id = $1 AND is_active = true
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
        """

        rows = await self.dao.fetch_all(query, tenant_id, limit, offset)
        return [TenantUserOut.from_dict(dict(row)) for row in rows]