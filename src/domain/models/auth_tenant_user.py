"""
认证服务 - 租户用户Domain Model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class TenantUserBase(BaseModel):
    """租户用户基础模型"""
    tenant_id: str = Field(..., description="租户ID")
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=200, description="真实姓名")
    is_active: bool = Field(True, description="是否激活")
    is_tenant_admin: bool = Field(False, description="是否租户管理员")

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v.lower()


class TenantUserIn(TenantUserBase):
    """租户用户创建模型"""
    password: str = Field(..., min_length=8, description="密码")
    password_hash: Optional[str] = Field(None, description="密码哈希值（系统生成）")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含至少一个字母')
        return v


class TenantUserUpdate(BaseModel):
    """租户用户更新模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    is_tenant_admin: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, description="新密码")
    password_hash: Optional[str] = Field(None, description="新密码哈希值")

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('密码长度不能少于8位')
            if not any(c.isdigit() for c in v):
                raise ValueError('密码必须包含至少一个数字')
            if not any(c.isalpha() for c in v):
                raise ValueError('密码必须包含至少一个字母')
        return v


class TenantUserOut(TenantUserBase):
    """租户用户输出模型"""
    id: str = Field(..., description="用户ID")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'TenantUserOut':
        """从字典创建对象"""
        return cls(**data)


class TenantUserInternal(TenantUserOut):
    """租户用户内部模型（包含敏感信息，仅用于服务内部）"""
    password_hash: str = Field(..., description="密码哈希值")

    @classmethod
    def from_dict(cls, data: dict) -> 'TenantUserInternal':
        """从字典创建对象"""
        return cls(**data)


class TenantUserQuery(BaseModel):
    """租户用户查询模型"""
    tenant_id: Optional[str] = Field(None, description="租户ID")
    username: Optional[str] = Field(None, description="用户名模糊查询")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_tenant_admin: Optional[bool] = Field(None, description="是否租户管理员")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class TenantUserLogin(BaseModel):
    """租户用户登录模型"""
    tenant_id: str = Field(..., description="租户ID")
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TenantUserResponse(BaseModel):
    """租户用户响应模型"""
    user: TenantUserOut
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None