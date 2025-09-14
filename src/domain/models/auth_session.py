"""
认证服务 - 会话Domain Model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .auth_user_role import UserType


class SessionBase(BaseModel):
    """会话基础模型"""
    user_id: str = Field(..., description="用户ID")
    user_type: UserType = Field(..., description="用户类型")
    session_token: str = Field(..., description="会话令牌")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    expires_at: datetime = Field(..., description="过期时间")
    is_active: bool = Field(True, description="是否激活")


class SessionIn(SessionBase):
    """会话创建模型"""
    pass


class SessionUpdate(BaseModel):
    """会话更新模型"""
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class SessionOut(SessionBase):
    """会话输出模型"""
    id: str = Field(..., description="会话ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'SessionOut':
        """从字典创建对象"""
        return cls(**data)


class SessionQuery(BaseModel):
    """会话查询模型"""
    user_id: Optional[str] = Field(None, description="用户ID")
    user_type: Optional[UserType] = Field(None, description="用户类型")
    is_active: Optional[bool] = Field(None, description="是否激活")
    include_expired: bool = Field(False, description="是否包含过期会话")
    ip_address: Optional[str] = Field(None, description="IP地址")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class SessionInfo(BaseModel):
    """会话信息模型"""
    session: SessionOut
    user_info: dict = Field(..., description="用户信息")
    permissions: list[str] = Field(default_factory=list, description="用户权限列表")
    roles: list[str] = Field(default_factory=list, description="用户角色列表")


class TokenPair(BaseModel):
    """令牌对模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class TokenRefreshRequest(BaseModel):
    """令牌刷新请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


class SessionStats(BaseModel):
    """会话统计模型"""
    total_sessions: int = Field(..., description="总会话数")
    active_sessions: int = Field(..., description="活跃会话数")
    today_logins: int = Field(..., description="今日登录数")
    unique_users_today: int = Field(..., description="今日独立用户数")