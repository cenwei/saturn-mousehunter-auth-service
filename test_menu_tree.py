#!/usr/bin/env python3
"""
Auth微服务菜单功能测试脚本
测试多级树形菜单初始化和显示
"""

import sys
import json
from pathlib import Path

# 添加src路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from domain.models.auth_menu import (
        MenuConfig, MenuTree, DEFAULT_MENU_CONFIG, MenuType
    )
    print("✅ 成功导入菜单模块")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


class MenuTestService:
    """菜单测试服务"""

    def __init__(self):
        self.menu_configs = DEFAULT_MENU_CONFIG

    def display_menu_hierarchy(self):
        """显示菜单层级结构"""
        print("\n🌳 菜单层级结构:")
        print("=" * 60)

        for i, menu in enumerate(self.menu_configs, 1):
            self._display_menu_item(menu, level=0, index=i)

        print("=" * 60)

    def _display_menu_item(self, menu: MenuConfig, level: int = 0, index: int = 1):
        """递归显示菜单项"""
        indent = "  " * level
        icon = menu.icon or "📋"

        if level == 0:
            print(f"{indent}{index}. {icon} {menu.title} ({menu.id})")
            print(f"{indent}   路径: {menu.path}")
            print(f"{indent}   权限: {menu.permission}")
        else:
            print(f"{indent}├─ {icon} {menu.title} ({menu.id})")
            print(f"{indent}   路径: {menu.path}")
            print(f"{indent}   权限: {menu.permission}")

        if menu.children:
            for child_index, child in enumerate(menu.children, 1):
                self._display_menu_item(child, level + 1, child_index)

    def get_menu_statistics(self):
        """获取菜单统计信息"""
        total_menus = 0
        total_permissions = set()
        menu_types = {"menu": 0, "button": 0, "tab": 0}

        def count_menu(menu: MenuConfig):
            nonlocal total_menus
            total_menus += 1
            if menu.permission:
                total_permissions.add(menu.permission)
            menu_types[menu.menu_type.value] += 1

            if menu.children:
                for child in menu.children:
                    count_menu(child)

        for menu in self.menu_configs:
            count_menu(menu)

        return {
            "total_menus": total_menus,
            "total_permissions": len(total_permissions),
            "menu_types": menu_types,
            "permissions": list(total_permissions)
        }

    def convert_to_tree_structure(self):
        """转换为前端可用的树形结构"""
        tree_menus = []

        def convert_menu(menu: MenuConfig) -> dict:
            tree_node = {
                "id": menu.id,
                "name": menu.name,
                "title": menu.title,
                "path": menu.path,
                "icon": menu.icon,
                "permission": menu.permission,
                "menu_type": menu.menu_type.value,
                "sort_order": menu.sort_order,
                "is_hidden": menu.is_hidden,
                "meta": menu.meta or {},
                "children": []
            }

            if menu.children:
                for child in menu.children:
                    tree_node["children"].append(convert_menu(child))

            return tree_node

        for menu in self.menu_configs:
            tree_menus.append(convert_menu(menu))

        return tree_menus

    def test_menu_permission_filtering(self):
        """测试菜单权限过滤"""
        print("\n🔒 菜单权限过滤测试:")
        print("=" * 60)

        # 模拟不同用户权限
        test_permissions = [
            # 管理员权限
            {
                "user_type": "ADMIN",
                "permissions": [
                    "menu:dashboard", "menu:user_management", "menu:role_management",
                    "menu:strategy", "menu:risk", "menu:system", "menu:reports", "menu:audit",
                    "user:read", "user:write", "role:read", "role:write", "strategy:read",
                    "strategy:write", "risk:monitor", "risk:write", "system:config",
                    "system:monitor", "report:read", "audit:read"
                ]
            },
            # 租户用户权限
            {
                "user_type": "TENANT",
                "permissions": [
                    "menu:dashboard", "menu:strategy", "strategy:read", "report:read"
                ]
            },
            # 受限用户权限
            {
                "user_type": "LIMITED",
                "permissions": ["menu:dashboard"]
            }
        ]

        for perm_set in test_permissions:
            print(f"\n👤 {perm_set['user_type']} 用户可访问菜单:")
            user_perms = set(perm_set['permissions'])
            accessible_menus = self._filter_menus_by_permissions(user_perms)

            for menu in accessible_menus:
                print(f"  ✅ {menu['title']} ({menu['id']})")
                for child in menu.get('children', []):
                    print(f"     └─ {child['title']} ({child['id']})")

    def _filter_menus_by_permissions(self, user_permissions: set) -> list:
        """根据权限过滤菜单"""
        filtered_menus = []

        def has_permission(menu_permission: str) -> bool:
            return not menu_permission or menu_permission in user_permissions

        def filter_menu(menu: MenuConfig) -> dict:
            if not has_permission(menu.permission):
                return None

            filtered_menu = {
                "id": menu.id,
                "title": menu.title,
                "path": menu.path,
                "icon": menu.icon,
                "permission": menu.permission,
                "children": []
            }

            if menu.children:
                for child in menu.children:
                    filtered_child = filter_menu(child)
                    if filtered_child:
                        filtered_menu["children"].append(filtered_child)

            return filtered_menu

        for menu in self.menu_configs:
            filtered_menu = filter_menu(menu)
            if filtered_menu:
                filtered_menus.append(filtered_menu)

        return filtered_menus


def main():
    """主测试函数"""
    print("🧪 Auth微服务菜单功能测试")
    print("=" * 60)

    # 初始化测试服务
    menu_service = MenuTestService()

    # 1. 显示菜单层级结构
    menu_service.display_menu_hierarchy()

    # 2. 显示统计信息
    stats = menu_service.get_menu_statistics()
    print(f"\n📊 菜单统计信息:")
    print(f"总菜单数: {stats['total_menus']}")
    print(f"权限数量: {stats['total_permissions']}")
    print(f"菜单类型: {stats['menu_types']}")

    # 3. 测试权限过滤
    menu_service.test_menu_permission_filtering()

    # 4. 生成树形结构JSON
    tree_structure = menu_service.convert_to_tree_structure()
    print(f"\n🌳 树形结构已生成 (共{len(tree_structure)}个根菜单)")

    # 保存树形结构到文件
    output_file = Path(__file__).parent / "docs" / "menu_tree_structure.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tree_structure, f, ensure_ascii=False, indent=2)

    print(f"📁 菜单树形结构已保存到: {output_file}")

    print("\n✅ 菜单功能测试完成!")


if __name__ == "__main__":
    main()