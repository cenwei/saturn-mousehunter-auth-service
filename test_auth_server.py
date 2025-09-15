"""
认证服务启动测试
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: dict


app = FastAPI(
    title="Saturn MouseHunter Auth Service",
    version="1.0.0",
    description="认证服务 - 提供JWT认证、用户管理功能"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简化的用户数据（生产环境应该从数据库读取）
USERS_DB = {
    "admin": {
        "username": "admin",
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
        "user_type": "admin_user",
        "is_active": True
    }
}

JWT_SECRET = "saturn-mousehunter-auth-secret-key"
JWT_ALGORITHM = "HS256"


@app.get("/")
def root():
    """根路径"""
    return {
        "service": "Saturn MouseHunter Auth Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """用户登录"""
    # 查找用户
    user = USERS_DB.get(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    # 验证密码
    if not bcrypt.checkpw(request.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="密码错误")

    # 检查用户状态
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="用户已被禁用")

    # 生成JWT令牌
    payload = {
        "user_id": user["username"],  # 简化实现
        "username": user["username"],
        "user_type": user["user_type"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return LoginResponse(
        access_token=access_token,
        user_info={
            "username": user["username"],
            "user_type": user["user_type"],
            "is_active": user["is_active"]
        }
    )


@app.get("/api/v1/auth/verify")
def verify_token(token: str):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "user_type": payload.get("user_type"),
            "expires_at": payload.get("exp")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效令牌")


@app.get("/api/v1/users/me")
def get_current_user(authorization: str = None):
    """获取当前用户信息"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少Authorization头")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("username")
        user = USERS_DB.get(username)

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        return {
            "username": user["username"],
            "user_type": user["user_type"],
            "is_active": user["is_active"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效令牌")


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动认证服务...")
    print("📍 访问地址:")
    print("   - API文档: http://192.168.8.168:8001/docs")
    print("   - 健康检查: http://192.168.8.168:8001/health")
    print("   - 登录测试: POST http://192.168.8.168:8001/api/v1/auth/login")
    print("     用户名: admin")
    print("     密码: admin123")

    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )