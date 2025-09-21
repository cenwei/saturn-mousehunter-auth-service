# Saturn MouseHunter 菜单模块 - 最小化UI对接版本

## 📋 概述

本文档为UI前端提供最小化但完整的菜单模块API对接规范，确保接口调用准确无误。

## 🎯 核心DTO定义

### 1. 菜单项DTO (MenuItemDTO)

```typescript
interface MenuItemDTO {
  id: string;                    // 菜单唯一ID
  name: string;                  // 菜单名称
  title: string;                 // 显示标题（中文）
  title_en?: string;             // 英文标题
  path?: string;                 // 路由路径
  component?: string;            // 组件名称
  icon?: string;                 // 图标类名
  emoji?: string;                // 表情图标
  parent_id?: string;            // 父菜单ID
  permission?: string;           // 所需权限
  sort_order: number;            // 排序值
  is_hidden: boolean;            // 是否隐藏
  status: string;                // 状态: "active" | "disabled"
  meta?: Record<string, any>;    // 元数据
  children?: MenuItemDTO[];      // 子菜单
}
```

### 2. 用户菜单响应DTO (UserMenuResponseDTO)

```typescript
interface UserMenuResponseDTO {
  user_id: string;               // 用户ID
  user_type: string;             // 用户类型: "ADMIN" | "TENANT" | "LIMITED"
  permissions: string[];         // 用户权限列表
  menus: MenuItemDTO[];          // 可访问菜单树
  updated_at: string;            // 更新时间 (ISO格式)
}
```

### 3. 菜单权限检查DTO (MenuPermissionCheckDTO)

```typescript
interface MenuPermissionCheckDTO {
  menu_id: string;               // 菜单ID
  permission: string;            // 所需权限
  has_permission: boolean;       // 是否有权限
}
```

### 4. 菜单统计DTO (MenuStatsDTO)

```typescript
interface MenuStatsDTO {
  total_menus: number;           // 菜单总数
  accessible_menus: number;      // 可访问菜单数
  permission_coverage: number;   // 权限覆盖率 (0-100)
  menu_usage: Record<string, number>; // 菜单使用统计
}
```

## 🔗 API端点规范

### 基础URL
```
http://localhost:8080/api/v1
```

### 1. 获取用户菜单

```http
GET /auth/user-menus
Authorization: Bearer {token}
```

**响应体:**
```json
{
  "user_id": "USER_12345",
  "user_type": "TENANT",
  "permissions": ["menu:dashboard", "menu:trading_calendar"],
  "menus": [
    {
      "id": "dashboard",
      "name": "dashboard",
      "title": "总览",
      "title_en": "Dashboard",
      "path": "/",
      "component": "Dashboard",
      "icon": "dashboard",
      "emoji": "🏠",
      "permission": "menu:dashboard",
      "sort_order": 1,
      "is_hidden": false,
      "status": "active",
      "meta": {"keepAlive": true},
      "children": []
    }
  ],
  "updated_at": "2025-09-20T05:35:50.000Z"
}
```

### 2. 检查菜单权限

```http
POST /auth/check-menu-permission
Authorization: Bearer {token}
Content-Type: application/json

Query参数:
?menu_id=dashboard
```

**响应体:**
```json
{
  "menu_id": "dashboard",
  "permission": "menu:dashboard",
  "has_permission": true
}
```

### 3. 获取菜单统计

```http
GET /auth/menu-stats
Authorization: Bearer {token}
```

**响应体:**
```json
{
  "total_menus": 23,
  "accessible_menus": 11,
  "permission_coverage": 47.83,
  "menu_usage": {
    "dashboard": 1,
    "trading_calendar": 1,
    "proxy_pool": 0
  }
}
```

### 4. 获取完整菜单树 (仅管理员)

```http
GET /menus/tree
Authorization: Bearer {token}
```

**权限要求:** ADMIN用户

