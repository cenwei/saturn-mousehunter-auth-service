#!/usr/bin/env python3
"""
使用现有菜单数据测试批量导入API
"""
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

BASE_URL = "http://192.168.8.168:8005"

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

def convert_menu_tree_to_import_format(menu_tree):
    """将菜单树转换为导入格式"""
    import_menus = []

    def process_menu(menu, parent_id=None):
        # 创建菜单项
        menu_item = {
            "id": menu["id"],
            "name": menu["name"],
            "title": menu["title"],
            "title_en": menu.get("title_en"),
            "path": menu.get("path"),
            "component": menu.get("component"),
            "icon": menu.get("icon"),
            "emoji": menu.get("emoji"),
            "parent_id": parent_id,
            "permission": menu.get("permission"),
            "menu_type": menu.get("menu_type", "menu"),
            "sort_order": menu.get("sort_order", 0),
            "is_hidden": menu.get("is_hidden", False),
            "is_external": menu.get("is_external", False),
            "status": menu.get("status", "active"),
            "meta": menu.get("meta")
        }

        import_menus.append(menu_item)

        # 处理子菜单
        for child in menu.get("children", []):
            process_menu(child, menu["id"])

    for menu in menu_tree:
        process_menu(menu)

    return import_menus

async def test_menu_import_with_existing_data():
    """使用现有菜单数据测试导入"""
    print("🧪 Testing Menu Import with Existing Data")
    print("=" * 60)

    # 获取管理员token
    print("🔐 Getting admin token...")
    try:
        token = await get_admin_token()
        print(f"   ✅ Token obtained")
    except Exception as e:
        print(f"   ❌ Failed to get token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:

        # ===== 1. 获取现有菜单数据 =====
        print("\n1️⃣ Getting Current Menu Tree")
        print("-" * 50)

        try:
            async with session.get(f"{BASE_URL}/api/v1/menus/tree", headers=headers) as response:
                if response.status == 200:
                    current_menu_tree = await response.json()
                    print(f"   ✅ Current menu count: {len(current_menu_tree)}")

                    # 统计子菜单
                    total_children = sum(len(menu.get('children', [])) for menu in current_menu_tree)
                    print(f"   📊 Total child menus: {total_children}")

                else:
                    print(f"   ❌ Failed to get menu tree: {response.status}")
                    return

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
            return

        # ===== 2. 转换为导入格式 =====
        print("\n2️⃣ Converting to Import Format")
        print("-" * 50)

        try:
            import_menus = convert_menu_tree_to_import_format(current_menu_tree)
            print(f"   ✅ Converted {len(import_menus)} menus for import")

            # 显示前3个菜单的转换结果
            print("   📋 Sample converted menus:")
            for i, menu in enumerate(import_menus[:3]):
                parent_info = f" (parent: {menu['parent_id']})" if menu['parent_id'] else ""
                print(f"      {i+1}. {menu['title']} (ID: {menu['id']}){parent_info}")

            # 保存到文件供查看
            with open("converted_menus_for_import.json", 'w', encoding='utf-8') as f:
                json.dump(import_menus, f, ensure_ascii=False, indent=2)
            print("   💾 Saved to: converted_menus_for_import.json")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
            return

        # ===== 3. 测试批量导入API =====
        print("\n3️⃣ Testing Batch Import API")
        print("-" * 50)

        # 选择前5个菜单进行测试，避免影响现有数据
        test_import_menus = import_menus[:5]
        for menu in test_import_menus:
            menu['id'] = f"test_import_{menu['id']}"  # 添加前缀避免冲突
            if menu['parent_id']:
                menu['parent_id'] = f"test_import_{menu['parent_id']}"

        import_request = {
            "menus": test_import_menus,
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

                    # 保存导入请求到文件
                    with open("test_import_request.json", 'w', encoding='utf-8') as f:
                        json.dump(import_request, f, ensure_ascii=False, indent=2)
                    print("   💾 Import request saved to: test_import_request.json")

                else:
                    print(f"   ❌ Failed: {result}")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

        # ===== 4. 测试其他菜单接口 =====
        print("\n4️⃣ Testing Other Menu Endpoints")
        print("-" * 50)

        # 测试获取菜单列表
        try:
            async with session.get(f"{BASE_URL}/api/v1/menus", headers=headers) as response:
                if response.status == 200:
                    menu_list = await response.json()
                    print(f"   ✅ GET /menus: {len(menu_list)} menus")
                else:
                    print(f"   ❌ GET /menus: {response.status}")
        except Exception as e:
            print(f"   💥 GET /menus: {str(e)}")

        # 测试创建单个菜单
        new_menu = {
            "id": "test_single_create",
            "name": "test_single_create",
            "title": "测试单个创建",
            "title_en": "Test Single Create",
            "path": "/test-single-create",
            "permission": "menu:test_single_create",
            "sort_order": 999
        }

        try:
            async with session.post(f"{BASE_URL}/api/v1/menus", headers=headers, json=new_menu) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ POST /menus: Created test menu")
                else:
                    print(f"   ❌ POST /menus: {response.status}")
        except Exception as e:
            print(f"   💥 POST /menus: {str(e)}")

    print("\n📊 Test Summary")
    print("=" * 60)
    print("✅ Menu import API comprehensive test completed")
    print("📋 Test scenarios:")
    print("   1. Export existing menu tree")
    print("   2. Convert to import format")
    print("   3. Test batch import with real data")
    print("   4. Test other menu endpoints")
    print()
    print("📁 Generated files:")
    print("   - converted_menus_for_import.json")
    print("   - test_import_request.json")
    print()
    print("🔗 Available endpoints:")
    print("   - POST /api/v1/menus/batch-import (批量导入)")
    print("   - GET /api/v1/menus (获取菜单列表)")
    print("   - POST /api/v1/menus (创建菜单)")
    print("   - GET /api/v1/menus/tree (菜单树)")


if __name__ == "__main__":
    asyncio.run(test_menu_import_with_existing_data())