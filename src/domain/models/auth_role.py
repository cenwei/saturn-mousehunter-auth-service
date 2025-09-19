"""
认证服务 - 角色Domain Model
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    from .auth_permission import PermissionOut


class RoleScope(str, Enum):
    """角色范围"""
    GLOBAL = "GLOBAL"      # 全局角色
    TENANT = "TENANT"      # 租户角色
    SYSTEM = "SYSTEM"      # 系统角色


class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str = Field(..., min_length=2, max_length=100, description="角色名称")
    role_code: str = Field(..., min_length=2, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")
    scope: RoleScope = Field(RoleScope.GLOBAL, description="角色范围")
    is_system_role: bool = Field(False, description="是否系统角色")
    is_active: bool = Field(True, description="是否激活")

    @validator('role_code')
    def validate_role_code(cls, v):
        if not v.isupper() or not v.replace('_', '').isalnum():
            raise ValueError('角色编码必须为大写字母、数字和下划线组合')
        return v


class RoleIn(RoleBase):
    """角色创建模型"""
    pass


class RoleUpdate(BaseModel):
    """角色更新模型"""
    role_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    scope: Optional[RoleScope] = None
    is_active: Optional[bool] = None

    # 系统角色不允许修改编码和系统标识

    @validator('role_name')
    def validate_role_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('角色名称至少2个字符')
        return v


class RoleOut(RoleBase):
    """角色输出模型"""
    id: str = Field(..., description="角色ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'RoleOut':
        """从字典创建对象"""
        return cls(**data)


class RoleQuery(BaseModel):
    """角色查询模型"""
    role_name: Optional[str] = Field(None, description="角色名称模糊查询")
    role_code: Optional[str] = Field(None, description="角色编码")
    scope: Optional[RoleScope] = Field(None, description="角色范围")
    is_system_role: Optional[bool] = Field(None, description="是否系统角色")
    is_active: Optional[bool] = Field(None, description="是否激活")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class RoleWithPermissions(RoleOut):
    """包含权限的角色模型"""
    permissions: List['PermissionOut'] = Field(default_factory=list, description="角色权限列表")