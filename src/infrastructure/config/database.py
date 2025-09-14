"""
认证服务 - 数据库配置
"""
import os
from typing import Optional
from dataclasses import dataclass
from saturn_mousehunter_shared.log.logger import get_logger

log = get_logger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    database: str
    username: str
    password: str
    min_connections: int = 5
    max_connections: int = 20
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    query_timeout: int = 60

    @property
    def connection_string(self) -> str:
        """获取连接字符串"""
        return (
            f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/"
            f"{self.database}?sslmode={self.ssl_mode}"
        )

    def __repr__(self) -> str:
        # 隐藏密码信息
        return (
            f"DatabaseConfig(host={self.host}, port={self.port}, "
            f"database={self.database}, username={self.username})"
        )


def get_database_config() -> DatabaseConfig:
    """从环境变量获取数据库配置"""

    # 读取基础配置
    host = os.getenv("AUTH_DB_HOST", "localhost")
    port = int(os.getenv("AUTH_DB_PORT", "5432"))
    database = os.getenv("AUTH_DB_NAME", "saturn_mousehunter_auth")
    username = os.getenv("AUTH_DB_USER", "postgres")
    password = os.getenv("AUTH_DB_PASSWORD", "")

    # 读取连接池配置
    min_connections = int(os.getenv("AUTH_DB_MIN_CONNECTIONS", "5"))
    max_connections = int(os.getenv("AUTH_DB_MAX_CONNECTIONS", "20"))

    # 读取其他配置
    ssl_mode = os.getenv("AUTH_DB_SSL_MODE", "prefer")
    connection_timeout = int(os.getenv("AUTH_DB_CONNECTION_TIMEOUT", "30"))
    query_timeout = int(os.getenv("AUTH_DB_QUERY_TIMEOUT", "60"))

    if not password:
        log.warning("数据库密码为空，请检查环境变量 AUTH_DB_PASSWORD")

    config = DatabaseConfig(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        min_connections=min_connections,
        max_connections=max_connections,
        ssl_mode=ssl_mode,
        connection_timeout=connection_timeout,
        query_timeout=query_timeout,
    )

    log.info(f"数据库配置已加载: {config}")
    return config


def get_test_database_config() -> DatabaseConfig:
    """获取测试数据库配置"""
    config = get_database_config()
    # 测试数据库通常添加 _test 后缀
    config.database = f"{config.database}_test"
    config.min_connections = 2
    config.max_connections = 5

    log.info(f"测试数据库配置: {config}")
    return config