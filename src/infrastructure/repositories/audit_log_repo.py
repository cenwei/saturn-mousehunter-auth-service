"""
认证服务 - 审计日志Repository
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_audit_log import AuditLogIn, AuditLogOut, AuditLogQuery, AuditLogStats

log = get_logger(__name__)

TABLE = "mh_auth_audit_logs"


class AuditLogRepo:
    """审计日志Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_audit_log_create_seconds")
    async def create(self, audit_log_data: AuditLogIn) -> AuditLogOut:
        """创建审计日志"""
        audit_log_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, user_id, user_type, action, resource, resource_id,
            details, ip_address, user_agent, success, error_message, created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
        ) RETURNING *
        """

        # 转换details为JSONB字符串
        import json
        details_json = json.dumps(audit_log_data.details) if audit_log_data.details else '{}'

        user_type_value = audit_log_data.user_type.value if audit_log_data.user_type else None

        row = await self.dao.fetch_one(
            query,
            audit_log_id,
            audit_log_data.user_id,
            user_type_value,
            audit_log_data.action,
            audit_log_data.resource,
            audit_log_data.resource_id,
            details_json,
            audit_log_data.ip_address,
            audit_log_data.user_agent,
            audit_log_data.success,
            audit_log_data.error_message,
            now
        )

        return AuditLogOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_audit_log_get_seconds")
    async def get_by_id(self, audit_log_id: str) -> Optional[AuditLogOut]:
        """根据ID获取审计日志"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, audit_log_id)

        if row:
            return AuditLogOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_audit_log_list_seconds")
    async def list(self, query_params: AuditLogQuery) -> List[AuditLogOut]:
        """获取审计日志列表"""
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

        if query_params.action:
            conditions.append(f"action ILIKE ${param_count}")
            params.append(f"%{query_params.action}%")
            param_count += 1

        if query_params.resource:
            conditions.append(f"resource = ${param_count}")
            params.append(query_params.resource)
            param_count += 1

        if query_params.success is not None:
            conditions.append(f"success = ${param_count}")
            params.append(query_params.success)
            param_count += 1

        if query_params.start_date:
            conditions.append(f"created_at >= ${param_count}")
            params.append(query_params.start_date)
            param_count += 1

        if query_params.end_date:
            conditions.append(f"created_at <= ${param_count}")
            params.append(query_params.end_date)
            param_count += 1

        if query_params.ip_address:
            conditions.append(f"ip_address = ${param_count}")
            params.append(query_params.ip_address)
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
        return [AuditLogOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_audit_log_count_seconds")
    async def count(self, query_params: AuditLogQuery) -> int:
        """获取审计日志总数"""
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

        if query_params.action:
            conditions.append(f"action ILIKE ${param_count}")
            params.append(f"%{query_params.action}%")
            param_count += 1

        if query_params.resource:
            conditions.append(f"resource = ${param_count}")
            params.append(query_params.resource)
            param_count += 1

        if query_params.success is not None:
            conditions.append(f"success = ${param_count}")
            params.append(query_params.success)
            param_count += 1

        if query_params.start_date:
            conditions.append(f"created_at >= ${param_count}")
            params.append(query_params.start_date)
            param_count += 1

        if query_params.end_date:
            conditions.append(f"created_at <= ${param_count}")
            params.append(query_params.end_date)
            param_count += 1

        if query_params.ip_address:
            conditions.append(f"ip_address = ${param_count}")
            params.append(query_params.ip_address)
            param_count += 1

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0

    @read_only_guard()
    @measure("db_audit_log_stats_seconds")
    async def get_stats(self, days: int = 30) -> AuditLogStats:
        """获取审计日志统计"""
        start_date = datetime.now() - timedelta(days=days)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        query = f"""
        SELECT
            COUNT(*) as total_count,
            SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as failed_count,
            SUM(CASE WHEN created_at >= $1 THEN 1 ELSE 0 END) as today_count,
            SUM(CASE WHEN created_at >= $2 THEN 1 ELSE 0 END) as this_week_count,
            SUM(CASE WHEN created_at >= $3 THEN 1 ELSE 0 END) as this_month_count
        FROM {TABLE}
        WHERE created_at >= $4
        """

        row = await self.dao.fetch_one(query, today_start, week_start, month_start, start_date)

        if row:
            return AuditLogStats(
                total_count=row['total_count'] or 0,
                success_count=row['success_count'] or 0,
                failed_count=row['failed_count'] or 0,
                today_count=row['today_count'] or 0,
                this_week_count=row['this_week_count'] or 0,
                this_month_count=row['this_month_count'] or 0
            )

        return AuditLogStats(
            total_count=0, success_count=0, failed_count=0,
            today_count=0, this_week_count=0, this_month_count=0
        )

    @read_only_guard()
    @measure("db_audit_log_list_by_user_seconds")
    async def list_by_user(self, user_id: str, user_type: str, limit: int = 20, offset: int = 0) -> List[AuditLogOut]:
        """根据用户获取审计日志"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE user_id = $1 AND user_type = $2
        ORDER BY created_at DESC
        LIMIT $3 OFFSET $4
        """

        rows = await self.dao.fetch_all(query, user_id, user_type, limit, offset)
        return [AuditLogOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_audit_log_list_recent_seconds")
    async def list_recent(self, hours: int = 24, limit: int = 100) -> List[AuditLogOut]:
        """获取最近的审计日志"""
        since = datetime.now() - timedelta(hours=hours)
        query = f"""
        SELECT * FROM {TABLE}
        WHERE created_at >= $1
        ORDER BY created_at DESC
        LIMIT $2
        """

        rows = await self.dao.fetch_all(query, since, limit)
        return [AuditLogOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_audit_log_list_failed_seconds")
    async def list_failed_actions(self, hours: int = 24, limit: int = 100) -> List[AuditLogOut]:
        """获取失败的操作日志"""
        since = datetime.now() - timedelta(hours=hours)
        query = f"""
        SELECT * FROM {TABLE}
        WHERE created_at >= $1 AND success = false
        ORDER BY created_at DESC
        LIMIT $2
        """

        rows = await self.dao.fetch_all(query, since, limit)
        return [AuditLogOut.from_dict(dict(row)) for row in rows]

    @measure("db_audit_log_cleanup_seconds")
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """清理旧的审计日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = f"DELETE FROM {TABLE} WHERE created_at < $1"

        result = await self.dao.execute(query, cutoff_date)

        if result > 0:
            log.info(f"Cleaned up {result} old audit logs (older than {days} days)")

        return result

    # 便利方法：记录特定类型的审计日志
    async def log_login_attempt(self, user_id: str, user_type: str, success: bool,
                               ip_address: str = None, user_agent: str = None,
                               error_message: str = None) -> AuditLogOut:
        """记录登录尝试"""
        audit_data = AuditLogIn(
            user_id=user_id,
            user_type=user_type,
            action="LOGIN",
            resource="authentication",
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
        return await self.create(audit_data)

    async def log_logout(self, user_id: str, user_type: str,
                        ip_address: str = None, user_agent: str = None) -> AuditLogOut:
        """记录登出"""
        audit_data = AuditLogIn(
            user_id=user_id,
            user_type=user_type,
            action="LOGOUT",
            resource="authentication",
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self.create(audit_data)

    async def log_permission_change(self, user_id: str, user_type: str, target_user_id: str,
                                   action: str, details: Dict[str, Any] = None,
                                   ip_address: str = None, user_agent: str = None) -> AuditLogOut:
        """记录权限变更"""
        audit_data = AuditLogIn(
            user_id=user_id,
            user_type=user_type,
            action=action,
            resource="permission",
            resource_id=target_user_id,
            details=details or {},
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self.create(audit_data)