"""
认证服务 - 数据库DAO依赖注入
"""
from infrastructure.db import AsyncDAO

# Global DAO instance will be set by main.py
_dao: AsyncDAO = None


def set_dao(dao: AsyncDAO):
    """Set the global DAO instance"""
    global _dao
    _dao = dao


def get_dao() -> AsyncDAO:
    """Get the global DAO instance"""
    if _dao is None:
        raise RuntimeError("DAO not initialized. Call set_dao() first.")
    return _dao