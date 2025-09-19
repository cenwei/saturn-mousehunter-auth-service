#!/usr/bin/env python3
"""
菜单权限功能简化测试脚本
Saturn MouseHunter 认证服务

本脚本使用纯Python测试菜单权限的核心逻辑
"""
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Set


class MenuType(str, Enum):
    """菜单类型"""
    MENU = "menu"
    BUTTON = "button"
    TAB = "tab"


class UserType(str, Enum):
    """用户类型"""
    ADMIN = "ADMIN"
    TENANT = "TENANT"


class MenuConfig:
    """简化的菜单配置"""
    def __init__(self, id: str, name: str, title: str, path: str = None,
                 icon: str = None, permission: str = None, sort_order: int = 0,
                 children: List['MenuConfig'] = None):
        self.id = id
        self.name = name
        self.title = title
        self.path = path
        self.icon = icon
        self.permission = permission
        self.sort_order = sort_order
        self.children = children or []


class MenuTree:
    """简化的菜单树"""
    def __init__(self, id: str, name: str, title: str, permission: str = None,
                 sort_order: int = 0, children: List['MenuTree'] = None):
        self.id = id
        self.name = name
        self.title = title
        self.permission = permission
        self.sort_order = sort_order
        self.children = children or []


# 默认菜单配置
DEFAULT_MENU_CONFIG = [
    MenuConfig(
        id="dashboard",
        name="dashboard",
        title="仪表盘",
        path="/dashboard",
        icon="dashboard",
        permission="menu:dashboard",
        sort_order=1
    ),
    MenuConfig(
        id="user_management",
        name="user_management",
        title="用户管理",
        path="/users",
        icon="users",
        permission="menu:user_management",
        sort_order=2,
        children=[
            MenuConfig(
                id="admin_users",
                name="admin_users",
                title="管理员用户",
                path="/users/admin",
                permission="user:read",
                sort_order=1
            ),
            MenuConfig(
                id="tenant_users",
                name="tenant_users",
                title="租户用户",
                path="/users/tenant",
                permission="user:read",
                sort_order=2
            )
        ]
    ),
    MenuConfig(
        id="role_management",
        name="role_management",
        title="角色管理",
        path="/roles",
        icon="role",
        permission="menu:role_management",
        sort_order=3,
        children=[
            MenuConfig(
                id="role_list",
                name="role_list",
                title="角色列表",
                path="/roles/list",
                permission="role:read",
                sort_order=1
            )
        ]
    ),
    MenuConfig(
        id="strategy_management",
        name="strategy_management",
        title="策略管理",
        path="/strategy",
        icon="strategy",
        permission="menu:strategy",
        sort_order=4,
        children=[
            MenuConfig(
                id="strategy_list",
                name="strategy_list",
                title="策略列表",
                path="/strategy/list",
                permission="strategy:read",
                sort_order=1
            )
        ]
    ),
    MenuConfig(
        id="system_management",
        name="system_management",
        title="系统设置",
        path="/system",
        icon="system",
        permission="menu:system",
        sort_order=5,
        children=[
            MenuConfig(
                id="system_config",
                name="system_config",
                title="系统配置",
                path="/system/config",
                permission="system:config",
                sort_order=1
            )
        ]
    )
]


