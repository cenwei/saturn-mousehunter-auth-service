"""
认证服务 - 租户用户API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from saturn_mousehunter_shared.log.logger import get_logger
from domain.models.auth_tenant_user import (
    TenantUserIn, TenantUserOut, TenantUserUpdate, TenantUserQuery,
    TenantUserLogin, TenantUserResponse
)
from application.services import TenantUserService
from api.dependencies.auth import get_tenant_user, require_permissions
from api.dependencies.services import get_tenant_user_service

log = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["租户用户"])


@router.post("/login", response_model=TenantUserResponse)
async def login(
    request: Request,
    login_data: TenantUserLogin,
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """租户用户登录"""
    client_ip = str(request.client.host)
    user_agent = request.headers.get("user-agent")

    response = await tenant_service.authenticate(
        login_data=login_data,
        ip_address=client_ip,
        user_agent=user_agent
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="租户ID、用户名或密码错误"
        )

    return response


@router.post("/", response_model=TenantUserOut)
async def create_tenant_user(
    user_data: TenantUserIn,
    current_user: dict = Depends(require_permissions(["user:write"])),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """创建租户用户"""
    try:
        return await tenant_service.create_tenant_user(
            user_data=user_data,
            created_by=current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=dict)
async def get_current_tenant_profile(
    current_user: dict = Depends(get_tenant_user),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """获取当前租户用户资料"""
    profile = await tenant_service.get_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到"
        )
    return profile


@router.get("/{user_id}", response_model=TenantUserOut)
async def get_tenant_user(
    user_id: str,
    current_user: dict = Depends(require_permissions(["user:read"])),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """获取租户用户详情"""
    user = await tenant_service.get_tenant_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/{user_id}", response_model=TenantUserOut)
async def update_tenant_user(
    user_id: str,
    update_data: TenantUserUpdate,
    current_user: dict = Depends(require_permissions(["user:write"])),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """更新租户用户"""
    try:
        # 添加类型检查以确保current_user是字典
        if not isinstance(current_user, dict):
            log.error(f"current_user is not a dict, got: {type(current_user)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="认证信息格式错误"
            )

        if "user_id" not in current_user:
            log.error(f"current_user missing user_id key, keys: {current_user.keys()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="认证信息不完整"
            )

        user = await tenant_service.update_tenant_user(
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
    except Exception as e:
        log.error(f"Update tenant user failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败，请稍后重试"
        )


@router.delete("/{user_id}")
async def delete_tenant_user(
    user_id: str,
    current_user: dict = Depends(require_permissions(["user:write"])),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """删除租户用户"""
    try:
        success = await tenant_service.delete_tenant_user(
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


@router.get("/", response_model=List[TenantUserOut])
async def list_tenant_users(
    query_params: TenantUserQuery = Depends(),
    current_user: dict = Depends(require_permissions(["user:read"])),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """获取租户用户列表"""
    return await tenant_service.list_tenant_users(query_params)


@router.get("/tenant/{tenant_id}", response_model=List[TenantUserOut])
async def list_users_by_tenant(
    tenant_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(require_permissions(["user:read"])),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """根据租户ID获取用户列表"""
    return await tenant_service.list_by_tenant(tenant_id, limit, offset)


@router.post("/{user_id}/change-password")
async def change_password(
    user_id: str,
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_tenant_user),
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """修改密码"""
    # 只能修改自己的密码，或者有用户管理权限
    if user_id != current_user["user_id"] and "user:write" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的密码或需要用户管理权限"
        )

    try:
        success = await tenant_service.change_password(
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
    tenant_service: TenantUserService = Depends(get_tenant_user_service)
):
    """重置密码（管理员操作）"""
    try:
        generated_password = await tenant_service.reset_password(
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