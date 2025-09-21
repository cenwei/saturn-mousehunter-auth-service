#!/usr/bin/env python3
"""
测试菜单批量导入API
"""
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

BASE_URL = "http://192.168.8.168:8001"

# 获取新的admin token
async def get_admin_token():
    """获取管理员token"""
    async with aiohttp.ClientSession() as session:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        async with session.post(
            f"{BASE_URL}/api/v1/admin/users/login",
            json=login_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result["access_token"]
            else:
                raise Exception(f"Login failed: {response.status}")

async def test_batch_import():
    """测试批量导入菜单"""
    print("🧪 Testing Menu Batch Import API")
    print("=" * 60)

    # 获取管理员token
    print("🔐 Getting admin token...")
    try:
        token = await get_admin_token()
        print(f"   ✅ Token obtained: {token[:50]}...")
    except Exception as e:
        print(f"   ❌ Failed to get token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 准备测试菜单数据
    test_menus = [
        {
            "id": "test_menu_1",
            "name": "test_menu_1",
            "title": "测试菜单1",
            "title_en": "Test Menu 1",
            "path": "/test-menu-1",
            "component": "TestMenu1",
            "icon": "test",
            "emoji": "🧪",
            "permission": "menu:test_menu_1",
            "menu_type": "menu",
            "sort_order": 100,
            "is_hidden": False,
            "is_external": False,
            "status": "active",
            "meta": {
                "title": "测试菜单1",
                "title_en": "Test Menu 1",
                "description": "This is a test menu"
            }
        },
        {
            "id": "test_menu_2",
            "name": "test_menu_2",
            "title": "测试菜单2",
            "title_en": "Test Menu 2",
            "path": "/test-menu-2",
            "component": "TestMenu2",
            "icon": "test",
            "emoji": "🔬",
            "permission": "menu:test_menu_2",
            "menu_type": "menu",
            "sort_order": 101,
            "is_hidden": False,
            "is_external": False,
            "status": "active",
            "meta": {
                "title": "测试菜单2",
                "title_en": "Test Menu 2"
            }
        },
        {
            "id": "test_submenu_1",
            "name": "test_submenu_1",
            "title": "测试子菜单1",
            "title_en": "Test Submenu 1",
            "path": "/test-menu-1/submenu-1",
            "component": "TestSubmenu1",
            "parent_id": "test_menu_1",
            "permission": "menu:test_submenu_1",
            "menu_type": "menu",
            "sort_order": 1,
            "is_hidden": False,
            "is_external": False,
            "status": "active",
            "meta": {
                "title": "测试子菜单1",
                "title_en": "Test Submenu 1"
            }
        }
    ]

    async with aiohttp.ClientSession() as session:

        # ===== 1. 测试批量导入 (增量导入) =====
        print("\n1️⃣ Testing Batch Import (Incremental)")
        print("-" * 50)

        import_request = {
            "menus": test_menus,
            "clear_existing": False
        }

        try:
            async with session.post(
                f"{BASE_URL}/api/v1/menus/batch-import",
                headers=headers,
                json=import_request
            ) as response:
                print(f"   Status: {response.status}")
                result = await response.json()

                if response.status == 200:
                    print(f"   ✅ Success: {result['message']}")
                    print(f"   📊 Imported Count: {result['data']['imported_count']}")
                    print(f"   🔄 Clear Existing: {result['data']['clear_existing']}")
                else:
                    print(f"   ❌ Failed: {result}")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

        # ===== 2. 验证导入结果 =====
        print("\n2️⃣ Verifying Import Results")
        print("-" * 50)

        try:
            async with session.get(f"{BASE_URL}/api/v1/menus/tree", headers=headers) as response:
                if response.status == 200:
                    menu_tree = await response.json()

                    # 查找测试菜单
                    test_menu_found = []
                    for menu in menu_tree:
                        if menu['id'].startswith('test_'):
                            test_menu_found.append(menu['id'])
                            print(f"   ✅ Found: {menu['title']} (ID: {menu['id']})")

                            # 检查子菜单
                            for child in menu.get('children', []):
                                if child['id'].startswith('test_'):
                                    test_menu_found.append(child['id'])
                                    print(f"      └─ ✅ Child: {child['title']} (ID: {child['id']})")

                    print(f"   📊 Total test menus found: {len(test_menu_found)}")

                else:
                    print(f"   ❌ Failed to get menu tree: {response.status}")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

        # ===== 3. 测试单个菜单查询 =====
        print("\n3️⃣ Testing Individual Menu Query")
        print("-" * 50)

        for test_menu in test_menus[:2]:  # 只测试前两个
            menu_id = test_menu['id']
            try:
                async with session.get(f"{BASE_URL}/api/v1/menus/{menu_id}", headers=headers) as response:
                    if response.status == 200:
                        menu_detail = await response.json()
                        print(f"   ✅ {menu_id}: {menu_detail.get('title')}")
                    elif response.status == 404:
                        print(f"   ❌ {menu_id}: Not found (may not be implemented)")
                    else:
                        print(f"   ❌ {menu_id}: Error {response.status}")
            except Exception as e:
                print(f"   💥 {menu_id}: Exception - {str(e)}")

        # ===== 4. 测试菜单删除 (清理) =====
        print("\n4️⃣ Testing Menu Cleanup")
        print("-" * 50)

        for test_menu in test_menus:
            menu_id = test_menu['id']
            try:
                async with session.delete(f"{BASE_URL}/api/v1/menus/{menu_id}", headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Deleted: {menu_id}")
                    elif response.status == 404:
                        print(f"   ❌ {menu_id}: Not found (may not be implemented)")
                    else:
                        print(f"   ❌ {menu_id}: Delete failed {response.status}")
            except Exception as e:
                print(f"   💥 {menu_id}: Exception - {str(e)}")

    print("\n📊 Test Summary")
    print("=" * 60)
    print("✅ Batch import API tested")
    print("📋 Test scenarios:")
    print("   1. Incremental batch import")
    print("   2. Import result verification")
    print("   3. Individual menu query")
    print("   4. Menu cleanup (delete)")
    print()
    print("💡 Note: Some endpoints may return 'not implemented' - this is expected")
    print("🔗 Batch import endpoint: POST /api/v1/menus/batch-import")


if __name__ == "__main__":
    asyncio.run(test_batch_import())