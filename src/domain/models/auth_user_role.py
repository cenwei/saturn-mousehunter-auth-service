"""
认证服务 - 用户角色关系Domain Model
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class UserType(str, Enum):
    """用户类型"""
    ADMIN = "ADMIN"      # 管理员用户
    TENANT = "TENANT"    # 租户用户


class UserRoleBase(BaseModel):
    """用户角色关系基础模型"""
    user_id: str = Field(..., description="用户ID")
    user_type: UserType = Field(..., description="用户类型")
    role_id: str = Field(..., description="角色ID")
    granted_by: Optional[str] = Field(None, description="授权人ID")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    is_active: bool = Field(True, description="是否激活")


class UserRoleIn(UserRoleBase):
    """用户角色关系创建模型"""
    pass


class UserRoleUpdate(BaseModel):
    """用户角色关系更新模型"""
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class UserRoleOut(UserRoleBase):
    """用户角色关系输出模型"""
    id: str = Field(..., description="关系ID")
    granted_at: datetime = Field(..., description="授权时间")
    role_name: Optional[str] = Field(None, description="角色名称")
    role_code: Optional[str] = Field(None, description="角色编码")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'UserRoleOut':
        """从字典创建对象"""
        return cls(**data)


class UserRoleQuery(BaseModel):
    """用户角色关系查询模型"""
    user_id: Optional[str] = Field(None, description="用户ID")
    user_type: Optional[UserType] = Field(None, description="用户类型")
    role_id: Optional[str] = Field(None, description="角色ID")
    is_active: Optional[bool] = Field(None, description="是否激活")
    include_expired: bool = Field(False, description="是否包含过期记录")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class UserRoleAssignment(BaseModel):
    """用户角色分配模型"""
    user_id: str = Field(..., description="用户ID")
    user_type: UserType = Field(..., description="用户类型")
    role_ids: list[str] = Field(..., description="角色ID列表")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class UserPermissions(BaseModel):
    """用户权限模型"""
    user_id: str = Field(..., description="用户ID")
    user_type: UserType = Field(..., description="用户类型")
    permissions: list[str] = Field(..., description="权限编码列表")
    roles: list[str] = Field(..., description="角色编码列表")