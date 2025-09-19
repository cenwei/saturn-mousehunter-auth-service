"""
认证服务 - 菜单API路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from saturn_mousehunter_shared.log.logger import get_logger
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_menu_permission_service
from api.dependencies.menu_permission import require_menu_permission
from application.services.menu_permission_service import MenuPermissionService
from domain.models.auth_menu import (
    UserMenuResponse, MenuTree, MenuStatsResponse, MenuPermissionCheck
)
from domain.models.auth_user_role import UserType

log = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["菜单权限"])


@router.get("/auth/user-menus", response_model=UserMenuResponse)
async def get_user_menus(
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> UserMenuResponse:
    """
    获取当前用户可访问的菜单

    **权限要求**: 已认证用户

    **返回信息**:
    - user_id: 用户ID
    - user_type: 用户类型
    - permissions: 用户权限列表
    - menus: 可访问菜单树
    - updated_at: 更新时间
    """
    try:
        user_id = current_user["user_id"]
        user_type = UserType(current_user["user_type"])

        log.info(f"Getting menus for user: {user_id} ({user_type.value})")

        result = await menu_service.get_user_accessible_menus(user_id, user_type)

        log.info(f"User {user_id} has access to {len(result.menus)} menus")
        return result

    except Exception as e:
        log.error(f"Failed to get user menus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户菜单失败: {str(e)}"
        )


@router.get("/menus/tree", response_model=List[MenuTree])
async def get_menu_tree(
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> List[MenuTree]:
    """
    获取完整菜单树结构

    **权限要求**: 已认证用户

    **用途**:
    - 管理界面显示所有菜单
    - 权限配置界面
    """
    try:
        # 只有管理员可以查看完整菜单树
        if current_user.get("user_type") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看完整菜单树"
            )

        log.info(f"Getting full menu tree for admin: {current_user['user_id']}")
        return menu_service.get_menu_tree()

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get menu tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单树失败: {str(e)}"
        )


@router.post("/auth/check-menu-permission", response_model=MenuPermissionCheck)
async def check_menu_permission(
    menu_id: str = Query(..., description="菜单ID"),
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuPermissionCheck:
    """
    检查用户是否有指定菜单的访问权限

    **权限要求**: 已认证用户

    **参数**:
    - menu_id: 菜单ID

    **返回信息**:
    - menu_id: 菜单ID
    - permission: 所需权限
    - has_permission: 是否有权限
    """
    try:
        user_id = current_user["user_id"]
        user_type = UserType(current_user["user_type"])

        log.debug(f"Checking menu permission for user {user_id}, menu {menu_id}")

        result = await menu_service.validate_menu_access(user_id, user_type, menu_id)

        log.debug(f"Menu permission check result: {result.has_permission}")
        return result

    except Exception as e:
        log.error(f"Failed to check menu permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查菜单权限失败: {str(e)}"
        )


@router.get("/users/{user_id}/menus", response_model=UserMenuResponse)
async def get_user_menus_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> UserMenuResponse:
    """
    获取指定用户的可访问菜单

    **权限要求**: 管理员用户或查看自己的菜单

    **参数**:
    - user_id: 目标用户ID
    """
    try:
        # 权限检查：只能查看自己的菜单，或管理员可以查看所有用户菜单
        if (current_user["user_id"] != user_id and
            current_user.get("user_type") != "ADMIN"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能查看自己的菜单，或需要管理员权限"
            )

        # 对于管理员查看其他用户菜单，需要确定目标用户类型
        # 这里简化处理，假设是TENANT用户，实际应该查询数据库确定
        target_user_type = UserType.TENANT
        if user_id.startswith("ADMIN_"):
            target_user_type = UserType.ADMIN

        log.info(f"Getting menus for user: {user_id} by admin: {current_user['user_id']}")

        result = await menu_service.get_user_accessible_menus(user_id, target_user_type)
        return result

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get user menus by id: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户菜单失败: {str(e)}"
        )


@router.get("/auth/menu-stats", response_model=MenuStatsResponse)
async def get_menu_stats(
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuStatsResponse:
    """
    获取当前用户的菜单统计信息

    **权限要求**: 已认证用户

    **返回信息**:
    - total_menus: 菜单总数
    - accessible_menus: 可访问菜单数
    - permission_coverage: 权限覆盖率
    - menu_usage: 菜单使用统计
    """
    try:
        user_id = current_user["user_id"]
        user_type = UserType(current_user["user_type"])

        log.info(f"Getting menu stats for user: {user_id}")

        result = await menu_service.get_menu_stats(user_id, user_type)
        return result

    except Exception as e:
        log.error(f"Failed to get menu stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单统计失败: {str(e)}"
        )


# 示例：使用菜单权限装饰器保护的路由
@router.get("/dashboard/data")
@require_menu_permission("menu:dashboard")
async def get_dashboard_data(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取仪表盘数据

    **权限要求**: menu:dashboard
    """
    try:
        log.info(f"Getting dashboard data for user: {current_user['user_id']}")

        # 这里是仪表盘数据的业务逻辑
        return {
            "user_count": 150,
            "active_strategies": 25,
            "risk_alerts": 3,
            "system_health": "good",
            "updated_at": "2024-01-01T12:00:00Z"
        }

    except Exception as e:
        log.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表盘数据失败: {str(e)}"
        )


@router.get("/system/config")
@require_menu_permission("menu:system")
async def get_system_config(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取系统配置

    **权限要求**: menu:system
    """
    try:
        log.info(f"Getting system config for user: {current_user['user_id']}")

        # 系统配置数据
        return {
            "app_name": "Saturn MouseHunter",
            "version": "1.0.0",
            "features": {
                "multi_tenant": True,
                "rbac": True,
                "audit_log": True
            },
            "limits": {
                "max_users": 1000,
                "max_strategies": 100
            }
        }

    except Exception as e:
        log.error(f"Failed to get system config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统配置失败: {str(e)}"
        )