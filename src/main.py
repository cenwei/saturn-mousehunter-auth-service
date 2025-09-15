"""
认证服务 - 主应用文件
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from saturn_mousehunter_shared.log.logger import get_logger

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Find .env file in the project root (one level up from src)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
    else:
        print(f"⚠️  .env file not found at: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, skipping .env loading")

from infrastructure.config import get_app_config
from infrastructure.db import AsyncDAO
from infrastructure.config import get_database_config
from api.routes import admin_users, tenant_users

log = get_logger(__name__)

# 获取配置
app_config = get_app_config()
db_config = get_database_config()

# 全局数据库连接
dao: AsyncDAO = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global dao

    # 启动阶段
    log.info(f"启动认证服务 - {app_config.app_name} v{app_config.version}")
    dao = AsyncDAO(db_config.connection_string, db_config.min_connections, db_config.max_connections)
    await dao.init_pool()
    log.info(f"认证服务已启动 - {app_config.app_name} v{app_config.version}")

    yield

    # 关闭阶段
    log.info("正在关闭认证服务...")
    if dao:
        await dao.close_pool()
    log.info("认证服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=app_config.app_name,
    version=app_config.version,
    debug=app_config.debug,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.cors.allow_origins,
    allow_credentials=app_config.cors.allow_credentials,
    allow_methods=app_config.cors.allow_methods,
    allow_headers=app_config.cors.allow_headers,
)


@app.get("/health")
async def health_check():
    """健康检查"""
    db_healthy = await dao.health_check() if dao else False
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": app_config.app_name,
        "version": app_config.version,
        "database": "connected" if db_healthy else "disconnected"
    }


# 注册路由
app.include_router(admin_users.router, prefix="/api/v1")
app.include_router(tenant_users.router, prefix="/api/v1")


# 依赖注入工厂函数
def get_dao():
    return dao


if __name__ == "__main__":
    import uvicorn
    import sys
    import os

    # 添加src目录到Python路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.reload,
        log_level=app_config.log_level.lower()
    )