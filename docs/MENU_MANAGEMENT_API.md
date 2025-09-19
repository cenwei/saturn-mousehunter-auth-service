# Saturn MouseHunter Auth Service - 菜单管理API文档

**服务信息**
- **服务名称**: Saturn MouseHunter Auth Service
- **版本**: 1.0.0
- **描述**: 认证与菜单权限管理微服务
- **OpenAPI规范**: 3.1.0

**基础URL**: `http://192.168.8.168:8001`

## 🌳 菜单层级结构测试结果

### 📊 菜单统计概览

| 统计项 | 数值 |
|--------|------|
| **总菜单数** | 22个 |
| **根菜单数** | 8个 |
| **权限类型** | 18种 |
| **菜单层级** | 2级 (根菜单 + 子菜单) |

### 🏗️ 菜单结构树

#### 1. 🏠 仪表盘 (`dashboard`)
- **路径**: `/dashboard`
- **权限**: `menu:dashboard`
- **功能**: 系统概览、数据展示

#### 2. 👥 用户管理 (`user_management`)
- **路径**: `/users`
- **权限**: `menu:user_management`
- **子菜单**:
  - 管理员用户 (`/users/admin`, 权限: `user:read`)
  - 租户用户 (`/users/tenant`, 权限: `user:read`)

#### 3. 🔐 角色管理 (`role_management`)
- **路径**: `/roles`
- **权限**: `menu:role_management`
- **子菜单**:
  - 角色列表 (`/roles/list`, 权限: `role:read`)
  - 权限列表 (`/roles/permissions`, 权限: `role:read`)

#### 4. 📈 策略管理 (`strategy_management`)
- **路径**: `/strategy`
- **权限**: `menu:strategy`
- **子菜单**:
  - 策略列表 (`/strategy/list`, 权限: `strategy:read`)
  - 创建策略 (`/strategy/create`, 权限: `strategy:write`)

#### 5. ⚠️ 风控管理 (`risk_management`)
- **路径**: `/risk`
- **权限**: `menu:risk`
- **子菜单**:
  - 风控监控 (`/risk/monitor`, 权限: `risk:monitor`)
  - 风控规则 (`/risk/rules`, 权限: `risk:write`)

#### 6. ⚙️ 系统设置 (`system_management`)
- **路径**: `/system`
- **权限**: `menu:system`
- **子菜单**:
  - 系统配置 (`/system/config`, 权限: `system:config`)
  - 系统监控 (`/system/monitor`, 权限: `system:monitor`)

#### 7. 📊 报表中心 (`reports`)
- **路径**: `/reports`
- **权限**: `menu:reports`
- **子菜单**:
  - 用户报表 (`/reports/users`, 权限: `report:read`)
  - 策略报表 (`/reports/strategy`, 权限: `report:read`)

#### 8. 📝 审计日志 (`audit_logs`)
- **路径**: `/audit`
- **权限**: `menu:audit`
- **子菜单**:
  - 登录日志 (`/audit/login`, 权限: `audit:read`)
  - 操作日志 (`/audit/operation`, 权限: `audit:read`)

## 🔒 权限过滤测试结果

### 👑 ADMIN 用户权限
**可访问菜单**: 8个根菜单 + 14个子菜单 = **22个全部菜单**

### 🏢 TENANT 用户权限
**可访问菜单**:
- 仪表盘
- 策略管理 (仅策略列表子菜单)

**总计**: 2个根菜单 + 1个子菜单 = **3个菜单**

### 🔒 LIMITED 用户权限
**可访问菜单**:
- 仪表盘

**总计**: **1个菜单**

## 🎯 核心API端点

### 菜单管理端点

| 端点 | 方法 | 描述 | 权限要求 |
|-----|------|------|----------|
| `/api/v1/auth/user-menus` | GET | **获取用户菜单** | 已认证 |
| `/api/v1/menus/tree` | GET | 获取完整菜单树 | 管理员 |
| `/api/v1/auth/check-menu-permission` | POST | 检查菜单权限 | 已认证 |
| `/api/v1/users/{user_id}/menus` | GET | 获取指定用户菜单 | 管理员/自己 |
| `/api/v1/auth/menu-stats` | GET | 获取菜单统计 | 已认证 |

### 功能端点

