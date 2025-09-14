"""
认证服务 - 审计日志Domain Model
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .auth_user_role import UserType


class AuditLogBase(BaseModel):
    """审计日志基础模型"""
    user_id: Optional[str] = Field(None, description="用户ID")
    user_type: Optional[UserType] = Field(None, description="用户类型")
    action: str = Field(..., max_length=100, description="操作类型")
    resource: Optional[str] = Field(None, max_length=100, description="资源类型")
    resource_id: Optional[str] = Field(None, max_length=50, description="资源ID")
    details: Dict[str, Any] = Field(default_factory=dict, description="操作详情")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    success: bool = Field(True, description="操作是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")


class AuditLogIn(AuditLogBase):
    """审计日志创建模型"""
    pass


class AuditLogOut(AuditLogBase):
    """审计日志输出模型"""
    id: str = Field(..., description="日志ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict) -> 'AuditLogOut':
        """从字典创建对象"""
        return cls(**data)


class AuditLogQuery(BaseModel):
    """审计日志查询模型"""
    user_id: Optional[str] = Field(None, description="用户ID")
    user_type: Optional[UserType] = Field(None, description="用户类型")
    action: Optional[str] = Field(None, description="操作类型")
    resource: Optional[str] = Field(None, description="资源类型")
    success: Optional[bool] = Field(None, description="是否成功")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    ip_address: Optional[str] = Field(None, description="IP地址")
    limit: Optional[int] = Field(20, ge=1, le=100, description="每页数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")


class AuditLogStats(BaseModel):
    """审计日志统计模型"""
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    today_count: int = Field(..., description="今日数量")
    this_week_count: int = Field(..., description="本周数量")
    this_month_count: int = Field(..., description="本月数量")