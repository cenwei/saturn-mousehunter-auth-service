#!/usr/bin/env python3
"""
测试4个核心菜单API端点
"""
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

BASE_URL = "http://192.168.8.168:8005"

# 从登录接口获取的真实Token
REAL_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfdHlwZSI6IkFETUlOIiwidXNlcl9pZCI6IkFETUlOXzAwMSIsImV4cCI6MTc1ODM2MzY3NSwiaWF0IjoxNzU4MzYxODc1LCJpc3MiOiJzYXR1cm4tbW91c2VodW50ZXItYXV0aC1zZXJ2aWNlIiwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.gz0f8LLPZkThjQySfLgZP0P2lN_redECcV8DlDu_c9Y"

async def test_core_menu_apis():
    """测试4个核心菜单API"""
    print("🧪 Testing Core Menu APIs")
    print("=" * 60)
    print(f"📡 Base URL: {BASE_URL}")
    print(f"🔐 Token: {REAL_TOKEN[:50]}...")
    print()

    headers = {
        "Authorization": f"Bearer {REAL_TOKEN}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:

        # ===== 1. 测试获取用户菜单 =====
        print("1️⃣ Testing GET /api/v1/auth/user-menus")
        print("-" * 50)
        try:
            async with session.get(f"{BASE_URL}/api/v1/auth/user-menus", headers=headers) as response:
                print(f"   Status: {response.status}")
                result = await response.json()

                if response.status == 200:
                    print(f"   ✅ User ID: {result.get('user_id')}")
                    print(f"   ✅ User Type: {result.get('user_type')}")
                    print(f"   ✅ Permissions Count: {len(result.get('permissions', []))}")
                    print(f"   ✅ Menus Count: {len(result.get('menus', []))}")
                    print(f"   ✅ Updated At: {result.get('updated_at')}")

                    # 显示前3个菜单
                    menus = result.get('menus', [])
                    if menus:
                        print("   📋 First 3 menus:")
                        for i, menu in enumerate(menus[:3]):
                            emoji = menu.get('emoji', '📄')
                            print(f"      {emoji} {menu.get('title')} -> {menu.get('path')}")
                        if len(menus) > 3:
                            print(f"      ... and {len(menus) - 3} more menus")
                else:
                    print(f"   ❌ Error: {result}")
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
        print()

        # ===== 2. 测试检查菜单权限 =====
        print("2️⃣ Testing POST /api/v1/auth/check-menu-permission")
        print("-" * 50)
        test_menu_ids = ["dashboard", "trading_calendar", "proxy_pool", "nonexistent_menu"]

        for menu_id in test_menu_ids:
            try:
                url = f"{BASE_URL}/api/v1/auth/check-menu-permission?menu_id={menu_id}"
                async with session.post(url, headers=headers) as response:
                    result = await response.json()

                    if response.status == 200:
                        has_perm = "✅" if result.get('has_permission') else "❌"
                        print(f"   {has_perm} Menu '{menu_id}': {result.get('has_permission')} (requires: {result.get('permission')})")
                    else:
                        print(f"   💥 Menu '{menu_id}': Error {response.status} - {result}")
            except Exception as e:
                print(f"   💥 Menu '{menu_id}': Exception - {str(e)}")
        print()

        # ===== 3. 测试获取菜单统计 =====
        print("3️⃣ Testing GET /api/v1/auth/menu-stats")
        print("-" * 50)
        try:
            async with session.get(f"{BASE_URL}/api/v1/auth/menu-stats", headers=headers) as response:
                print(f"   Status: {response.status}")
                result = await response.json()

                if response.status == 200:
                    print(f"   ✅ Total Menus: {result.get('total_menus')}")
                    print(f"   ✅ Accessible Menus: {result.get('accessible_menus')}")
                    print(f"   ✅ Permission Coverage: {result.get('permission_coverage', 0):.1%}")

                    usage = result.get('menu_usage', {})
                    if usage:
                        print("   📊 Menu Usage (Top 5):")
                        sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
                        for menu, count in sorted_usage[:5]:
                            print(f"      📈 {menu}: {count} times")
                else:
                    print(f"   ❌ Error: {result}")
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
        print()

        # ===== 4. 测试获取菜单树结构 =====
        print("4️⃣ Testing GET /api/v1/menus/tree (Admin Only)")
        print("-" * 50)
        try:
            async with session.get(f"{BASE_URL}/api/v1/menus/tree", headers=headers) as response:
                print(f"   Status: {response.status}")
                result = await response.json()

                if response.status == 200:
                    print(f"   ✅ Menu Tree Count: {len(result)}")

                    # 显示菜单树结构
                    if result:
                        print("   🌳 Menu Tree Structure:")
                        for menu in result[:3]:  # 只显示前3个
                            emoji = menu.get('emoji', '📄')
                            print(f"      {emoji} {menu.get('title')} (ID: {menu.get('id')})")

                            children = menu.get('children', [])
                            if children:
                                for child in children[:2]:  # 每个父菜单只显示前2个子菜单
                                    child_emoji = child.get('emoji', '📄')
                                    print(f"         └─ {child_emoji} {child.get('title')} (ID: {child.get('id')})")
                                if len(children) > 2:
                                    print(f"         └─ ... and {len(children) - 2} more children")

                        if len(result) > 3:
                            print(f"      ... and {len(result) - 3} more root menus")

                elif response.status == 403:
                    print(f"   🚫 Forbidden: {result.get('detail', 'Admin access required')}")
                else:
                    print(f"   ❌ Error: {result}")
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
        print()

        # ===== 测试总结 =====
        print("📊 Test Summary")
        print("=" * 60)
        print("✅ All 4 core menu API endpoints tested")
        print("📋 APIs tested:")
        print("   1. GET /api/v1/auth/user-menus - User accessible menus")
        print("   2. POST /api/v1/auth/check-menu-permission - Menu permission check")
        print("   3. GET /api/v1/auth/menu-stats - Menu statistics")
        print("   4. GET /api/v1/menus/tree - Complete menu tree (Admin)")
        print()
        print("💡 Note: Using real token from admin login")
        print("🔗 Token obtained from: POST /api/v1/admin/users/login")


if __name__ == "__main__":
    asyncio.run(test_core_menu_apis())