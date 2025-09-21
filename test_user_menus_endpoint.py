#!/usr/bin/env python3
"""
专门测试 /api/v1/auth/user-menus 接口
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://192.168.8.168:8005"

def get_admin_token():
    """获取管理员token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/users/login",
            json=login_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return result["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login exception: {str(e)}")
        return None

def test_user_menus_endpoint():
    """测试用户菜单接口"""
    print("🧪 Testing /api/v1/auth/user-menus Endpoint")
    print("=" * 60)
    print(f"📡 Base URL: {BASE_URL}")
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 获取管理员token
    print("🔐 Getting admin token...")
    token = get_admin_token()

    if not token:
        print("❌ Failed to get admin token, cannot proceed")
        return

    print(f"   ✅ Token obtained: {token[:50]}...")
    print()

    # 测试用户菜单接口
    print("📋 Testing GET /api/v1/auth/user-menus")
    print("-" * 50)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/user-menus",
            headers=headers,
            timeout=10
        )

        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()

            print(f"   ✅ Success!")
            print(f"   📊 Response Details:")
            print(f"      User ID: {result.get('user_id')}")
            print(f"      User Type: {result.get('user_type')}")
            print(f"      Permissions Count: {len(result.get('permissions', []))}")
            print(f"      Menus Count: {len(result.get('menus', []))}")
            print(f"      Updated At: {result.get('updated_at')}")

            # 显示前5个权限
            permissions = result.get('permissions', [])
            if permissions:
                print(f"   🔑 Permissions (showing first 5 of {len(permissions)}):")
                for i, perm in enumerate(permissions[:5]):
                    print(f"      {i+1}. {perm}")
                if len(permissions) > 5:
                    print(f"      ... and {len(permissions) - 5} more permissions")

            # 显示前3个菜单
            menus = result.get('menus', [])
            if menus:
                print(f"   📋 Menus (showing first 3 of {len(menus)}):")
                for i, menu in enumerate(menus[:3]):
                    emoji = menu.get('emoji', '📄')
                    title = menu.get('title', 'N/A')
                    path = menu.get('path', 'N/A')
                    children_count = len(menu.get('children', []))
                    child_info = f" ({children_count} children)" if children_count > 0 else ""
                    print(f"      {i+1}. {emoji} {title} -> {path}{child_info}")
                if len(menus) > 3:
                    print(f"      ... and {len(menus) - 3} more menus")

            # 保存完整响应到文件
            with open('user_menus_test_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"   💾 Full response saved to: user_menus_test_response.json")

        elif response.status_code == 401:
            print(f"   🚫 Unauthorized: {response.text}")
            print("   💡 Token may be expired or invalid")

        elif response.status_code == 404:
            print(f"   ❌ Not Found: {response.text}")
            print("   💡 Endpoint may not be implemented yet")

        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")

    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out (10 seconds)")

    except requests.exceptions.ConnectionError:
        print("   🔌 Connection error - service may be down")

    except Exception as e:
        print(f"   💥 Exception: {str(e)}")

    print()
    print("📊 Test Summary")
    print("=" * 60)
    print("✅ user-menus endpoint test completed")
    print(f"🔗 Tested endpoint: GET {BASE_URL}/api/v1/auth/user-menus")
    print("💡 This endpoint returns user's accessible menus based on permissions")

if __name__ == "__main__":
    test_user_menus_endpoint()