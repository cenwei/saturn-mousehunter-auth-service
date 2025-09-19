#!/usr/bin/env python3
"""
测试菜单管理API
"""
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

BASE_URL = "http://localhost:8001"


async def test_menu_management_api():
    """测试菜单管理API"""
    print("🧪 Testing Menu Management API")
    print("=" * 60)

    # 创建HTTP会话
    async with aiohttp.ClientSession() as session:

        # 测试获取菜单树（未认证）
        print("📋 Testing Get Menu Tree (Unauthenticated):")
        async with session.get(f"{BASE_URL}/api/v1/menus/tree") as response:
            print(f"   Status: {response.status}")
            result = await response.json()
            print(f"   Response: {result}")
            print()

        # 测试用户菜单API（使用模拟TOKEN）
        print("👤 Testing User Menus API (Mocked Authentication):")
        headers = {"Authorization": "Bearer mock_token"}  # 模拟token
        async with session.get(f"{BASE_URL}/api/v1/auth/user-menus", headers=headers) as response:
            print(f"   Status: {response.status}")
            if response.status == 200:
                result = await response.json()
                print(f"   User ID: {result.get('user_id')}")
                print(f"   User Type: {result.get('user_type')}")
                print(f"   Permissions: {len(result.get('permissions', []))}")
                print(f"   Menus: {len(result.get('menus', []))}")

                # 显示前几个菜单
                menus = result.get('menus', [])
                for i, menu in enumerate(menus[:3]):
                    emoji = menu.get('emoji', '📄')
                    print(f"     {emoji} {menu.get('title')} ({menu.get('path')})")
                if len(menus) > 3:
                    print(f"     ... and {len(menus) - 3} more menus")
            else:
                result = await response.json()
                print(f"   Error: {result}")
            print()

        # 测试获取菜单列表
        print("📋 Testing Get Menus List:")
        async with session.get(f"{BASE_URL}/api/v1/menus", headers=headers) as response:
            print(f"   Status: {response.status}")
            if response.status == 200:
                result = await response.json()
                print(f"   Menus count: {len(result)}")
                # 显示前几个菜单
                for i, menu in enumerate(result[:3]):
                    emoji = menu.get('emoji', '📄')
                    print(f"     {emoji} {menu.get('title')} ({menu.get('id')})")
                if len(result) > 3:
                    print(f"     ... and {len(result) - 3} more menus")
            else:
                result = await response.json()
                print(f"   Error: {result}")
            print()

        # 测试获取特定菜单详情
        print("🔍 Testing Get Menu by ID:")
        async with session.get(f"{BASE_URL}/api/v1/menus/dashboard", headers=headers) as response:
            print(f"   Status: {response.status}")
            if response.status == 200:
                result = await response.json()
                print(f"   Menu ID: {result.get('id')}")
                print(f"   Title: {result.get('title')}")
                print(f"   Path: {result.get('path')}")
                print(f"   Permission: {result.get('permission')}")
            else:
                result = await response.json()
                print(f"   Error: {result}")
            print()

        # 测试创建菜单（需要管理员权限）
        print("➕ Testing Create Menu (Admin Required):")
        new_menu = {
            "id": "test_menu",
            "name": "test_menu",
            "title": "测试菜单",
            "title_en": "Test Menu",
            "path": "/test-menu",
            "icon": "test",
            "emoji": "🧪",
            "permission": "menu:test",
            "sort_order": 100,
            "status": "active"
        }
        async with session.post(f"{BASE_URL}/api/v1/menus",
                               json=new_menu, headers=headers) as response:
            print(f"   Status: {response.status}")
            result = await response.json()
            print(f"   Response: {result}")
            print()

        # 测试批量导入菜单
        print("📦 Testing Batch Import Menus:")
        batch_request = {
            "menus": [
                {
                    "id": "batch_menu_1",
                    "name": "batch_menu_1",
                    "title": "批量菜单1",
                    "path": "/batch-1",
                    "permission": "menu:batch1"
                },
                {
                    "id": "batch_menu_2",
                    "name": "batch_menu_2",
                    "title": "批量菜单2",
                    "path": "/batch-2",
                    "permission": "menu:batch2"
                }
            ],
            "clear_existing": False
        }
        async with session.post(f"{BASE_URL}/api/v1/menus/batch-import",
                               json=batch_request, headers=headers) as response:
            print(f"   Status: {response.status}")
            result = await response.json()
            print(f"   Response: {result}")
            print()

        # 测试健康检查
        print("❤️ Testing Health Check:")
        async with session.get(f"{BASE_URL}/health") as response:
            print(f"   Status: {response.status}")
            result = await response.json()
            print(f"   Service: {result.get('service')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Database: {result.get('database')}")
            print()


async def test_openapi_schema():
    """测试OpenAPI模式"""
    print("📋 Testing OpenAPI Schema")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/openapi.json") as response:
            if response.status == 200:
                openapi = await response.json()

                # 检查菜单管理相关的端点
                paths = openapi.get("paths", {})
                menu_paths = [path for path in paths.keys() if "/menus" in path]

                print(f"📊 OpenAPI Schema Info:")
                print(f"   Title: {openapi.get('info', {}).get('title')}")
                print(f"   Version: {openapi.get('info', {}).get('version')}")
                print(f"   Total paths: {len(paths)}")
                print(f"   Menu-related paths: {len(menu_paths)}")
                print()

                print(f"🔗 Menu Management Endpoints:")
                for path in sorted(menu_paths):
                    methods = list(paths[path].keys())
                    print(f"   {path} [{', '.join(methods)}]")
                print()

            else:
                print(f"   ❌ Failed to get OpenAPI schema: {response.status}")


async def main():
    """主函数"""
    print("🚀 Menu Management API Test Suite")
    print("=" * 70)
    print()

    try:
        await test_menu_management_api()
        await test_openapi_schema()

        print("✅ All API tests completed!")

    except Exception as e:
        print(f"❌ API test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)