class MenuPermissionTester:
    """菜单权限测试器"""

    def __init__(self):
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}: {message}")

    def filter_menus_by_permissions(self, menus: List[MenuConfig], user_permissions: Set[str]) -> List[MenuTree]:
        """根据用户权限过滤菜单"""
        filtered_menus = []

        for menu in menus:
            # 创建菜单树节点
            menu_tree = MenuTree(
                id=menu.id,
                name=menu.name,
                title=menu.title,
                permission=menu.permission,
                sort_order=menu.sort_order,
                children=[]
            )

            # 处理子菜单
            if menu.children:
                filtered_children = self.filter_menus_by_permissions(menu.children, user_permissions)
                menu_tree.children = filtered_children

                # 如果有子菜单权限，即使父菜单没有直接权限也要显示
                # 或者父菜单有权限也要显示
                if filtered_children or not menu.permission or menu.permission in user_permissions:
                    filtered_menus.append(menu_tree)
            else:
                # 叶子菜单：检查权限
                if not menu.permission or menu.permission in user_permissions:
                    filtered_menus.append(menu_tree)

        return sorted(filtered_menus, key=lambda x: x.sort_order)

    def count_total_menus(self, menus: List[MenuConfig]) -> int:
        """统计总菜单数"""
        count = 0
        for menu in menus:
            count += 1
            if menu.children:
                count += self.count_total_menus(menu.children)
        return count

    def test_menu_structure(self):
        """测试菜单结构"""
        print("\n=== 测试菜单结构 ===")

        try:
            total_menus = self.count_total_menus(DEFAULT_MENU_CONFIG)
            top_level_menus = len(DEFAULT_MENU_CONFIG)

            self.log_test("菜单配置加载", True, f"顶级菜单: {top_level_menus}, 总菜单: {total_menus}")

            # 验证菜单完整性
            for menu in DEFAULT_MENU_CONFIG:
                if not menu.id or not menu.name or not menu.title:
                    self.log_test("菜单完整性检查", False, f"菜单{menu.id}缺少必要字段")
                    return

            self.log_test("菜单完整性检查", True, "所有菜单字段完整")

            # 统计权限
            permissions = set()
            def collect_permissions(menus):
                for menu in menus:
                    if menu.permission:
                        permissions.add(menu.permission)
                    if menu.children:
                        collect_permissions(menu.children)

            collect_permissions(DEFAULT_MENU_CONFIG)
            self.log_test("权限统计", True, f"涉及{len(permissions)}个不同权限")

        except Exception as e:
            self.log_test("菜单结构测试", False, str(e))

    def test_permission_filtering(self):
        """测试权限过滤"""
        print("\n=== 测试权限过滤 ===")

        try:
            # 测试超级管理员权限
            super_admin_permissions = {
                "menu:dashboard", "menu:user_management", "user:read",
                "menu:role_management", "role:read", "menu:strategy", "strategy:read",
                "menu:system", "system:config"
            }

            super_admin_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, super_admin_permissions)
            super_admin_count = len(super_admin_menus)
            self.log_test("超级管理员权限过滤", super_admin_count >= 4,
                         f"可访问{super_admin_count}个顶级菜单")

            # 测试策略管理员权限
            strategy_manager_permissions = {"menu:dashboard", "menu:strategy", "strategy:read"}
            strategy_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, strategy_manager_permissions)
            strategy_count = len(strategy_menus)
            self.log_test("策略管理员权限过滤", strategy_count >= 2,
                         f"可访问{strategy_count}个顶级菜单")

            # 测试普通用户权限
            normal_user_permissions = {"menu:dashboard"}
            normal_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, normal_user_permissions)
            normal_count = len(normal_menus)
            self.log_test("普通用户权限过滤", normal_count >= 1,
                         f"可访问{normal_count}个顶级菜单")

            # 测试无权限用户
            no_permissions = set()
            no_permission_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, no_permissions)
            self.log_test("无权限用户过滤", len(no_permission_menus) == 0,
                         f"无权限用户应该看不到任何菜单")

        except Exception as e:
            self.log_test("权限过滤测试", False, str(e))

    def test_child_menu_filtering(self):
        """测试子菜单过滤"""
        print("\n=== 测试子菜单过滤 ===")

        try:
            # 测试有子菜单权限但无父菜单权限的情况
            child_only_permissions = {"user:read"}  # 只有子菜单权限，没有父菜单权限
            child_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, child_only_permissions)

            # 应该显示用户管理菜单（因为有子菜单权限）
            user_mgmt_menu = None
            for menu in child_menus:
                if menu.id == "user_management":
                    user_mgmt_menu = menu
                    break

            if user_mgmt_menu and len(user_mgmt_menu.children) > 0:
                self.log_test("子菜单权限继承", True,
                             f"父菜单显示，包含{len(user_mgmt_menu.children)}个子菜单")
            else:
                self.log_test("子菜单权限继承", False, "有子菜单权限时父菜单应该显示")

            # 测试父菜单权限但无子菜单权限
            parent_only_permissions = {"menu:user_management"}
            parent_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, parent_only_permissions)

            user_mgmt_parent = None
            for menu in parent_menus:
                if menu.id == "user_management":
                    user_mgmt_parent = menu
                    break

            if user_mgmt_parent:
                self.log_test("父菜单权限显示", True,
                             f"父菜单显示，子菜单数: {len(user_mgmt_parent.children)}")
            else:
                self.log_test("父菜单权限显示", False, "有父菜单权限时应该显示父菜单")

        except Exception as e:
            self.log_test("子菜单过滤测试", False, str(e))

    def test_user_scenarios(self):
        """测试不同用户场景"""
        print("\n=== 测试用户场景 ===")

        try:
            # 定义不同角色的权限
            role_permissions = {
                "超级管理员": {
                    "menu:dashboard", "menu:user_management", "user:read",
                    "menu:role_management", "role:read", "menu:strategy",
                    "strategy:read", "menu:system", "system:config"
                },
                "租户管理员": {
                    "menu:dashboard", "menu:user_management", "user:read",
                    "menu:strategy", "strategy:read"
                },
                "策略管理员": {
                    "menu:dashboard", "menu:strategy", "strategy:read"
                },
                "普通用户": {
                    "menu:dashboard"
                }
            }

            for role_name, permissions in role_permissions.items():
                accessible_menus = self.filter_menus_by_permissions(DEFAULT_MENU_CONFIG, permissions)
                menu_count = len(accessible_menus)

                # 计算子菜单总数
                total_accessible = menu_count
                for menu in accessible_menus:
                    total_accessible += len(menu.children)

                self.log_test(f"{role_name}菜单访问", menu_count > 0,
                             f"顶级菜单: {menu_count}, 总可访问: {total_accessible}")

        except Exception as e:
            self.log_test("用户场景测试", False, str(e))

    def test_menu_path_validation(self):
        """测试菜单路径验证"""
        print("\n=== 测试菜单路径验证 ===")

        try:
            # 构建菜单字典
            menu_dict = {}
            def build_menu_dict(menus):
                for menu in menus:
                    menu_dict[menu.id] = menu
                    if menu.children:
                        build_menu_dict(menu.children)

            build_menu_dict(DEFAULT_MENU_CONFIG)

            # 测试路径查找
            dashboard_menu = menu_dict.get("dashboard")
            if dashboard_menu and dashboard_menu.path == "/dashboard":
                self.log_test("菜单路径查找", True, f"仪表盘路径: {dashboard_menu.path}")
            else:
                self.log_test("菜单路径查找", False, "无法找到仪表盘菜单或路径错误")

            # 测试不存在的菜单
            nonexistent = menu_dict.get("nonexistent")
            self.log_test("不存在菜单查找", nonexistent is None, "不存在的菜单应该返回None")

        except Exception as e:
            self.log_test("菜单路径验证测试", False, str(e))

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始菜单权限功能测试...")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.test_menu_structure()
        self.test_permission_filtering()
        self.test_child_menu_filtering()
        self.test_user_scenarios()
        self.test_menu_path_validation()

        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests

        print(f"\n📊 测试总结:")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")

        return failed_tests == 0


if __name__ == "__main__":
    tester = MenuPermissionTester()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 所有测试通过！菜单权限功能正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查实现。")

    exit(0 if success else 1)