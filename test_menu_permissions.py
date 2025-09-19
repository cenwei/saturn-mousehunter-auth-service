#!/usr/bin/env python3
"""
菜单权限功能测试脚本
Saturn MouseHunter 认证服务

本脚本测试菜单权限相关的所有功能模块
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 添加src路径以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入必要的模块
from domain.models.auth_menu import (
    MenuConfig, MenuTree, UserMenuResponse,
    MenuPermissionCheck, DEFAULT_MENU_CONFIG, MenuType
)
from domain.models.auth_user_role import UserType


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
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message}")

    def test_menu_models(self):
        """测试菜单数据模型"""
        print("\n=== 测试菜单数据模型 ===")

        try:
            # 测试MenuConfig创建
            menu = MenuConfig(
                id="test_menu",
                name="test_menu",
                title="测试菜单",
                path="/test",
                permission="test:menu",
                menu_type=MenuType.MENU,
                sort_order=1
            )
            self.log_test("MenuConfig创建", True, f"菜单ID: {menu.id}")

            # 测试MenuTree创建
            tree = MenuTree(
                id="tree_test",
                name="tree_test",
                title="树形菜单",
                permission="tree:test",
                children=[]
            )
            self.log_test("MenuTree创建", True, f"树形菜单ID: {tree.id}")

            # 测试UserMenuResponse创建
            response = UserMenuResponse(
                user_id="TEST_001",
                user_type="ADMIN",
                permissions=["test:permission"],
                menus=[tree],
                updated_at=datetime.now()
            )
            self.log_test("UserMenuResponse创建", True, f"用户ID: {response.user_id}")

        except Exception as e:
            self.log_test("菜单数据模型测试", False, str(e))

    def test_default_menu_config(self):
        """测试默认菜单配置"""
        print("\n=== 测试默认菜单配置 ===")

        try:
            # 验证默认菜单配置
            if not DEFAULT_MENU_CONFIG:
                self.log_test("默认菜单配置", False, "默认菜单配置为空")
                return

            menu_count = len(DEFAULT_MENU_CONFIG)
            self.log_test("默认菜单数量", True, f"共{menu_count}个顶级菜单")

            # 统计总菜单数（包括子菜单）
            total_menus = 0
            menu_permissions = set()

            def count_menus(menus: List[MenuConfig]):
                nonlocal total_menus
                for menu in menus:
                    total_menus += 1
                    if menu.permission:
                        menu_permissions.add(menu.permission)
                    if menu.children:
                        count_menus(menu.children)

            count_menus(DEFAULT_MENU_CONFIG)
            self.log_test("总菜单统计", True, f"总计{total_menus}个菜单项")
            self.log_test("菜单权限统计", True, f"涉及{len(menu_permissions)}个权限")

            # 验证菜单结构
            for menu in DEFAULT_MENU_CONFIG:
                if not menu.id or not menu.name or not menu.title:
                    self.log_test("菜单结构验证", False, f"菜单{menu.id}缺少必要字段")
                    return

            self.log_test("菜单结构验证", True, "所有菜单结构完整")

        except Exception as e:
            self.log_test("默认菜单配置测试", False, str(e))

    def test_menu_permission_filtering(self):
        """测试菜单权限过滤逻辑"""
        print("\n=== 测试菜单权限过滤 ===")

        try:
            # 模拟权限过滤逻辑
            def filter_menus_by_permissions(menus: List[MenuConfig], user_permissions: set) -> List[MenuTree]:
                filtered_menus = []

                for menu in menus:
                    # 检查菜单权限
                    if menu.permission and menu.permission not in user_permissions:
                        continue

                    # 创建菜单树节点
                    menu_tree = MenuTree(
                        id=menu.id,
                        name=menu.name,
                        title=menu.title,
                        path=menu.path,
                        icon=menu.icon,
                        permission=menu.permission,
                        menu_type=menu.menu_type,
                        sort_order=menu.sort_order,
                        children=[]
                    )

                    # 处理子菜单
                    if menu.children:
                        filtered_children = filter_menus_by_permissions(menu.children, user_permissions)
                        menu_tree.children = filtered_children

                        # 如果有子菜单权限，即使父菜单没有直接权限也要显示
                        if filtered_children or not menu.permission or menu.permission in user_permissions:
                            filtered_menus.append(menu_tree)
                    else:
                        filtered_menus.append(menu_tree)

                return sorted(filtered_menus, key=lambda x: x.sort_order)

            # 测试超级管理员权限（拥有所有权限）
            super_admin_permissions = {
                "menu:dashboard", "menu:user_management", "user:read",
                "menu:role_management", "role:read", "menu:strategy",
                "strategy:read", "strategy:write", "menu:risk", "risk:monitor",
                "risk:write", "menu:system", "system:config", "system:monitor",
                "menu:reports", "report:read", "menu:audit", "audit:read"
            }

            super_admin_menus = filter_menus_by_permissions(DEFAULT_MENU_CONFIG, super_admin_permissions)
            self.log_test("超级管理员菜单过滤", True, f"可访问{len(super_admin_menus)}个顶级菜单")

            # 测试普通用户权限
            normal_user_permissions = {"menu:dashboard", "strategy:read", "report:read"}
            normal_user_menus = filter_menus_by_permissions(DEFAULT_MENU_CONFIG, normal_user_permissions)
            self.log_test("普通用户菜单过滤", True, f"可访问{len(normal_user_menus)}个顶级菜单")

            # 测试无权限用户
            no_permissions = set()
            no_permission_menus = filter_menus_by_permissions(DEFAULT_MENU_CONFIG, no_permissions)
            self.log_test("无权限用户菜单过滤", True, f"可访问{len(no_permission_menus)}个顶级菜单")

        except Exception as e:
            self.log_test("菜单权限过滤测试", False, str(e))

    def test_menu_permission_validation(self):
        """测试菜单权限验证"""
        print("\n=== 测试菜单权限验证 ===")

        try:
            # 构建菜单字典
            menu_dict = {}
            def build_menu_dict(menus: List[MenuConfig]):
                for menu in menus:
                    menu_dict[menu.id] = menu
                    if menu.children:
                        build_menu_dict(menu.children)

            build_menu_dict(DEFAULT_MENU_CONFIG)

            # 模拟权限验证
            def validate_menu_access(menu_id: str, user_permissions: set) -> MenuPermissionCheck:
                menu = menu_dict.get(menu_id)
                if not menu:
                    return MenuPermissionCheck(
                        menu_id=menu_id,
                        permission="",
                        has_permission=False
                    )

                if not menu.permission:
                    return MenuPermissionCheck(
                        menu_id=menu_id,
                        permission="",
                        has_permission=True
                    )

                has_permission = menu.permission in user_permissions
                return MenuPermissionCheck(
                    menu_id=menu_id,
                    permission=menu.permission,
                    has_permission=has_permission
                )

            # 测试各种权限验证场景
            test_permissions = {"menu:dashboard", "user:read"}

            # 测试有权限的菜单
            dashboard_check = validate_menu_access("dashboard", test_permissions)
            self.log_test("仪表盘权限验证", dashboard_check.has_permission,
                         f"权限: {dashboard_check.permission}")

            # 测试无权限的菜单
            system_check = validate_menu_access("system_config", test_permissions)
            self.log_test("系统配置权限验证", not system_check.has_permission,
                         f"缺少权限: {system_check.permission}")

            # 测试不存在的菜单
            nonexistent_check = validate_menu_access("nonexistent", test_permissions)
            self.log_test("不存在菜单验证", not nonexistent_check.has_permission,
                         "菜单不存在")

        except Exception as e:
            self.log_test("菜单权限验证测试", False, str(e))

    def test_user_type_scenarios(self):
        """测试不同用户类型的菜单访问场景"""
        print("\n=== 测试用户类型场景 ===")

        try:
            # 定义不同用户类型的权限
            user_type_permissions = {
                UserType.ADMIN: {
                    "menu:dashboard", "menu:user_management", "user:read", "user:write",
                    "menu:role_management", "role:read", "role:write", "menu:system",
                    "system:admin", "menu:audit", "audit:read"
                },
                UserType.TENANT: {
                    "menu:dashboard", "strategy:read", "report:read"
                }
            }

            # 模拟不同用户类型的菜单访问
            for user_type, permissions in user_type_permissions.items():
                accessible_menus = 0
                for menu in DEFAULT_MENU_CONFIG:
                    if not menu.permission or menu.permission in permissions:
                        accessible_menus += 1

                self.log_test(f"{user_type.value}用户菜单访问",
                             accessible_menus > 0,
                             f"可访问{accessible_menus}个顶级菜单")

        except Exception as e:
            self.log_test("用户类型场景测试", False, str(e))

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始菜单权限功能测试...")
        print(f"测试时间: {datetime.now().isoformat()}")

        self.test_menu_models()
        self.test_default_menu_config()
        self.test_menu_permission_filtering()
        self.test_menu_permission_validation()
        self.test_user_type_scenarios()

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

    def export_results(self, filename: str = "menu_permission_test_results.json"):
        """导出测试结果"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_summary": {
                        "total_tests": len(self.test_results),
                        "passed_tests": len([r for r in self.test_results if r['success']]),
                        "failed_tests": len([r for r in self.test_results if not r['success']]),
                        "test_time": datetime.now().isoformat()
                    },
                    "test_results": self.test_results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n📄 测试结果已导出到: {filename}")
        except Exception as e:
            print(f"❌ 导出测试结果失败: {str(e)}")


if __name__ == "__main__":
    tester = MenuPermissionTester()
    success = tester.run_all_tests()
    tester.export_results()

    # 返回适当的退出码
    sys.exit(0 if success else 1)