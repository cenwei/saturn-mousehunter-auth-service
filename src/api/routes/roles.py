"""
认证服务 - 角色管理API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from domain.models.auth_role import (
    RoleIn, RoleOut, RoleUpdate, RoleQuery, RoleWithPermissions
)
from application.services.role_service import RoleService
from api.dependencies.auth import get_admin_user
from api.dependencies.services import get_role_service

router = APIRouter(prefix="/admin/roles", tags=["角色管理"])


@router.post("/", response_model=RoleOut)
async def create_role(
    request: Request,
    role_data: RoleIn,
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """创建角色"""
    try:
        return await role_service.create_role(
            role_data=role_data,
            created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/count", response_model=dict)
async def count_roles(
    query_params: RoleQuery = Depends(),
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """获取角色总数"""
    count = await role_service.count_roles(query_params)
    return {"count": count}


@router.get("/system", response_model=List[RoleOut])
async def list_system_roles(
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """获取系统角色列表"""
    return await role_service.list_system_roles()


@router.get("/", response_model=List[RoleOut])
async def list_roles(
    query_params: RoleQuery = Depends(),
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """获取角色列表"""
    return await role_service.list_roles(query_params)


@router.get("/{role_id}", response_model=RoleOut)
async def get_role(
    role_id: str,
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """获取角色详情"""
    role = await role_service.get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role


@router.get("/{role_id}/permissions", response_model=RoleWithPermissions)
async def get_role_with_permissions(
    role_id: str,
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """获取角色及其权限"""
    role = await role_service.get_role_with_permissions(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role


@router.put("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: str,
    update_data: RoleUpdate,
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """更新角色"""
    try:
        role = await role_service.update_role(
            role_id=role_id,
            update_data=update_data,
            updated_by=current_user["user_id"]
        )
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    current_user: dict = Depends(get_admin_user),
    role_service: RoleService = Depends(get_role_service)
):
    """删除角色"""
    try:
        success = await role_service.delete_role(
            role_id=role_id,
            deleted_by=current_user["user_id"]
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        return {"message": "角色删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )