#!/usr/bin/env python3
"""
菜单权限API使用示例
Saturn MouseHunter 认证服务

本脚本展示如何使用菜单权限相关的API
"""

# 示例1: 获取用户菜单的curl命令
print("=== 菜单权限API使用示例 ===\n")

print("1. 获取当前用户可访问菜单")
print("curl -X GET 'http://localhost:8000/api/v1/auth/user-menus' \\")
print("     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
print("     -H 'Content-Type: application/json'")
print()

print("2. 检查特定菜单权限")
print("curl -X POST 'http://localhost:8000/api/v1/auth/check-menu-permission?menu_id=dashboard' \\")
print("     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
print("     -H 'Content-Type: application/json'")
print()

print("3. 获取菜单统计信息")
print("curl -X GET 'http://localhost:8000/api/v1/auth/menu-stats' \\")
print("     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
print("     -H 'Content-Type: application/json'")
print()

print("4. 获取完整菜单树（管理员）")
print("curl -X GET 'http://localhost:8000/api/v1/menus/tree' \\")
print("     -H 'Authorization: Bearer ADMIN_JWT_TOKEN' \\")
print("     -H 'Content-Type: application/json'")
print()

print("5. 访问需要菜单权限的API")
print("curl -X GET 'http://localhost:8000/api/v1/dashboard/data' \\")
print("     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
print("     -H 'Content-Type: application/json'")
print()

# 示例2: 前端JavaScript集成示例
print("=== 前端集成示例 ===\n")

js_code = '''
// JavaScript前端集成示例
class MenuPermissionClient {
    constructor(apiBaseUrl, token) {
        this.apiBaseUrl = apiBaseUrl;
        this.token = token;
    }

    // 获取用户菜单
    async getUserMenus() {
        const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/user-menus`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        });
        return response.json();
    }

    // 检查菜单权限
    async checkMenuPermission(menuId) {
        const response = await fetch(
            `${this.apiBaseUrl}/api/v1/auth/check-menu-permission?menu_id=${menuId}`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        const result = await response.json();
        return result.has_permission;
    }

    // 动态渲染菜单
    renderMenus(menus, container) {
        const menuHtml = menus.map(menu => `
            <div class="menu-item" data-menu-id="${menu.id}">
                <a href="${menu.path}" class="menu-link">
                    <i class="icon ${menu.icon}"></i>
                    <span>${menu.title}</span>
                </a>
                ${menu.children && menu.children.length > 0 ?
                    `<div class="submenu">${this.renderMenus(menu.children)}</div>` :
                    ''
                }
            </div>
        `).join('');

        container.innerHTML = menuHtml;
    }

    // 路由守卫
    async routeGuard(path) {
        // 根据路径找到对应的菜单权限
        const menuMap = {
            '/dashboard': 'dashboard',
            '/users': 'user_management',
            '/roles': 'role_management',
            '/system': 'system_management'
        };

        const menuId = menuMap[path];
        if (!menuId) return true; // 没有权限要求的路由

        return await this.checkMenuPermission(menuId);
    }
}

// 使用示例
const client = new MenuPermissionClient('http://localhost:8000', 'your-jwt-token');

// 初始化菜单
client.getUserMenus().then(response => {
    const menuContainer = document.getElementById('menu-container');
    client.renderMenus(response.menus, menuContainer);
});

// 路由守卫使用
router.beforeEach(async (to, from, next) => {
    const hasPermission = await client.routeGuard(to.path);
    if (hasPermission) {
        next();
    } else {
        next('/403'); // 跳转到无权限页面
    }
});
'''

print(js_code)
print()

# 示例3: Python客户端示例
print("=== Python客户端示例 ===\n")

python_code = '''
import requests
from typing import Dict, List, Any

class MenuPermissionClient:
    """菜单权限客户端"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
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

    def print_user_menus(self):
        """打印用户菜单结构"""
        menus_data = self.get_user_menus()
        print(f"用户 {menus_data['user_id']} 的菜单:")
        print(f"用户类型: {menus_data['user_type']}")
        print(f"权限数量: {len(menus_data['permissions'])}")
        print("可访问菜单:")

        def print_menu_tree(menus: List[Dict], level: int = 0):
            for menu in menus:
                indent = "  " * level
                print(f"{indent}- {menu['title']} ({menu['id']})")
                if menu.get('children'):
                    print_menu_tree(menu['children'], level + 1)

        print_menu_tree(menus_data['menus'])

# 使用示例
if __name__ == "__main__":
    client = MenuPermissionClient('http://localhost:8000', 'your-jwt-token')

    # 获取并打印用户菜单
    client.print_user_menus()

    # 检查特定菜单权限
    has_dashboard = client.check_menu_permission('dashboard')
    print(f"\\n仪表盘访问权限: {has_dashboard}")

    # 获取菜单统计
    stats = client.get_menu_stats()
    print(f"\\n菜单统计:")
    print(f"总菜单数: {stats['total_menus']}")
    print(f"可访问数: {stats['accessible_menus']}")
    print(f"覆盖率: {stats['permission_coverage']}%")
'''

print(python_code)
print()

print("=== 部署说明 ===")
print("1. 确保数据库已初始化:")
print("   - 运行 src/complete_auth_init.sql")
print("   - 或运行 src/grant_admin_permissions.sql")
print()
print("2. 启动认证服务:")
print("   - cd src/")
print("   - python main.py")
print()
print("3. 访问API文档:")
print("   - http://localhost:8000/docs")
print()
print("4. 测试健康检查:")
print("   - curl http://localhost:8000/health")
print()

print("✅ 菜单权限功能实现完成!")
print("📖 查看完整API文档: docs/PERMISSION_API.md")
print("🔧 参考权限配置: docs/PERMISSION_QUICK_REFERENCE.md")