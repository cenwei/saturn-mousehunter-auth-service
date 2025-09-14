"""
认证服务 - 角色权限关系Domain Model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RolePermissionBase(BaseModel):
    """角色权限关系基础模型"""
    role_id: str = Field(..., description="角色ID")
    permission_id: str = Field(..., description="权限ID")


class RolePermissionIn(RolePermissionBase):
    """角色权限关系创建模型"""
    pass


class RolePermissionOut(RolePermissionBase):
    """角色权限关系输出模型"""
    id: str = Field(..., description="关系ID")
    created_at: datetime = Field(..., description="创建时间")
    role_name: Optional[str] = Field(None, description="角色名称")
    role_code: Optional[str] = Field(None, description="角色编码")
    permission_name: Optional[str] = Field(None, description="权限名称")
    permission_code: Optional[str] = Field(None, description="权限编码")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'RolePermissionOut':
        """从字典创建对象"""
        return cls(**data)


class RolePermissionQuery(BaseModel):
    """角色权限关系查询模型"""
    role_id: Optional[str] = Field(None, description="角色ID")
    permission_id: Optional[str] = Field(None, description="权限ID")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class RolePermissionAssignment(BaseModel):
    """角色权限分配模型"""
    role_id: str = Field(..., description="角色ID")
    permission_ids: list[str] = Field(..., description="权限ID列表")