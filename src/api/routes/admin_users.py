"""
认证服务 - 管理员用户API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from domain.models.auth_admin_user import (
    AdminUserIn, AdminUserOut, AdminUserUpdate, AdminUserQuery,
    AdminUserLogin, AdminUserResponse
)
from application.services import AdminUserService
from api.dependencies.auth import get_admin_user, require_permissions

router = APIRouter(prefix="/admin/users", tags=["管理员用户"])


@router.post("/login", response_model=AdminUserResponse)
async def login(
    request: Request,
    login_data: AdminUserLogin,
    admin_service: AdminUserService = Depends()
):
    """管理员用户登录"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")

    response = await admin_service.authenticate(
        login_data=login_data,
        ip_address=client_ip,
        user_agent=user_agent
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    return response


@router.post("/", response_model=AdminUserOut)
async def create_admin_user(
    user_data: AdminUserIn,
    current_user: dict = Depends(require_permissions(["user:write"])),
    admin_service: AdminUserService = Depends()
):
    """创建管理员用户"""
    try:
        return await admin_service.create_admin_user(
            user_data=user_data,
            created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=dict)
async def get_current_admin_profile(
    current_user: dict = Depends(get_admin_user),
    admin_service: AdminUserService = Depends()
):
    """获取当前管理员用户资料"""
    profile = await admin_service.get_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到"
        )
    return profile


@router.get("/{user_id}", response_model=AdminUserOut)
async def get_admin_user(
    user_id: str,
    current_user: dict = Depends(require_permissions(["user:read"])),
    admin_service: AdminUserService = Depends()
):
    """获取管理员用户详情"""
    user = await admin_service.get_admin_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/{user_id}", response_model=AdminUserOut)
async def update_admin_user(
    user_id: str,
    update_data: AdminUserUpdate,
    current_user: dict = Depends(require_permissions(["user:write"])),
    admin_service: AdminUserService = Depends()
):
    """更新管理员用户"""
    try:
        user = await admin_service.update_admin_user(
            user_id=user_id,
            update_data=update_data,
            updated_by=current_user["user_id"]
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_admin_user(
    user_id: str,
    current_user: dict = Depends(require_permissions(["user:write"])),
    admin_service: AdminUserService = Depends()
):
    """删除管理员用户"""
    try:
        success = await admin_service.delete_admin_user(
            user_id=user_id,
            deleted_by=current_user["user_id"]
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return {"message": "用户删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[AdminUserOut])
async def list_admin_users(
    query_params: AdminUserQuery = Depends(),
    current_user: dict = Depends(require_permissions(["user:read"])),
    admin_service: AdminUserService = Depends()
):
    """获取管理员用户列表"""
    return await admin_service.list_admin_users(query_params)


@router.post("/{user_id}/change-password")
async def change_password(
    user_id: str,
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_admin_user),
    admin_service: AdminUserService = Depends()
):
    """修改密码"""
    # 只能修改自己的密码，或者有用户管理权限
    if user_id != current_user["user_id"] and "user:write" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的密码或需要用户管理权限"
        )

    try:
        success = await admin_service.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password,
            changed_by=current_user["user_id"]
        )
        if not success:
            return {"message": "密码修改失败"}
        return {"message": "密码修改成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: str,
    new_password: str = None,
    current_user: dict = Depends(require_permissions(["user:write"])),
    admin_service: AdminUserService = Depends()
):
    """重置密码（管理员操作）"""
    try:
        generated_password = await admin_service.reset_password(
            user_id=user_id,
            new_password=new_password,
            reset_by=current_user["user_id"]
        )
        return {
            "message": "密码重置成功",
            "new_password": generated_password if not new_password else "已设置为指定密码"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )