#!/usr/bin/env python3
"""
导出菜单树数据为JSON
"""
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

BASE_URL = "http://192.168.8.168:8001"

# 从登录获取的新Token
REAL_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfdHlwZSI6IkFETUlOIiwidXNlcl9pZCI6IkFETUlOXzAwMSIsImV4cCI6MTc1ODM2NjAxMSwiaWF0IjoxNzU4MzY0MjExLCJpc3MiOiJzYXR1cm4tbW91c2VodW50ZXItYXV0aC1zZXJ2aWNlIiwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.8fxRT0oE5sGpeiJiuE0qv39SckCpuWN4-EWAXIMRves"

async def export_menu_data():
    """导出菜单数据"""
    print("📤 Exporting Menu Tree Data")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {REAL_TOKEN}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:

        # ===== 1. 导出完整菜单树 =====
        print("🌳 Exporting Complete Menu Tree...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/menus/tree", headers=headers) as response:
                if response.status == 200:
                    menu_tree = await response.json()

                    # 保存到文件
                    output_file = "menu_tree_export.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(menu_tree, f, ensure_ascii=False, indent=2)

                    print(f"   ✅ Menu tree exported to: {output_file}")
                    print(f"   📊 Total root menus: {len(menu_tree)}")

                    # 统计子菜单数量
                    total_children = sum(len(menu.get('children', [])) for menu in menu_tree)
                    print(f"   📊 Total child menus: {total_children}")

                else:
                    print(f"   ❌ Failed to export menu tree: {response.status}")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

        # ===== 2. 导出用户菜单 =====
        print("\n👤 Exporting User Menu...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/auth/user-menus", headers=headers) as response:
                if response.status == 200:
                    user_menus = await response.json()

                    # 保存到文件
                    output_file = "user_menus_export.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(user_menus, f, ensure_ascii=False, indent=2)

                    print(f"   ✅ User menus exported to: {output_file}")
                    print(f"   👤 User: {user_menus.get('user_id')} ({user_menus.get('user_type')})")
                    print(f"   📊 Accessible menus: {len(user_menus.get('menus', []))}")
                    print(f"   🔐 Permissions: {len(user_menus.get('permissions', []))}")

                else:
                    print(f"   ❌ Failed to export user menus: {response.status}")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

        # ===== 3. 导出菜单统计 =====
        print("\n📊 Exporting Menu Stats...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/auth/menu-stats", headers=headers) as response:
                if response.status == 200:
                    menu_stats = await response.json()

                    # 保存到文件
                    output_file = "menu_stats_export.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(menu_stats, f, ensure_ascii=False, indent=2)

                    print(f"   ✅ Menu stats exported to: {output_file}")
                    print(f"   📊 Total menus: {menu_stats.get('total_menus')}")
                    print(f"   ✅ Accessible: {menu_stats.get('accessible_menus')}")

                else:
                    print(f"   ❌ Failed to export menu stats: {response.status}")

        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

    print("\n📁 Export Summary")
    print("=" * 60)
    print("Generated files:")
    print("  📄 menu_tree_export.json     - Complete menu tree structure")
    print("  📄 user_menus_export.json    - User accessible menus")
    print("  📄 menu_stats_export.json    - Menu usage statistics")


if __name__ == "__main__":
    asyncio.run(export_menu_data())