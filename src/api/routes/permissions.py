"""
认证服务 - 权限管理API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from domain.models.auth_permission import (
    PermissionIn, PermissionOut, PermissionUpdate, PermissionQuery
)
from application.services.permission_service import PermissionService
from api.dependencies.auth import get_admin_user
from api.dependencies.services import get_permission_service

router = APIRouter(prefix="/admin/permissions", tags=["权限管理"])


@router.post("/", response_model=PermissionOut)
async def create_permission(
    request: Request,
    permission_data: PermissionIn,
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """创建权限"""
    try:
        return await permission_service.create_permission(
            permission_data=permission_data,
            created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/count", response_model=dict)
async def count_permissions(
    query_params: PermissionQuery = Depends(),
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """获取权限总数"""
    count = await permission_service.count_permissions(query_params)
    return {"count": count}


@router.get("/system", response_model=List[PermissionOut])
async def list_system_permissions(
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """获取系统权限列表"""
    return await permission_service.list_system_permissions()


@router.get("/by-resource/{resource}", response_model=List[PermissionOut])
async def list_permissions_by_resource(
    resource: str,
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """根据资源获取权限列表"""
    return await permission_service.list_permissions_by_resource(resource)


@router.get("/check/{permission_code}", response_model=dict)
async def check_permission_exists(
    permission_code: str,
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """检查权限是否存在"""
    exists = await permission_service.check_permission_exists(permission_code)
    return {"exists": exists, "permission_code": permission_code}


@router.get("/", response_model=List[PermissionOut])
async def list_permissions(
    query_params: PermissionQuery = Depends(),
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """获取权限列表"""
    return await permission_service.list_permissions(query_params)


@router.get("/{permission_id}", response_model=PermissionOut)
async def get_permission(
    permission_id: str,
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """获取权限详情"""
    permission = await permission_service.get_permission(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return permission


@router.put("/{permission_id}", response_model=PermissionOut)
async def update_permission(
    permission_id: str,
    update_data: PermissionUpdate,
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """更新权限"""
    try:
        permission = await permission_service.update_permission(
            permission_id=permission_id,
            update_data=update_data,
            updated_by=current_user["user_id"]
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在"
            )
        return permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: str,
    current_user: dict = Depends(get_admin_user),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """删除权限"""
    try:
        success = await permission_service.delete_permission(
            permission_id=permission_id,
            deleted_by=current_user["user_id"]
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在"
            )
        return {"message": "权限删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )