"""
认证服务 - 菜单管理API路由
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from saturn_mousehunter_shared.log.logger import get_logger
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_menu_permission_service
from application.services.menu_permission_service import MenuPermissionService
from domain.models.auth_menu import (
    MenuTree, MenuType
)

log = get_logger(__name__)

router = APIRouter(prefix="/api/v1/menus", tags=["菜单管理"])


class MenuCreateRequest(BaseModel):
    """创建菜单请求"""
    id: str = Field(..., description="菜单ID")
    name: str = Field(..., description="菜单名称")
    title: str = Field(..., description="菜单标题")
    title_en: Optional[str] = Field(None, description="英文标题")
    path: Optional[str] = Field(None, description="菜单路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="菜单图标")
    emoji: Optional[str] = Field(None, description="表情符号图标")
    parent_id: Optional[str] = Field(None, description="父菜单ID")
    permission: Optional[str] = Field(None, description="所需权限")
    menu_type: MenuType = Field(MenuType.MENU, description="菜单类型")
    sort_order: int = Field(0, description="排序顺序")
    is_hidden: bool = Field(False, description="是否隐藏")
    is_external: bool = Field(False, description="是否外部链接")
    status: str = Field("active", description="菜单状态")
    meta: Optional[Dict[str, Any]] = Field(None, description="菜单元数据")


class MenuUpdateRequest(BaseModel):
    """更新菜单请求"""
    name: Optional[str] = Field(None, description="菜单名称")
    title: Optional[str] = Field(None, description="菜单标题")
    title_en: Optional[str] = Field(None, description="英文标题")
    path: Optional[str] = Field(None, description="菜单路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="菜单图标")
    emoji: Optional[str] = Field(None, description="表情符号图标")
    parent_id: Optional[str] = Field(None, description="父菜单ID")
    permission: Optional[str] = Field(None, description="所需权限")
    menu_type: Optional[MenuType] = Field(None, description="菜单类型")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    is_hidden: Optional[bool] = Field(None, description="是否隐藏")
    is_external: Optional[bool] = Field(None, description="是否外部链接")
    status: Optional[str] = Field(None, description="菜单状态")
    meta: Optional[Dict[str, Any]] = Field(None, description="菜单元数据")


class MenuBatchImportRequest(BaseModel):
    """批量导入菜单请求"""
    menus: List[MenuCreateRequest] = Field(..., description="菜单列表")
    clear_existing: bool = Field(False, description="是否清除现有菜单")


class MenuResponse(BaseModel):
    """菜单响应"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


