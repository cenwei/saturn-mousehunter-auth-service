"""
认证服务 - 权限Domain Model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class PermissionBase(BaseModel):
    """权限基础模型"""
    permission_name: str = Field(..., min_length=2, max_length=100, description="权限名称")
    permission_code: str = Field(..., min_length=2, max_length=100, description="权限编码")
    resource: str = Field(..., min_length=2, max_length=100, description="资源名称")
    action: str = Field(..., min_length=2, max_length=50, description="操作类型")
    description: Optional[str] = Field(None, description="权限描述")
    is_system_permission: bool = Field(False, description="是否系统权限")

    @validator('permission_code')
    def validate_permission_code(cls, v):
        # 权限编码格式：resource:action
        if ':' not in v:
            raise ValueError('权限编码格式应为 resource:action')
        parts = v.split(':')
        if len(parts) != 2:
            raise ValueError('权限编码格式应为 resource:action')
        resource, action = parts
        if not resource or not action:
            raise ValueError('资源名和操作不能为空')
        return v.lower()

    @validator('action')
    def validate_action(cls, v):
        valid_actions = {'create', 'read', 'update', 'delete', 'write', 'execute', 'manage'}
        if v.lower() not in valid_actions:
            raise ValueError(f'操作类型必须是以下之一: {", ".join(valid_actions)}')
        return v.lower()

    @validator('resource')
    def validate_resource(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('资源名只能包含字母、数字、下划线和连字符')
        return v.lower()


class PermissionIn(PermissionBase):
    """权限创建模型"""
    pass


class PermissionUpdate(BaseModel):
    """权限更新模型"""
    permission_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None

    # 系统权限不允许修改编码、资源、操作等核心信息

    @validator('permission_name')
    def validate_permission_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('权限名称至少2个字符')
        return v


class PermissionOut(PermissionBase):
    """权限输出模型"""
    id: str = Field(..., description="权限ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'PermissionOut':
        """从字典创建对象"""
        return cls(**data)


class PermissionQuery(BaseModel):
    """权限查询模型"""
    permission_name: Optional[str] = Field(None, description="权限名称模糊查询")
    resource: Optional[str] = Field(None, description="资源名称")
    action: Optional[str] = Field(None, description="操作类型")
    is_system_permission: Optional[bool] = Field(None, description="是否系统权限")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")