**响应体:**
```json
[
  {
    "id": "dashboard",
    "name": "dashboard",
    "title": "总览",
    "title_en": "Dashboard",
    "path": "/",
    "component": "Dashboard",
    "icon": "dashboard",
    "emoji": "🏠",
    "permission": "menu:dashboard",
    "sort_order": 1,
    "is_hidden": false,
    "status": "active",
    "meta": {"keepAlive": true},
    "children": []
  }
]
```

### 5. 获取指定用户菜单 (仅管理员)

```http
GET /users/{user_id}/menus
Authorization: Bearer {token}
```

**路径参数:**
- `user_id`: 目标用户ID

**权限要求:** ADMIN用户或查看自己的菜单

**响应体:** 同`UserMenuResponseDTO`

## 🚨 错误响应格式

```json
{
  "detail": "错误描述信息",
  "status_code": 400|401|403|404|500
}
```

**常见错误码:**
- `401`: 未认证或token过期
- `403`: 权限不足
- `404`: 菜单不存在
- `500`: 服务器内部错误

## 💡 UI集成示例

### Vue.js 集成示例

```typescript
// 菜单服务类
class MenuService {
  private baseURL = 'http://localhost:8080/api/v1';

  // 获取用户菜单
  async getUserMenus(): Promise<UserMenuResponseDTO> {
    const response = await fetch(`${this.baseURL}/auth/user-menus`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // 检查菜单权限
  async checkMenuPermission(menuId: string): Promise<MenuPermissionCheckDTO> {
    const response = await fetch(
      `${this.baseURL}/auth/check-menu-permission?menu_id=${menuId}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // 获取菜单统计
  async getMenuStats(): Promise<MenuStatsDTO> {
    const response = await fetch(`${this.baseURL}/auth/menu-stats`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }
}
```

### React Hook 示例

```typescript
// 菜单Hook
function useMenus() {
  const [menus, setMenus] = useState<MenuItemDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMenus = async () => {
      try {
        setLoading(true);
        const menuService = new MenuService();
        const response = await menuService.getUserMenus();
        setMenus(response.menus);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchMenus();
  }, []);

  return { menus, loading, error };
}
```

## 🔧 调试工具

### Curl测试命令

```bash
# 获取用户菜单
curl -X GET "http://localhost:8080/api/v1/auth/user-menus" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# 检查菜单权限
curl -X POST "http://localhost:8080/api/v1/auth/check-menu-permission?menu_id=dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# 获取菜单统计
curl -X GET "http://localhost:8080/api/v1/auth/menu-stats" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Postman环境变量

```json
{
  "base_url": "http://localhost:8080/api/v1",
  "auth_token": "{{your_jwt_token}}",
  "headers": {
    "Authorization": "Bearer {{auth_token}}",
    "Content-Type": "application/json"
  }
}
```

## 📝 注意事项

1. **认证令牌**: 所有接口都需要有效的JWT token
2. **权限检查**: ADMIN接口需要管理员权限
3. **错误处理**: 务必处理HTTP错误状态码
4. **数据格式**: 时间格式为ISO 8601标准
5. **缓存策略**: 建议缓存菜单数据5-10分钟
6. **路由守卫**: 前端路由需要检查菜单权限

## 🎯 核心菜单项ID参考

```typescript
// 系统核心菜单ID常量
const MENU_IDS = {
  DASHBOARD: 'dashboard',
  MARKET_CONFIG: 'market_config',
  TRADING_CALENDAR: 'trading_calendar',
  INSTRUMENT_POOL: 'instrument_pool',
  BENCHMARK_POOL: 'benchmark_pool',
  PROXY_POOL: 'proxy_pool',
  KLINE_MANAGEMENT: 'kline_management',
  COOKIE_MANAGEMENT: 'cookie_management',
  AUTH_SERVICE: 'auth_service',
  USER_MANAGEMENT: 'user_management',
  ROLE_MANAGEMENT: 'role_management',
  PERMISSION_MANAGEMENT: 'permission_management',
  STRATEGY_ENGINE: 'strategy_engine',
  UNIVERSE: 'universe',
  API_EXPLORER: 'api_explorer'
} as const;
```

这个最小化菜单模块确保了UI能够准确对接所有菜单相关功能，避免接口调用错误。