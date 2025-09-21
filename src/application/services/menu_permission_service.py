"""
认证服务 - 菜单权限服务
"""
from typing import List, Dict, Optional, Set, Any
from datetime import datetime

from saturn_mousehunter_shared.aop.decorators import measure
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.repositories import UserRoleRepo
from infrastructure.repositories.menu_repo import MenuRepo
from domain.models.auth_menu import (
    MenuConfig, MenuTree, UserMenuResponse, MenuStatsResponse,
    MenuPermissionCheck, DEFAULT_MENU_CONFIG, SATURN_MHC_MENU_CONFIG, MENU_PERMISSIONS, MenuType
)
from domain.models.auth_user_role import UserType

log = get_logger(__name__)


class MenuPermissionService:
    """菜单权限服务"""

    def __init__(self, user_role_repo: UserRoleRepo, menu_repo: Optional[MenuRepo] = None, use_saturn_mhc_menus: bool = True):
        self.user_role_repo = user_role_repo
        self.menu_repo = menu_repo

        # 支持切换菜单配置：默认使用Saturn MHC完整菜单，可回退到原有菜单
        menu_config = SATURN_MHC_MENU_CONFIG if use_saturn_mhc_menus else DEFAULT_MENU_CONFIG
        self._menu_config = self._build_menu_dict(menu_config)
        self._menu_permissions = MENU_PERMISSIONS
        self._use_saturn_mhc = use_saturn_mhc_menus

        log.info(f"MenuPermissionService initialized with {'Saturn MHC' if use_saturn_mhc_menus else 'Default'} menu config")
        log.info(f"Total menus loaded: {len(self._menu_config)}")
        log.info(f"Total permissions configured: {len(self._menu_permissions)}")
        log.info(f"Database menu storage: {'enabled' if menu_repo else 'disabled'}")

    async def initialize_menu_storage(self):
        """初始化菜单存储"""
        if self.menu_repo:
            try:
                await self.menu_repo.initialize_tables()
                log.info("Menu storage tables initialized successfully")
            except Exception as e:
                log.error(f"Failed to initialize menu storage: {e}")
                raise

    def _build_menu_dict(self, menus: List[MenuConfig]) -> Dict[str, MenuConfig]:
        """构建菜单字典"""
        menu_dict = {}

        def add_menu(menu: MenuConfig):
            menu_dict[menu.id] = menu
            if menu.children:
                for child in menu.children:
                    add_menu(child)

        for menu in menus:
            add_menu(menu)

        return menu_dict

    @measure("service_menu_filter_seconds")
    async def filter_menus_by_permissions(
        self,
        menus: List[MenuConfig],
        user_permissions: Set[str]
    ) -> List[MenuTree]:
        """根据用户权限过滤菜单"""
        filtered_menus = []

        for menu in menus:
            # 创建菜单树节点
            menu_tree = MenuTree(
                id=menu.id,
                name=menu.name,
                title=menu.title,
                title_en=getattr(menu, 'title_en', None),
                path=menu.path,
                icon=menu.icon,
                emoji=getattr(menu, 'emoji', None),
                permission=menu.permission,
                menu_type=menu.menu_type,
                sort_order=menu.sort_order,
                is_hidden=menu.is_hidden,
                status=getattr(menu, 'status', 'active'),
                meta=menu.meta,
                children=[]
            )

            # 处理子菜单
            if menu.children:
                filtered_children = await self.filter_menus_by_permissions(
                    menu.children,
                    user_permissions
                )
                menu_tree.children = filtered_children

                # 如果有子菜单权限，即使父菜单没有直接权限也要显示
                # 或者父菜单有权限也要显示
                if filtered_children or not menu.permission or menu.permission in user_permissions:
                    filtered_menus.append(menu_tree)
            else:
                # 叶子菜单：检查权限
                if not menu.permission or menu.permission in user_permissions:
                    filtered_menus.append(menu_tree)

        # 按排序顺序排序
        filtered_menus.sort(key=lambda x: x.sort_order)
        return filtered_menus

    @measure("service_get_user_menus_seconds")
    async def get_user_accessible_menus(
        self,
        user_id: str,
        user_type: UserType
    ) -> UserMenuResponse:
        """获取用户可访问的菜单"""
        try:
            # 获取用户权限
            if self._use_saturn_mhc:
                # 使用新的权限映射逻辑
                user_permissions = self._get_user_permissions_by_type(user_type)
                log.info(f"User {user_id} ({user_type.value}) permissions from mapping: {user_permissions}")
            else:
                # 使用原有的数据库权限查询
                user_perms = await self.user_role_repo.get_user_permissions(user_id, user_type)
                user_permissions = set(user_perms.permissions)
                log.info(f"User {user_id} permissions from DB: {user_permissions}")

            # 获取当前菜单配置
            menu_config = SATURN_MHC_MENU_CONFIG if self._use_saturn_mhc else DEFAULT_MENU_CONFIG

            # 过滤菜单
            accessible_menus = await self.filter_menus_by_permissions(
                menu_config,
                user_permissions
            )

            return UserMenuResponse(
                user_id=user_id,
                user_type=user_type.value,
                permissions=list(user_permissions),
                menus=accessible_menus,
                updated_at=datetime.now()
            )

        except Exception as e:
            log.error(f"Failed to get user menus for {user_id}: {str(e)}")
            # 返回最基础的菜单
            return UserMenuResponse(
                user_id=user_id,
                user_type=user_type.value,
                permissions=[],
                menus=[],
                updated_at=datetime.now()
            )

    def _get_user_permissions_by_type(self, user_type: UserType) -> Set[str]:
        """根据用户类型获取权限"""
        user_permissions = set()

        for permission, allowed_types in self._menu_permissions.items():
            if user_type.value in allowed_types:
                user_permissions.add(permission)

        log.debug(f"User type {user_type.value} has {len(user_permissions)} permissions")
        return user_permissions

    @measure("service_validate_menu_access_seconds")
    async def validate_menu_access(
        self,
        user_id: str,
        user_type: UserType,
        menu_id: str
    ) -> MenuPermissionCheck:
        """验证用户是否有菜单访问权限"""
        try:
            # 获取菜单配置
            menu = self._menu_config.get(menu_id)
            if not menu:
                return MenuPermissionCheck(
                    menu_id=menu_id,
                    permission="",
                    has_permission=False
                )

            # 如果菜单不需要权限，直接允许访问
            if not menu.permission:
                return MenuPermissionCheck(
                    menu_id=menu_id,
                    permission="",
                    has_permission=True
                )

            # 获取用户权限
            if self._use_saturn_mhc:
                # 使用权限映射逻辑
                user_permissions = self._get_user_permissions_by_type(user_type)
                has_permission = menu.permission in user_permissions
            else:
                # 使用原有数据库权限查询
                user_perms = await self.user_role_repo.get_user_permissions(user_id, user_type)
                has_permission = menu.permission in user_perms.permissions

            return MenuPermissionCheck(
                menu_id=menu_id,
                permission=menu.permission,
                has_permission=has_permission
            )

        except Exception as e:
            log.error(f"Failed to validate menu access for user {user_id}, menu {menu_id}: {str(e)}")
            return MenuPermissionCheck(
                menu_id=menu_id,
                permission="",
                has_permission=False
            )

    @measure("service_get_menu_stats_seconds")
    async def get_menu_stats(
        self,
        user_id: str,
        user_type: UserType
    ) -> MenuStatsResponse:
        """获取菜单统计信息"""
        try:
            # 获取用户权限
            if self._use_saturn_mhc:
                user_permissions = self._get_user_permissions_by_type(user_type)
            else:
                user_perms = await self.user_role_repo.get_user_permissions(user_id, user_type)
                user_permissions = set(user_perms.permissions)

            # 计算总菜单数（包括子菜单）
            total_menus = len(self._menu_config)

            # 计算可访问菜单数
            accessible_count = 0
            menu_usage = {}

            for menu_id, menu in self._menu_config.items():
                if not menu.permission or menu.permission in user_permissions:
                    accessible_count += 1
                    menu_usage[menu_id] = 1
                else:
                    menu_usage[menu_id] = 0

            # 计算权限覆盖率
            coverage = (accessible_count / total_menus * 100) if total_menus > 0 else 0

            return MenuStatsResponse(
                total_menus=total_menus,
                accessible_menus=accessible_count,
                permission_coverage=round(coverage, 2),
                menu_usage=menu_usage
            )

        except Exception as e:
            log.error(f"Failed to get menu stats for user {user_id}: {str(e)}")
            return MenuStatsResponse(
                total_menus=0,
                accessible_menus=0,
                permission_coverage=0.0,
                menu_usage={}
            )

    def get_menu_by_path(self, path: str) -> Optional[MenuConfig]:
        """根据路径获取菜单配置"""
        for menu in self._menu_config.values():
            if menu.path == path:
                return menu
        return None

    def get_all_menu_permissions(self) -> Set[str]:
        """获取所有菜单权限"""
        permissions = set()
        for menu in self._menu_config.values():
            if menu.permission:
                permissions.add(menu.permission)
        return permissions

    def get_menu_tree(self) -> List[MenuTree]:
        """获取完整菜单树（不过滤权限）"""
        def build_tree(menus: List[MenuConfig]) -> List[MenuTree]:
            tree = []
            for menu in menus:
                menu_tree = MenuTree(
                    id=menu.id,
                    name=menu.name,
                    title=menu.title,
                    title_en=getattr(menu, 'title_en', None),
                    path=menu.path,
                    icon=menu.icon,
                    emoji=getattr(menu, 'emoji', None),
                    permission=menu.permission,
                    menu_type=menu.menu_type,
                    sort_order=menu.sort_order,
                    is_hidden=menu.is_hidden,
                    status=getattr(menu, 'status', 'active'),
                    meta=menu.meta,
                    children=build_tree(menu.children) if menu.children else []
                )
                tree.append(menu_tree)
            return sorted(tree, key=lambda x: x.sort_order)

        # 使用当前配置的菜单
        menu_config = SATURN_MHC_MENU_CONFIG if self._use_saturn_mhc else DEFAULT_MENU_CONFIG
        return build_tree(menu_config)

    # ======================== 菜单数据库管理方法 ========================

    @measure("service_create_menu_seconds")
    async def create_menu(self, menu_request: 'MenuCreateRequest', created_by: str) -> str:
        """创建新菜单"""
        if not self.menu_repo:
            raise RuntimeError("Menu repository not available")

        # 检查菜单ID是否已存在
        existing_menu = await self.menu_repo.get_menu_by_id(menu_request.id)
        if existing_menu:
            raise ValueError(f"Menu with ID '{menu_request.id}' already exists")

        # 如果有父菜单，检查父菜单是否存在
        if menu_request.parent_id:
            parent_menu = await self.menu_repo.get_menu_by_id(menu_request.parent_id)
            if not parent_menu:
                raise ValueError(f"Parent menu '{menu_request.parent_id}' does not exist")

        # 转换为MenuConfig
        menu_config = MenuConfig(
            id=menu_request.id,
            name=menu_request.name,
            title=menu_request.title,
            title_en=menu_request.title_en,
            path=menu_request.path,
            component=menu_request.component,
            icon=menu_request.icon,
            emoji=menu_request.emoji,
            parent_id=menu_request.parent_id,
            permission=menu_request.permission,
            menu_type=menu_request.menu_type,
            sort_order=menu_request.sort_order,
            is_hidden=menu_request.is_hidden,
            is_external=menu_request.is_external,
            status=menu_request.status,
            meta=menu_request.meta,
            children=None
        )

        # 创建菜单
        menu_id = await self.menu_repo.create_menu(menu_config, created_by)

        # 更新内存缓存
        self._menu_config[menu_id] = menu_config

        log.info(f"Menu created successfully: {menu_id} by {created_by}")
        return menu_id

    @measure("service_update_menu_seconds")
    async def update_menu(self, menu_id: str, update_data: Dict[str, Any], updated_by: str) -> bool:
        """更新菜单"""
        if not self.menu_repo:
            raise RuntimeError("Menu repository not available")

        # 检查菜单是否存在
        existing_menu = await self.menu_repo.get_menu_by_id(menu_id)
        if not existing_menu:
            raise ValueError(f"Menu '{menu_id}' does not exist")

        # 如果更新父菜单，检查父菜单是否存在
        if 'parent_id' in update_data and update_data['parent_id']:
            parent_menu = await self.menu_repo.get_menu_by_id(update_data['parent_id'])
            if not parent_menu:
                raise ValueError(f"Parent menu '{update_data['parent_id']}' does not exist")

        # 处理menu_type枚举
        if 'menu_type' in update_data and isinstance(update_data['menu_type'], MenuType):
            update_data['menu_type'] = update_data['menu_type'].value

        # 更新菜单
        success = await self.menu_repo.update_menu(menu_id, update_data, updated_by)

        if success:
            # 重新加载菜单配置到内存
            updated_menu = await self.menu_repo.get_menu_by_id(menu_id)
            if updated_menu:
                self._menu_config[menu_id] = updated_menu

            log.info(f"Menu updated successfully: {menu_id} by {updated_by}")

        return success

    @measure("service_delete_menu_seconds")
    async def delete_menu(self, menu_id: str, deleted_by: str) -> bool:
        """删除菜单"""
        if not self.menu_repo:
            raise RuntimeError("Menu repository not available")

        # 检查菜单是否存在
        existing_menu = await self.menu_repo.get_menu_by_id(menu_id)
        if not existing_menu:
            raise ValueError(f"Menu '{menu_id}' does not exist")

        # 删除菜单
        success = await self.menu_repo.delete_menu(menu_id, deleted_by)

        if success:
            # 从内存缓存中移除
            if menu_id in self._menu_config:
                del self._menu_config[menu_id]

            log.info(f"Menu deleted successfully: {menu_id} by {deleted_by}")

        return success

    @measure("service_batch_import_menus_seconds")
    async def batch_import_menus(self, menus: List['MenuCreateRequest'], created_by: str,
                               clear_existing: bool = False) -> Dict[str, Any]:
        """批量导入菜单"""
        if not self.menu_repo:
            raise RuntimeError("Menu repository not available")

        result = {
            "total_count": len(menus),
            "created_count": 0,
            "skipped_count": 0,
            "errors": []
        }

        try:
            # 如果需要清除现有菜单
            if clear_existing:
                cleared_count = await self.menu_repo.clear_all_menus(created_by)
                self._menu_config.clear()
                log.info(f"Cleared {cleared_count} existing menus")

            # 转换为MenuConfig列表
            menu_configs = []
            for menu_request in menus:
                try:
                    # 检查是否已存在
                    existing = await self.menu_repo.get_menu_by_id(menu_request.id)
                    if existing and not clear_existing:
                        result["skipped_count"] += 1
                        continue

                    menu_config = MenuConfig(
                        id=menu_request.id,
                        name=menu_request.name,
                        title=menu_request.title,
                        title_en=menu_request.title_en,
                        path=menu_request.path,
                        component=menu_request.component,
                        icon=menu_request.icon,
                        emoji=menu_request.emoji,
                        parent_id=menu_request.parent_id,
                        permission=menu_request.permission,
                        menu_type=menu_request.menu_type,
                        sort_order=menu_request.sort_order,
                        is_hidden=menu_request.is_hidden,
                        is_external=menu_request.is_external,
                        status=menu_request.status,
                        meta=menu_request.meta,
                        children=None
                    )
                    menu_configs.append(menu_config)

                except Exception as e:
                    result["errors"].append({
                        "menu_id": menu_request.id,
                        "error": str(e)
                    })

            # 批量创建
            if menu_configs:
                created_count = await self.menu_repo.batch_create_menus(menu_configs, created_by)
                result["created_count"] = created_count

                # 更新内存缓存
                for menu_config in menu_configs:
                    self._menu_config[menu_config.id] = menu_config

            log.info(f"Batch import completed: {result}")
            return result

        except Exception as e:
            log.error(f"Batch import failed: {e}")
            raise

    async def get_menu_from_database(self, menu_id: str) -> Optional[MenuConfig]:
        """从数据库获取菜单"""
        if not self.menu_repo:
            return None

        return await self.menu_repo.get_menu_by_id(menu_id)

    async def reload_menus_from_database(self) -> int:
        """从数据库重新加载所有菜单到内存"""
        if not self.menu_repo:
            return 0

        try:
            db_menus = await self.menu_repo.get_all_menus(status="active")

            # 清空当前缓存
            self._menu_config.clear()

            # 重新构建缓存
            for menu in db_menus:
                self._menu_config[menu.id] = menu

            log.info(f"Reloaded {len(db_menus)} menus from database")
            return len(db_menus)

        except Exception as e:
            log.error(f"Failed to reload menus from database: {e}")
            raise