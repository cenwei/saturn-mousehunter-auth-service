"""
基础测试配置和工具类
"""
import os
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator, Dict, Any

# 设置测试环境变量
os.environ["SERVICE_ENVIRONMENT"] = "test"
os.environ["DATABASE_NAME"] = "saturn_auth_test"
os.environ["LOG_LEVEL"] = "ERROR"


class AsyncTestCase(unittest.TestCase):
    """支持异步测试的基础测试类"""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def async_test(self, coro):
        """运行异步测试"""
        return self.loop.run_until_complete(coro)


class MockDatabase:
    """模拟数据库连接"""

    def __init__(self):
        self.data = {}
        self.connected = True

    async def execute(self, query: str, *args) -> str:
        return "mocked_result"

    async def fetch(self, query: str, *args) -> list:
        return []

    async def fetchrow(self, query: str, *args) -> dict:
        return {}


def create_mock_config() -> Dict[str, Any]:
    """创建模拟配置"""
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_pass"
        },
        "jwt": {
            "secret_key": "test_secret_key",
            "algorithm": "HS256",
            "expire_minutes": 30
        },
        "app": {
            "port": 8001,
            "debug": True
        }
    }


# 全局测试配置
TEST_CONFIG = create_mock_config()