@router.get("", response_model=List[MenuTree])
async def get_menus(
    current_user: dict = Depends(get_current_user),
    parent_id: Optional[str] = Query(None, description="父菜单ID，空值获取根菜单"),
    status: Optional[str] = Query(None, description="菜单状态过滤"),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> List[MenuTree]:
    """
    获取菜单列表

    **权限要求**: 已认证用户

    **参数**:
    - parent_id: 父菜单ID，为空时获取根菜单
    - status: 菜单状态过滤，可选值：active, inactive
    """
    try:
        # 管理员可以查看所有菜单，普通用户只能查看有权限的菜单
        if current_user.get("user_type") == "ADMIN":
            menus = menu_service.get_menu_tree()
        else:
            # 普通用户获取可访问菜单
            from domain.models.auth_user_role import UserType
            user_response = await menu_service.get_user_accessible_menus(
                current_user["user_id"],
                UserType(current_user["user_type"])
            )
            menus = user_response.menus

        # 应用过滤条件
        if parent_id is not None:
            # 查找指定父菜单的子菜单
            filtered_menus = []
            for menu in menus:
                if menu.id == parent_id and menu.children:
                    filtered_menus = menu.children
                    break
            menus = filtered_menus

        if status:
            menus = [menu for menu in menus if getattr(menu, 'status', 'active') == status]

        log.info(f"Retrieved {len(menus)} menus for user {current_user['user_id']}")
        return menus

    except Exception as e:
        log.error(f"Failed to get menus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单列表失败: {str(e)}"
        )


@router.post("", response_model=MenuResponse)
async def create_menu(
    request: MenuCreateRequest,
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuResponse:
    """
    创建新菜单

    **权限要求**: 管理员权限
    """
    try:
        # 检查管理员权限
        if current_user.get("user_type") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以创建菜单"
            )

        # TODO: 这里应该调用具体的菜单创建服务
        # 现在返回模拟响应
        log.info(f"Admin {current_user['user_id']} created menu: {request.id}")

        return MenuResponse(
            success=True,
            message=f"菜单 '{request.title}' 创建成功",
            data={"menu_id": request.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to create menu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建菜单失败: {str(e)}"
        )


@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: str,
    request: MenuUpdateRequest,
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuResponse:
    """
    更新菜单

    **权限要求**: 管理员权限
    """
    try:
        # 检查管理员权限
        if current_user.get("user_type") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以更新菜单"
            )

        # 检查菜单是否存在
        existing_menu = menu_service._menu_config.get(menu_id)
        if not existing_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"菜单 '{menu_id}' 不存在"
            )

        # TODO: 这里应该调用具体的菜单更新服务
        # 现在返回模拟响应
        log.info(f"Admin {current_user['user_id']} updated menu: {menu_id}")

        return MenuResponse(
            success=True,
            message=f"菜单 '{menu_id}' 更新成功",
            data={"menu_id": menu_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to update menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新菜单失败: {str(e)}"
        )


@router.delete("/{menu_id}", response_model=MenuResponse)
async def delete_menu(
    menu_id: str,
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuResponse:
    """
    删除菜单

    **权限要求**: 管理员权限
    """
    try:
        # 检查管理员权限
        if current_user.get("user_type") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以删除菜单"
            )

        # 检查菜单是否存在
        existing_menu = menu_service._menu_config.get(menu_id)
        if not existing_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"菜单 '{menu_id}' 不存在"
            )

        # TODO: 这里应该调用具体的菜单删除服务
        # 现在返回模拟响应
        log.info(f"Admin {current_user['user_id']} deleted menu: {menu_id}")

        return MenuResponse(
            success=True,
            message=f"菜单 '{menu_id}' 删除成功",
            data={"menu_id": menu_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to delete menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除菜单失败: {str(e)}"
        )


@router.get("/tree", response_model=List[MenuTree])
async def get_menu_tree(
    current_user: dict = Depends(get_current_user),
    include_hidden: bool = Query(False, description="是否包含隐藏菜单"),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> List[MenuTree]:
    """
    获取完整菜单树结构

    **权限要求**: 管理员权限（查看完整树）或已认证用户（查看有权限的树）
    """
    try:
        if current_user.get("user_type") == "ADMIN":
            # 管理员获取完整菜单树
            menus = menu_service.get_menu_tree()
            log.info(f"Admin {current_user['user_id']} retrieved full menu tree: {len(menus)} menus")
        else:
            # 普通用户获取有权限的菜单树
            from domain.models.auth_user_role import UserType
            user_response = await menu_service.get_user_accessible_menus(
                current_user["user_id"],
                UserType(current_user["user_type"])
            )
            menus = user_response.menus
            log.info(f"User {current_user['user_id']} retrieved accessible menu tree: {len(menus)} menus")

        # 过滤隐藏菜单
        if not include_hidden:
            def filter_hidden(menu_list: List[MenuTree]) -> List[MenuTree]:
                filtered = []
                for menu in menu_list:
                    if not menu.is_hidden:
                        menu_copy = menu.model_copy()
                        menu_copy.children = filter_hidden(menu.children)
                        filtered.append(menu_copy)
                return filtered

            menus = filter_hidden(menus)

        return menus

    except Exception as e:
        log.error(f"Failed to get menu tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单树失败: {str(e)}"
        )


@router.post("/batch-import", response_model=MenuResponse)
async def batch_import_menus(
    request: MenuBatchImportRequest,
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuResponse:
    """
    批量导入菜单

    **权限要求**: 管理员权限
    """
    try:
        # 检查管理员权限
        if current_user.get("user_type") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以批量导入菜单"
            )

        # TODO: 这里应该调用具体的批量导入服务
        # 现在返回模拟响应
        imported_count = len(request.menus)

        log.info(f"Admin {current_user['user_id']} batch imported {imported_count} menus")

        return MenuResponse(
            success=True,
            message=f"成功导入 {imported_count} 个菜单",
            data={
                "imported_count": imported_count,
                "clear_existing": request.clear_existing
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to batch import menus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入菜单失败: {str(e)}"
        )


@router.get("/{menu_id}", response_model=MenuTree)
async def get_menu_by_id(
    menu_id: str,
    current_user: dict = Depends(get_current_user),
    menu_service: MenuPermissionService = Depends(get_menu_permission_service)
) -> MenuTree:
    """
    根据ID获取菜单详情

    **权限要求**: 已认证用户
    """
    try:
        # 获取菜单配置
        menu_config = menu_service._menu_config.get(menu_id)
        if not menu_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"菜单 '{menu_id}' 不存在"
            )

        # 检查用户是否有权限访问此菜单
        if current_user.get("user_type") != "ADMIN" and menu_config.permission:
            from domain.models.auth_user_role import UserType
            permission_check = await menu_service.validate_menu_access(
                current_user["user_id"],
                UserType(current_user["user_type"]),
                menu_id
            )

            if not permission_check.has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有权限访问菜单 '{menu_id}'"
                )

        # 转换为MenuTree格式
        menu_tree = MenuTree(
            id=menu_config.id,
            name=menu_config.name,
            title=menu_config.title,
            title_en=getattr(menu_config, 'title_en', None),
            path=menu_config.path,
            icon=menu_config.icon,
            emoji=getattr(menu_config, 'emoji', None),
            permission=menu_config.permission,
            menu_type=menu_config.menu_type,
            sort_order=menu_config.sort_order,
            is_hidden=menu_config.is_hidden,
            status=getattr(menu_config, 'status', 'active'),
            meta=menu_config.meta,
            children=[]
        )

        log.info(f"User {current_user['user_id']} retrieved menu details: {menu_id}")
        return menu_tree

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取菜单详情失败: {str(e)}"
        )