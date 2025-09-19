"""
认证服务 - 管理员用户Domain Model
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, validator


class AdminUserType(str, Enum):
    """管理员用户类型/等级"""
    ADMIN = "admin"                    # 普通管理员
    SUPER_ADMIN = "super_admin"        # 超级管理员


class AdminUserBase(BaseModel):
    """管理员用户基础模型"""
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=200, description="真实姓名")
    is_active: bool = Field(True, description="是否激活")
    is_superuser: bool = Field(False, description="是否超级用户")

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v.lower()


class AdminUserIn(AdminUserBase):
    """管理员用户创建模型"""
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


class AdminUserUpdate(BaseModel):
    """管理员用户更新模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    user_type: Optional[AdminUserType] = Field(None, description="用户类型")
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

    @validator('is_superuser', always=True)
    def sync_user_type_with_superuser(cls, v, values):
        """根据user_type同步is_superuser字段"""
        user_type = values.get('user_type')
        if user_type is not None:
            return user_type == AdminUserType.SUPER_ADMIN
        return v

    def dict(self, **kwargs):
        """重写dict方法，确保user_type正确映射到is_superuser"""
        data = super().dict(**kwargs)

        # 如果设置了user_type，同步到is_superuser并移除user_type字段
        if self.user_type is not None:
            data['is_superuser'] = (self.user_type == AdminUserType.SUPER_ADMIN)
            # 移除user_type字段，因为数据库没有这个列
            data.pop('user_type', None)

        return data


class AdminUserOut(AdminUserBase):
    """管理员用户输出模型"""
    id: str = Field(..., description="用户ID")
    user_type: str = Field(default="ADMIN", description="用户类型")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'AdminUserOut':
        """从字典创建对象"""
        # 根据is_superuser字段确定user_type
        if data.get('is_superuser'):
            data['user_type'] = AdminUserType.SUPER_ADMIN.value
        else:
            data['user_type'] = AdminUserType.ADMIN.value
        return cls(**data)

    def dict(self, **kwargs):
        """重写dict方法，确保返回正确的用户类型"""
        data = super().dict(**kwargs)

        # 根据is_superuser设置正确的user_type
        if self.is_superuser:
            data['user_type'] = AdminUserType.SUPER_ADMIN.value
        else:
            data['user_type'] = AdminUserType.ADMIN.value

        return data


class AdminUserInternal(AdminUserOut):
    """管理员用户内部模型（包含敏感信息，仅用于服务内部）"""
    password_hash: str = Field(..., description="密码哈希值")

    @classmethod
    def from_dict(cls, data: dict) -> 'AdminUserInternal':
        """从字典创建对象"""
        return cls(**data)


class AdminUserQuery(BaseModel):
    """管理员用户查询模型"""
    username: Optional[str] = Field(None, description="用户名模糊查询")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_superuser: Optional[bool] = Field(None, description="是否超级用户")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class AdminUserLogin(BaseModel):
    """管理员用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class AdminUserResponse(BaseModel):
    """管理员用户响应模型"""
    user: AdminUserOut = Field(..., serialization_alias="user_info", description="用户信息")
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None

    model_config = {"populate_by_name": True}