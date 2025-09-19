# Saturn MouseHunter 认证服务 - 菜单权限API文档

## API 概述

本文档描述了 Saturn MouseHunter 认证服务中菜单权限管理相关的 API 接口。

**基础URL**: `/api/v1`

**认证方式**: Bearer Token (JWT)

## 🍽️ 菜单权限 API

### 1. 获取当前用户可访问菜单

```http
GET /api/v1/auth/user-menus
```

**权限要求**: 已认证用户

**请求头**:
```http
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**响应示例**:
```json
{
  "user_id": "ADMIN_001",
  "user_type": "ADMIN",
  "permissions": [
    "menu:dashboard",
    "menu:user_management",
    "user:read",
    "user:write",
    "menu:role_management",
    "role:read",
    "role:write"
  ],
  "menus": [
    {
      "id": "dashboard",
      "name": "dashboard",
      "title": "仪表盘",
      "path": "/dashboard",
      "icon": "dashboard",
      "permission": "menu:dashboard",
      "menu_type": "menu",
      "sort_order": 1,
      "is_hidden": false,
      "meta": {
        "title": "仪表盘",
        "keepAlive": true
      },
      "children": []
    },
    {
      "id": "user_management",
      "name": "user_management",
      "title": "用户管理",
      "path": "/users",
      "icon": "users",
      "permission": "menu:user_management",
      "menu_type": "menu",
      "sort_order": 2,
      "is_hidden": false,
      "meta": {
        "title": "用户管理"
      },
      "children": [
        {
          "id": "admin_users",
          "name": "admin_users",
          "title": "管理员用户",
          "path": "/users/admin",
          "permission": "user:read",
          "menu_type": "menu",
          "sort_order": 1,
          "is_hidden": false,
          "meta": {
            "title": "管理员用户"
          },
          "children": []
        }
      ]
    }
  ],
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### 2. 检查用户菜单权限

```http
POST /api/v1/auth/check-menu-permission
```

**权限要求**: 已认证用户

**查询参数**:
- `menu_id` (string, required): 菜单ID

**请求示例**:
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/check-menu-permission?menu_id=dashboard' \
     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
     -H 'Content-Type: application/json'
```

**响应示例**:
```json
{
  "menu_id": "dashboard",
  "permission": "menu:dashboard",
  "has_permission": true
}
```

### 3. 获取用户菜单统计信息

```http
GET /api/v1/auth/menu-stats
```

**权限要求**: 已认证用户

**响应示例**:
```json
{
  "total_menus": 15,
  "accessible_menus": 12,
  "permission_coverage": 80.0,
  "menu_usage": {
    "dashboard": 1,
    "user_management": 1,
    "role_management": 1,
    "strategy_management": 1,
    "risk_management": 0,
    "system_management": 0,
    "reports": 1,
    "audit_logs": 0
  }
}
```

### 4. 获取完整菜单树（管理员专用）

```http
GET /api/v1/menus/tree
```

**权限要求**: 管理员用户 (user_type: ADMIN)

**响应示例**:
```json
[
  {
    "id": "dashboard",
    "name": "dashboard",
    "title": "仪表盘",
    "path": "/dashboard",
    "icon": "dashboard",
    "permission": "menu:dashboard",
    "menu_type": "menu",
    "sort_order": 1,
    "is_hidden": false,
    "meta": {
      "title": "仪表盘"
    },
    "children": []
  },
  {
    "id": "user_management",
    "name": "user_management",
    "title": "用户管理",
    "path": "/users",
    "icon": "users",
    "permission": "menu:user_management",
    "menu_type": "menu",
    "sort_order": 2,
    "is_hidden": false,
    "children": [
      {
        "id": "admin_users",
        "name": "admin_users",
        "title": "管理员用户",
        "path": "/users/admin",
        "permission": "user:read",
        "sort_order": 1,
        "children": []
      }
    ]
  }
]
```

### 5. 获取指定用户的菜单

```http
GET /api/v1/users/{user_id}/menus
```

**权限要求**: 管理员用户或查看自己的菜单

**路径参数**:
- `user_id` (string): 目标用户ID

**响应格式**: 与 `/auth/user-menus` 相同

## 🎯 权限保护的示例API

### 1. 仪表盘数据（需要仪表盘菜单权限）

```http
GET /api/v1/dashboard/data
```

**权限要求**: `menu:dashboard`

**响应示例**:
```json
{
  "user_count": 150,
  "active_strategies": 25,
  "risk_alerts": 3,
  "system_health": "good",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### 2. 系统配置（需要系统菜单权限）

```http
GET /api/v1/system/config
```

**权限要求**: `menu:system`

**响应示例**:
```json
{
  "app_name": "Saturn MouseHunter",
  "version": "1.0.0",
  "features": {
    "multi_tenant": true,
    "rbac": true,
    "audit_log": true
  },
  "limits": {
    "max_users": 1000,
    "max_strategies": 100
  }
}
```

## 🔧 前端集成指南

### JavaScript客户端示例

```javascript
class MenuPermissionClient {
    constructor(apiBaseUrl, token) {
        this.apiBaseUrl = apiBaseUrl;
        this.token = token;
        this.headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    // 获取用户菜单
    async getUserMenus() {
        const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/user-menus`, {
            headers: this.headers
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    // 检查菜单权限
    async checkMenuPermission(menuId) {
        const response = await fetch(
            `${this.apiBaseUrl}/api/v1/auth/check-menu-permission?menu_id=${menuId}`,
            {
                method: 'POST',
                headers: this.headers
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        return result.has_permission;
    }

    // 获取菜单统计
    async getMenuStats() {
        const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/menu-stats`, {
            headers: this.headers
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    // 动态渲染菜单
    renderMenus(menus, container) {
        const menuHtml = menus.map(menu => {
            const childrenHtml = menu.children && menu.children.length > 0
                ? `<ul class="submenu">${this.renderMenus(menu.children).join('')}</ul>`
                : '';

            return `
                <li class="menu-item" data-menu-id="${menu.id}">
                    <a href="${menu.path || '#'}" class="menu-link">
                        <i class="icon ${menu.icon || 'default'}"></i>
                        <span class="menu-title">${menu.title}</span>
                    </a>
                    ${childrenHtml}
                </li>
            `;
        }).join('');

        if (container) {
            container.innerHTML = `<ul class="menu-list">${menuHtml}</ul>`;
        }

        return menuHtml;
    }

    // 路由守卫
    async routeGuard(path) {
        // 菜单路径映射
        const pathMenuMap = {
            '/dashboard': 'dashboard',
            '/users': 'user_management',
            '/users/admin': 'admin_users',
            '/users/tenant': 'tenant_users',
            '/roles': 'role_management',
            '/strategy': 'strategy_management',
            '/risk': 'risk_management',
            '/system': 'system_management',
            '/reports': 'reports',
            '/audit': 'audit_logs'
        };

        const menuId = pathMenuMap[path];
        if (!menuId) {
            return true; // 没有权限要求的路由
        }

        try {
            return await this.checkMenuPermission(menuId);
        } catch (error) {
            console.error('Route guard error:', error);
            return false;
        }
    }
}

// 使用示例
const menuClient = new MenuPermissionClient('http://localhost:8000', 'your-jwt-token');

// 初始化应用菜单
async function initializeMenus() {
    try {
        const menuData = await menuClient.getUserMenus();
        const menuContainer = document.getElementById('sidebar-menu');
        menuClient.renderMenus(menuData.menus, menuContainer);

        console.log(`用户 ${menuData.user_id} 加载了 ${menuData.menus.length} 个菜单`);
    } catch (error) {
        console.error('Failed to initialize menus:', error);
    }
}

// Vue.js 路由守卫集成
router.beforeEach(async (to, from, next) => {
    try {
        const hasPermission = await menuClient.routeGuard(to.path);
        if (hasPermission) {
            next();
        } else {
            next('/403'); // 跳转到无权限页面
        }
    } catch (error) {
        console.error('Route guard failed:', error);
        next('/error');
    }
});
```

### React集成示例

```jsx
import React, { useState, useEffect } from 'react';

const MenuComponent = ({ token }) => {
    const [menus, setMenus] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchMenus = async () => {
            try {
                const response = await fetch('/api/v1/auth/user-menus', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();
                setMenus(data.menus);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchMenus();
    }, [token]);

    const renderMenuItem = (menu) => (
        <li key={menu.id} className="menu-item">
            <a href={menu.path} className="menu-link">
                <i className={`icon ${menu.icon}`}></i>
                <span>{menu.title}</span>
            </a>
            {menu.children && menu.children.length > 0 && (
                <ul className="submenu">
                    {menu.children.map(renderMenuItem)}
                </ul>
            )}
        </li>
    );

    if (loading) return <div>Loading menus...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <nav className="sidebar">
            <ul className="menu-list">
                {menus.map(renderMenuItem)}
            </ul>
        </nav>
    );
};

export default MenuComponent;
```

### Python客户端示例

```python
import requests
from typing import Dict, List, Any, Optional

class MenuPermissionClient:
    """菜单权限Python客户端"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_user_menus(self) -> Dict[str, Any]:
        """获取用户菜单"""
        response = requests.get(
            f'{self.base_url}/api/v1/auth/user-menus',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def check_menu_permission(self, menu_id: str) -> bool:
        """检查菜单权限"""
        response = requests.post(
            f'{self.base_url}/api/v1/auth/check-menu-permission',
            params={'menu_id': menu_id},
            headers=self.headers
        )
        response.raise_for_status()
        result = response.json()
        return result['has_permission']

    def get_menu_stats(self) -> Dict[str, Any]:
        """获取菜单统计"""
        response = requests.get(
            f'{self.base_url}/api/v1/auth/menu-stats',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_menu_tree(self) -> List[Dict[str, Any]]:
        """获取完整菜单树（管理员）"""
        response = requests.get(
            f'{self.base_url}/api/v1/menus/tree',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def print_user_menus(self):
        """打印用户菜单结构"""
        try:
            menus_data = self.get_user_menus()
            print(f"用户 {menus_data['user_id']} 的菜单:")
            print(f"用户类型: {menus_data['user_type']}")
            print(f"权限数量: {len(menus_data['permissions'])}")
            print("可访问菜单:")

            def print_menu_tree(menus: List[Dict], level: int = 0):
                for menu in menus:
                    indent = "  " * level
                    path = menu.get('path', 'N/A')
                    permission = menu.get('permission', 'None')
                    print(f"{indent}- {menu['title']} ({menu['id']})")
                    print(f"{indent}  路径: {path}, 权限: {permission}")

                    if menu.get('children'):
                        print_menu_tree(menu['children'], level + 1)

            print_menu_tree(menus_data['menus'])

        except requests.RequestException as e:
            print(f"获取菜单失败: {e}")

    def validate_permissions(self, required_menus: List[str]) -> Dict[str, bool]:
        """批量验证菜单权限"""
        results = {}
        for menu_id in required_menus:
            try:
                results[menu_id] = self.check_menu_permission(menu_id)
            except requests.RequestException:
                results[menu_id] = False
        return results

# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = MenuPermissionClient('http://localhost:8000', 'your-jwt-token')

    # 获取并打印用户菜单
    client.print_user_menus()

    # 检查特定菜单权限
    menus_to_check = ['dashboard', 'user_management', 'system_management']
    permissions = client.validate_permissions(menus_to_check)

    print("\n权限检查结果:")
    for menu_id, has_permission in permissions.items():
        status = "✅" if has_permission else "❌"
        print(f"  {status} {menu_id}: {has_permission}")

    # 获取菜单统计
    try:
        stats = client.get_menu_stats()
        print(f"\n菜单统计:")
        print(f"总菜单数: {stats['total_menus']}")
        print(f"可访问数: {stats['accessible_menus']}")
        print(f"覆盖率: {stats['permission_coverage']}%")
    except requests.RequestException as e:
        print(f"获取统计失败: {e}")
```

## ❌ 错误响应

### 401 未认证
```json
{
  "detail": "无效的访问令牌"
}
```

### 403 权限不足
```json
{
  "detail": "缺少菜单访问权限: menu:system"
}
```

### 404 菜单不存在
```json
{
  "detail": "菜单不存在"
}
```

### 500 服务器错误
```json
{
  "detail": "获取用户菜单失败: 数据库连接错误"
}
```

## 🔐 权限要求矩阵

| API端点 | 权限要求 | 用户类型 | 备注 |
|---------|----------|----------|------|
| GET /auth/user-menus | 已认证 | ALL | 获取自己的菜单 |
| POST /auth/check-menu-permission | 已认证 | ALL | 检查菜单权限 |
| GET /auth/menu-stats | 已认证 | ALL | 菜单统计信息 |
| GET /menus/tree | 已认证 | ADMIN | 管理员专用 |
| GET /users/{id}/menus | user:read | ADMIN | 查看他人菜单 |
| GET /dashboard/data | menu:dashboard | ALL | 仪表盘数据 |
| GET /system/config | menu:system | ADMIN | 系统配置 |

## 📝 开发调试

### 使用curl测试

```bash
# 设置token变量
export TOKEN="your-jwt-token-here"

# 获取用户菜单
curl -X GET "http://localhost:8000/api/v1/auth/user-menus" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" | jq

# 检查菜单权限
curl -X POST "http://localhost:8000/api/v1/auth/check-menu-permission?menu_id=dashboard" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" | jq

# 获取菜单统计
curl -X GET "http://localhost:8000/api/v1/auth/menu-stats" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" | jq
```

### 常见问题排查

1. **菜单不显示**
   - 检查用户权限是否包含菜单权限
   - 验证菜单配置是否正确
   - 确认权限继承逻辑是否正常

2. **权限验证失败**
   - 确认JWT token有效性
   - 检查用户角色权限分配
   - 验证权限编码是否匹配

3. **子菜单显示异常**
   - 检查父子菜单权限关系
   - 验证权限继承算法
   - 确认菜单排序设置

---

**最后更新**: 2025-09-16
**版本**: 1.0.0
**维护者**: Saturn MouseHunter Team