| 端点 | 方法 | 描述 | 权限要求 |
|-----|------|------|----------|
| `/api/v1/dashboard/data` | GET | 获取仪表盘数据 | `menu:dashboard` |
| `/api/v1/system/config` | GET | 获取系统配置 | `menu:system` |

## 📋 响应示例

### 用户菜单响应 (`/api/v1/auth/user-menus`)
```json
{
  "user_id": "USER_123",
  "user_type": "ADMIN",
  "permissions": [
    "menu:dashboard", "menu:user_management", "user:read",
    "menu:role_management", "role:read", "menu:strategy",
    "strategy:read", "strategy:write"
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
      "meta": {"title": "仪表盘", "keepAlive": true},
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
      "meta": {"title": "用户管理"},
      "children": [
        {
          "id": "admin_users",
          "name": "admin_users",
          "title": "管理员用户",
          "path": "/users/admin",
          "permission": "user:read",
          "menu_type": "menu",
          "sort_order": 1,
          "children": []
        },
        {
          "id": "tenant_users",
          "name": "tenant_users",
          "title": "租户用户",
          "path": "/users/tenant",
          "permission": "user:read",
          "menu_type": "menu",
          "sort_order": 2,
          "children": []
        }
      ]
    }
  ],
  "updated_at": "2025-09-19T01:30:00Z"
}
```

### 菜单权限检查响应 (`/api/v1/auth/check-menu-permission`)
```json
{
  "menu_id": "dashboard",
  "permission": "menu:dashboard",
  "has_permission": true
}
```

### 菜单统计响应 (`/api/v1/auth/menu-stats`)
```json
{
  "total_menus": 22,
  "accessible_menus": 18,
  "permission_coverage": 0.82,
  "menu_usage": {
    "dashboard": 150,
    "user_management": 45,
    "strategy_management": 89
  }
}
```

## 🌐 访问地址

- **API文档**: http://192.168.8.168:8001/docs
- **完整OpenAPI规范**: http://192.168.8.168:8001/openapi.json
- **健康检查**: http://192.168.8.168:8001/health

## 📁 本地文件

- **OpenAPI规范文件**: `/saturn-mousehunter-auth-service/docs/auth_service_openapi.json`
- **Kotlin序列化类**: `/saturn-mousehunter-auth-service/docs/AuthMenuApiModels.kt`
- **菜单测试脚本**: `/saturn-mousehunter-auth-service/test_menu_tree.py`
- **菜单树形结构**: `/saturn-mousehunter-auth-service/docs/menu_tree_structure.json`

## 🔧 Kotlin Quickly客户端集成

### 关键序列化类

1. **MenuTree** - 菜单树结构
2. **UserMenuResponse** - 用户菜单响应
3. **MenuPermissionCheck** - 权限检查结果
4. **MenuStatsResponse** - 菜单统计信息

### 使用示例

```kotlin
// 获取用户菜单
val userMenus = authClient.getUserMenus(token)

// 权限过滤
val userPermissions = setOf("menu:dashboard", "menu:strategy")
val filteredMenus = MenuUtils.filterMenusByPermissions(
    userMenus.menus,
    userPermissions
)

// 检查菜单权限
val hasPermission = authClient.checkMenuPermission(token, "dashboard")
```

## 🚧 待补充功能

### 代理池管理菜单
当前菜单配置中缺少代理池管理模块，建议添加：

```json
{
  "id": "proxy_pool_management",
  "name": "proxy_pool_management",
  "title": "代理池管理",
  "path": "/proxy-pool",
  "icon": "proxy",
  "permission": "menu:proxy_pool",
  "sort_order": 4.5,
  "children": [
    {
      "id": "proxy_pool_cn",
      "title": "中国市场代理池",
      "path": "/proxy-pool/cn"
    },
    {
      "id": "proxy_pool_hk",
      "title": "香港市场代理池",
      "path": "/proxy-pool/hk"
    },
    {
      "id": "proxy_pool_us",
      "title": "美国市场代理池",
      "path": "/proxy-pool/us"
    }
  ]
}
```

---

**生成时间**: 2025-09-19
**测试状态**: ✅ 多级菜单结构测试通过，权限过滤功能正常
**Kotlin序列化**: ✅ 已生成完整的Kotlin Quickly兼容序列化类