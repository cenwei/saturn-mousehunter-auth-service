"""
认证服务 - 基础数据访问对象
"""
import asyncio
from typing import Any, List, Optional, Dict
from contextlib import asynccontextmanager
import asyncpg
from saturn_mousehunter_shared.log.logger import get_logger
from saturn_mousehunter_shared.aop.decorators import measure

log = get_logger(__name__)


class AsyncDAO:
    """异步数据访问对象基类"""

    def __init__(self, connection_string: str, min_connections: int = 5, max_connections: int = 20):
        self.connection_string = connection_string
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool: Optional[asyncpg.Pool] = None

    async def init_pool(self) -> None:
        """初始化连接池"""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    self.connection_string,
                    min_size=self.min_connections,
                    max_size=self.max_connections,
                    command_timeout=60,
                )
                log.info("数据库连接池初始化成功")
            except Exception as e:
                log.error(f"数据库连接池初始化失败: {e}")
                raise

    async def close_pool(self) -> None:
        """关闭连接池"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            log.info("数据库连接池已关闭")

    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接"""
        if not self.pool:
            await self.init_pool()

        async with self.pool.acquire() as connection:
            yield connection

    @measure("db_fetch_one_seconds")
    async def fetch_one(self, query: str, *args) -> Optional[asyncpg.Record]:
        """执行查询并返回单条记录"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetchrow(query, *args)
                log.debug(f"fetch_one query: {query[:100]}...")
                return result
            except Exception as e:
                log.error(f"fetch_one 执行失败: {e}, query: {query[:100]}...")
                raise

    @measure("db_fetch_all_seconds")
    async def fetch_all(self, query: str, *args) -> List[asyncpg.Record]:
        """执行查询并返回所有记录"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetch(query, *args)
                log.debug(f"fetch_all query: {query[:100]}, count: {len(result)}")
                return result
            except Exception as e:
                log.error(f"fetch_all 执行失败: {e}, query: {query[:100]}...")
                raise

    @measure("db_execute_seconds")
    async def execute(self, query: str, *args) -> int:
        """执行非查询SQL并返回影响行数"""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(query, *args)
                # PostgreSQL返回的是状态字符串，如 "UPDATE 1"
                if isinstance(result, str):
                    parts = result.split()
                    if len(parts) > 1 and parts[-1].isdigit():
                        affected_rows = int(parts[-1])
                    else:
                        affected_rows = 0
                else:
                    affected_rows = result

                log.debug(f"execute query: {query[:100]}, affected: {affected_rows}")
                return affected_rows
            except Exception as e:
                log.error(f"execute 执行失败: {e}, query: {query[:100]}...")
                raise

    @measure("db_execute_many_seconds")
    async def execute_many(self, query: str, args_list: List[tuple]) -> int:
        """批量执行SQL"""
        async with self.get_connection() as conn:
            try:
                await conn.executemany(query, args_list)
                count = len(args_list)
                log.debug(f"execute_many query: {query[:100]}, count: {count}")
                return count
            except Exception as e:
                log.error(f"execute_many 执行失败: {e}, query: {query[:100]}...")
                raise

    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器"""
        async with self.get_connection() as conn:
            transaction = conn.transaction()
            try:
                await transaction.start()
                yield conn
                await transaction.commit()
                log.debug("事务提交成功")
            except Exception as e:
                await transaction.rollback()
                log.error(f"事务回滚: {e}")
                raise

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            log.error(f"数据库健康检查失败: {e}")
            return False

    async def get_pool_status(self) -> Dict[str, Any]:
        """获取连接池状态"""
        if not self.pool:
            return {"status": "not_initialized"}

        return {
            "status": "active",
            "size": self.pool.get_size(),
            "idle_count": self.pool.get_idle_size(),
            "max_size": self.pool.get_max_size(),
            "min_size": self.pool.get_min_size(),
        }

    def __repr__(self) -> str:
        return f"AsyncDAO(pool_size={self.max_connections})"