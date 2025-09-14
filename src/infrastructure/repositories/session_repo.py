"""
认证服务 - 会话Repository
"""
from datetime import datetime, timedelta
from typing import List, Optional

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_session import (
    SessionIn, SessionOut, SessionUpdate, SessionQuery,
    SessionStats
)

log = get_logger(__name__)

TABLE = "mh_auth_sessions"


class SessionRepo:
    """会话Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_session_create_seconds")
    async def create(self, session_data: SessionIn) -> SessionOut:
        """创建会话"""
        session_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, user_id, user_type, session_token, refresh_token,
            ip_address, user_agent, expires_at, is_active, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            session_id,
            session_data.user_id,
            session_data.user_type.value,
            session_data.session_token,
            session_data.refresh_token,
            session_data.ip_address,
            session_data.user_agent,
            session_data.expires_at,
            session_data.is_active,
            now,
            now
        )

        log.info(f"Created session for user: {session_data.user_id}")
        return SessionOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_session_get_seconds")
    async def get_by_id(self, session_id: str) -> Optional[SessionOut]:
        """根据ID获取会话"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, session_id)

        if row:
            return SessionOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_session_get_by_token_seconds")
    async def get_by_session_token(self, session_token: str) -> Optional[SessionOut]:
        """根据会话令牌获取会话"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE session_token = $1 AND is_active = true AND expires_at > NOW()
        """
        row = await self.dao.fetch_one(query, session_token)

        if row:
            return SessionOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_session_get_by_refresh_token_seconds")
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[SessionOut]:
        """根据刷新令牌获取会话"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE refresh_token = $1 AND is_active = true AND expires_at > NOW()
        """
        row = await self.dao.fetch_one(query, refresh_token)

        if row:
            return SessionOut.from_dict(dict(row))
        return None

    @measure("db_session_update_seconds")
    async def update(self, session_id: str, update_data: SessionUpdate) -> Optional[SessionOut]:
        """更新会话"""
        set_clauses = []
        params = []
        param_count = 1

        # 动态构建UPDATE语句
        for field, value in update_data.dict(exclude_unset=True).items():
            set_clauses.append(f"{field} = ${param_count}")
            params.append(value)
            param_count += 1

        if not set_clauses:
            return await self.get_by_id(session_id)

        # 添加更新时间
        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.now())
        param_count += 1

        # 添加WHERE条件
        params.append(session_id)

        query = f"""
        UPDATE {TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = ${param_count}
        RETURNING *
        """

        row = await self.dao.fetch_one(query, *params)
        if row:
            log.info(f"Updated session: {session_id}")
            return SessionOut.from_dict(dict(row))
        return None

    @measure("db_session_deactivate_seconds")
    async def deactivate(self, session_id: str) -> bool:
        """停用会话"""
        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = $1
        WHERE id = $2
        """

        result = await self.dao.execute(query, datetime.now(), session_id)
        success = result > 0

        if success:
            log.info(f"Deactivated session: {session_id}")

        return success

    @measure("db_session_deactivate_by_token_seconds")
    async def deactivate_by_token(self, session_token: str) -> bool:
        """根据会话令牌停用会话"""
        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = $1
        WHERE session_token = $2
        """

        result = await self.dao.execute(query, datetime.now(), session_token)
        success = result > 0

        if success:
            log.info(f"Deactivated session by token")

        return success

    @measure("db_session_deactivate_user_sessions_seconds")
    async def deactivate_user_sessions(self, user_id: str, user_type: str, exclude_session_id: str = None) -> int:
        """停用用户的所有其他会话"""
        conditions = ["user_id = $1", "user_type = $2", "is_active = true"]
        params = [user_id, user_type]
        param_count = 3

        if exclude_session_id:
            conditions.append(f"id != ${param_count}")
            params.append(exclude_session_id)

        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = NOW()
        WHERE {' AND '.join(conditions)}
        """

        result = await self.dao.execute(query, *params)

        if result > 0:
            log.info(f"Deactivated {result} sessions for user: {user_id}")

        return result

    @read_only_guard()
    @measure("db_session_list_seconds")
    async def list(self, query_params: SessionQuery) -> List[SessionOut]:
        """获取会话列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.user_id:
            conditions.append(f"user_id = ${param_count}")
            params.append(query_params.user_id)
            param_count += 1

        if query_params.user_type:
            conditions.append(f"user_type = ${param_count}")
            params.append(query_params.user_type.value)
            param_count += 1

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.ip_address:
            conditions.append(f"ip_address = ${param_count}")
            params.append(query_params.ip_address)
            param_count += 1

        # 处理过期会话
        if not query_params.include_expired:
            conditions.append("expires_at > NOW()")

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
        return [SessionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_session_count_seconds")
    async def count(self, query_params: SessionQuery) -> int:
        """获取会话总数"""
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

        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.ip_address:
            conditions.append(f"ip_address = ${param_count}")
            params.append(query_params.ip_address)
            param_count += 1

        if not query_params.include_expired:
            conditions.append("expires_at > NOW()")

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0

    @read_only_guard()
    @measure("db_session_list_user_sessions_seconds")
    async def list_user_sessions(self, user_id: str, user_type: str, active_only: bool = True) -> List[SessionOut]:
        """获取用户的所有会话"""
        conditions = ["user_id = $1", "user_type = $2"]
        params = [user_id, user_type]

        if active_only:
            conditions.append("is_active = true AND expires_at > NOW()")

        query = f"""
        SELECT * FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
        """

        rows = await self.dao.fetch_all(query, *params)
        return [SessionOut.from_dict(dict(row)) for row in rows]

    @measure("db_session_cleanup_expired_seconds")
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = NOW()
        WHERE is_active = true AND expires_at <= NOW()
        """

        result = await self.dao.execute(query)

        if result > 0:
            log.info(f"Cleaned up {result} expired sessions")

        return result

    @measure("db_session_delete_old_sessions_seconds")
    async def delete_old_sessions(self, days: int = 30) -> int:
        """删除旧会话记录"""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = f"""
        DELETE FROM {TABLE}
        WHERE is_active = false AND updated_at < $1
        """

        result = await self.dao.execute(query, cutoff_date)

        if result > 0:
            log.info(f"Deleted {result} old session records (older than {days} days)")

        return result

    @read_only_guard()
    @measure("db_session_get_stats_seconds")
    async def get_stats(self) -> SessionStats:
        """获取会话统计"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        query = f"""
        SELECT
            COUNT(*) as total_sessions,
            SUM(CASE WHEN is_active = true AND expires_at > NOW() THEN 1 ELSE 0 END) as active_sessions,
            SUM(CASE WHEN created_at >= $1 THEN 1 ELSE 0 END) as today_logins,
            COUNT(DISTINCT CASE WHEN created_at >= $1 THEN user_id END) as unique_users_today
        FROM {TABLE}
        """

        row = await self.dao.fetch_one(query, today_start)

        if row:
            return SessionStats(
                total_sessions=row['total_sessions'] or 0,
                active_sessions=row['active_sessions'] or 0,
                today_logins=row['today_logins'] or 0,
                unique_users_today=row['unique_users_today'] or 0
            )

        return SessionStats(
            total_sessions=0, active_sessions=0,
            today_logins=0, unique_users_today=0
        )

    @read_only_guard()
    @measure("db_session_validate_token_seconds")
    async def validate_session_token(self, session_token: str) -> bool:
        """验证会话令牌是否有效"""
        query = f"""
        SELECT 1 FROM {TABLE}
        WHERE session_token = $1 AND is_active = true AND expires_at > NOW()
        """
        row = await self.dao.fetch_one(query, session_token)
        return row is not None

    @measure("db_session_extend_expiry_seconds")
    async def extend_session_expiry(self, session_id: str, new_expires_at: datetime) -> bool:
        """延长会话过期时间"""
        query = f"""
        UPDATE {TABLE}
        SET expires_at = $1, updated_at = $2
        WHERE id = $3 AND is_active = true
        """

        result = await self.dao.execute(query, new_expires_at, datetime.now(), session_id)
        success = result > 0

        if success:
            log.info(f"Extended session expiry: {session_id}")

        return success