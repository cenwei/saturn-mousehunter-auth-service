"""
认证服务 - 主应用文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.config import get_app_config
from infrastructure.db import AsyncDAO
from infrastructure.config import get_database_config
from api.routes import admin_users

log = get_logger(__name__)

# 获取配置
app_config = get_app_config()
db_config = get_database_config()

# 创建FastAPI应用
app = FastAPI(
    title=app_config.app_name,
    version=app_config.version,
    debug=app_config.debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.cors.allow_origins,
    allow_credentials=app_config.cors.allow_credentials,
    allow_methods=app_config.cors.allow_methods,
    allow_headers=app_config.cors.allow_headers,
)

# 全局数据库连接
dao: AsyncDAO = None


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global dao
    dao = AsyncDAO(db_config.connection_string, db_config.min_connections, db_config.max_connections)
    await dao.init_pool()
    log.info(f"认证服务已启动 - {app_config.app_name} v{app_config.version}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global dao
    if dao:
        await dao.close_pool()
    log.info("认证服务已关闭")


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


# 依赖注入工厂函数
def get_dao():
    return dao


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.reload,
        log_level=app_config.log_level.lower()
    )