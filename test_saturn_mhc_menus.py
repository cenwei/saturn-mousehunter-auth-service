#!/usr/bin/env python3
"""
测试Saturn MHC完整菜单配置
"""
import sys
import asyncio
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.models.auth_menu import SATURN_MHC_MENU_CONFIG, MENU_PERMISSIONS, MenuTree
from domain.models.auth_user_role import UserType
from application.services.menu_permission_service import MenuPermissionService


class MockUserRoleRepo:
    """模拟用户角色仓库"""
    async def get_user_permissions(self, user_id: str, user_type: UserType):
        class MockPermissions:
            def __init__(self, permissions):
                self.permissions = permissions

        # 模拟不同用户类型的权限
        if user_type == UserType.ADMIN:
            return MockPermissions(["menu:dashboard", "menu:user_management", "user:read"])
        elif user_type == UserType.TENANT:
            return MockPermissions(["menu:dashboard", "menu:strategy"])
        else:
            return MockPermissions(["menu:dashboard"])


async def test_saturn_mhc_menu_config():
    """测试Saturn MHC菜单配置"""
    print("🧪 Testing Saturn MHC Menu Configuration")
    print("=" * 60)

    # 菜单配置统计
    print(f"📊 Menu Statistics:")
    print(f"   Total menus: {len(SATURN_MHC_MENU_CONFIG)}")

    # 统计子菜单
    total_children = 0
    for menu in SATURN_MHC_MENU_CONFIG:
        if menu.children:
            total_children += len(menu.children)

    print(f"   Root menus: {len(SATURN_MHC_MENU_CONFIG)}")
    print(f"   Child menus: {total_children}")
    print(f"   Total permissions: {len(MENU_PERMISSIONS)}")
    print()

    # 显示菜单结构
    print("📋 Saturn MHC Menu Structure:")
    for menu in sorted(SATURN_MHC_MENU_CONFIG, key=lambda x: x.sort_order):
        emoji = menu.emoji or "📄"
        print(f"   {emoji} {menu.title} ({menu.id})")
        print(f"      Path: {menu.path}")
        print(f"      Permission: {menu.permission}")
        if menu.children:
            for child in menu.children:
                print(f"        ├─ {child.title} ({child.id})")
                print(f"           Path: {child.path}")
                print(f"           Permission: {child.permission}")
        print()

    # 权限映射统计
    print("🔐 Permission Mapping Statistics:")
    admin_perms = [p for p, roles in MENU_PERMISSIONS.items() if "ADMIN" in roles]
    tenant_perms = [p for p, roles in MENU_PERMISSIONS.items() if "TENANT" in roles]
    limited_perms = [p for p, roles in MENU_PERMISSIONS.items() if "LIMITED" in roles]

    print(f"   ADMIN permissions: {len(admin_perms)}")
    print(f"   TENANT permissions: {len(tenant_perms)}")
    print(f"   LIMITED permissions: {len(limited_perms)}")
    print()


async def test_menu_permission_service():
    """测试菜单权限服务"""
    print("🔧 Testing Menu Permission Service")
    print("=" * 60)

    # 创建服务实例
    mock_repo = MockUserRoleRepo()

    # 测试Saturn MHC菜单配置
    print("📋 Testing with Saturn MHC Menu Config:")
    service_mhc = MenuPermissionService(mock_repo, use_saturn_mhc_menus=True)

    # 测试不同用户类型的菜单访问
    user_types = [UserType.ADMIN, UserType.TENANT, UserType.LIMITED]

    for user_type in user_types:
        print(f"\n👤 Testing {user_type.value} user:")

        # 获取用户菜单
        user_menus = await service_mhc.get_user_accessible_menus(
            f"test_{user_type.value.lower()}_user",
            user_type
        )

        print(f"   Accessible menus: {len(user_menus.menus)}")
        print(f"   User permissions: {len(user_menus.permissions)}")

        # 显示可访问菜单
        for menu in user_menus.menus[:5]:  # 只显示前5个
            emoji = menu.emoji or "📄"
            print(f"   {emoji} {menu.title} ({menu.path})")

        if len(user_menus.menus) > 5:
            print(f"   ... and {len(user_menus.menus) - 5} more menus")

        # 获取菜单统计
        stats = await service_mhc.get_menu_stats(
            f"test_{user_type.value.lower()}_user",
            user_type
        )

        print(f"   Menu stats:")
        print(f"     Total: {stats.total_menus}")
        print(f"     Accessible: {stats.accessible_menus}")
        print(f"     Coverage: {stats.permission_coverage}%")

    # 测试菜单权限检查
    print(f"\n🔍 Testing Menu Permission Checks:")
    test_menus = ["dashboard", "proxy_pool", "user_management", "api_explorer"]

    for menu_id in test_menus:
        admin_check = await service_mhc.validate_menu_access("admin_user", UserType.ADMIN, menu_id)
        tenant_check = await service_mhc.validate_menu_access("tenant_user", UserType.TENANT, menu_id)

        print(f"   Menu '{menu_id}':")
        print(f"     ADMIN: {'✅' if admin_check.has_permission else '❌'}")
        print(f"     TENANT: {'✅' if tenant_check.has_permission else '❌'}")


async def test_menu_tree():
    """测试菜单树结构"""
    print("\n🌳 Testing Menu Tree Structure")
    print("=" * 60)

    mock_repo = MockUserRoleRepo()
    service = MenuPermissionService(mock_repo, use_saturn_mhc_menus=True)

    # 获取完整菜单树
    menu_tree = service.get_menu_tree()

    print(f"📊 Menu Tree Statistics:")
    print(f"   Root nodes: {len(menu_tree)}")

    total_nodes = len(menu_tree)
    for menu in menu_tree:
        total_nodes += len(menu.children)

    print(f"   Total nodes: {total_nodes}")

    print(f"\n📋 Menu Tree Structure:")
    for menu in menu_tree[:3]:  # 只显示前3个根菜单
        emoji = menu.emoji or "📄"
        print(f"   {emoji} {menu.title}")
        print(f"      ID: {menu.id}")
        print(f"      Path: {menu.path}")
        print(f"      Permission: {menu.permission}")
        print(f"      Sort Order: {menu.sort_order}")

        if menu.children:
            for child in menu.children:
                child_emoji = getattr(child, 'emoji', None) or "📄"
                print(f"        ├─ {child_emoji} {child.title}")
                print(f"           ID: {child.id}")
                print(f"           Path: {child.path}")
        print()


async def main():
    """主函数"""
    print("🚀 Saturn MHC Menu Configuration Test Suite")
    print("=" * 70)
    print()

    try:
        await test_saturn_mhc_menu_config()
        await test_menu_permission_service()
        await test_menu_tree()

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)