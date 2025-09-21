# Saturn MouseHunter - 菜单API核心文档

## 📋 概述

本文档描述4个核心菜单API端点的请求和响应规范，供前端客户端集成使用。

## 🔗 基础配置

- **服务地址**: `http://192.168.8.168:8005`
- **API前缀**: `/api/v1`
- **认证方式**: Bearer Token (Authorization Header)
- **响应格式**: JSON

---

## 1. 获取用户菜单

### **端点**
```http
GET /api/v1/auth/user-menus
```

### **描述**
获取当前用户可访问的菜单树，根据用户权限过滤。

### **请求参数**

#### **Headers**
```json
{
  "Authorization": "Bearer {access_token}",
  "Content-Type": "application/json"
}
```

#### **Query Parameters**
无

### **响应格式**

#### **成功响应 (200)**
```json
{
  "user_id": "USER_12345",
  "user_type": "ADMIN",
  "permissions": [
    "menu:dashboard",
    "menu:trading_calendar",
    "menu:proxy_pool",
    "trading_calendar:read",
    "trading_calendar:write"
  ],
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
      "menu_type": "menu",
      "sort_order": 1,
      "is_hidden": false,
      "status": "active",
      "meta": {
        "title": "总览",
        "title_en": "Dashboard",
        "keepAlive": true
      },
      "children": []
    },
    {
      "id": "trading_calendar",
      "name": "trading_calendar",
      "title": "交易日历管理",
      "title_en": "Trading Calendar",
      "path": "/trading-calendar",
      "component": "TradingCalendar",
      "icon": "calendar",
      "emoji": "📅",
      "permission": "menu:trading_calendar",
      "menu_type": "menu",
      "sort_order": 3,
      "is_hidden": false,
      "status": "active",
      "meta": {
        "title": "交易日历管理",
        "title_en": "Trading Calendar"
      },
      "children": [
        {
          "id": "trading_calendar_table",
          "name": "trading_calendar_table",
          "title": "交易日历表格",
          "title_en": "Trading Calendar Table",
          "path": "/trading-calendar-table",
          "component": "TradingCalendarTable",
          "permission": "trading_calendar:read",
          "menu_type": "menu",
          "sort_order": 1,
          "is_hidden": false,
          "status": "active",
          "meta": {
            "title": "交易日历表格",
            "title_en": "Trading Calendar Table"
          },
          "children": []
        }
      ]
    }
  ],
  "updated_at": "2025-09-20T17:30:00Z"
}
```

#### **错误响应**
- **401 Unauthorized**: Token无效或已过期
- **500 Internal Server Error**: 服务器内部错误

---

## 2. 检查菜单权限

### **端点**
```http
POST /api/v1/auth/check-menu-permission
```

### **描述**
检查当前用户是否有访问指定菜单的权限。

### **请求参数**

#### **Headers**
```json
{
  "Authorization": "Bearer {access_token}",
  "Content-Type": "application/json"
}
```

#### **Query Parameters**
| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| menu_id | string | 是 | 菜单ID |

#### **请求示例**
```http
POST /api/v1/auth/check-menu-permission?menu_id=trading_calendar
```

### **响应格式**

#### **成功响应 (200)**
```json
{
  "menu_id": "trading_calendar",
  "permission": "menu:trading_calendar",
  "has_permission": true
}
```

#### **错误响应**
- **400 Bad Request**: 缺少必需参数
- **401 Unauthorized**: Token无效或已过期
- **500 Internal Server Error**: 服务器内部错误

---

## 3. 获取菜单统计

### **端点**
```http
GET /api/v1/auth/menu-stats
```

### **描述**
获取当前用户的菜单访问统计信息。

### **请求参数**

#### **Headers**
```json
{
  "Authorization": "Bearer {access_token}",
  "Content-Type": "application/json"
}
```

#### **Query Parameters**
无

### **响应格式**

#### **成功响应 (200)**
```json
{
  "total_menus": 15,
  "accessible_menus": 12,
  "permission_coverage": 0.8,
  "menu_usage": {
    "dashboard": 156,
    "trading_calendar": 89,
    "proxy_pool": 45,
    "instrument_pool": 67,
    "benchmark_pool": 23
  }
}
```

#### **字段说明**
| 字段 | 类型 | 描述 |
|-----|------|------|
| total_menus | number | 系统菜单总数 |
| accessible_menus | number | 用户可访问的菜单数 |
| permission_coverage | number | 权限覆盖率 (0-1) |
| menu_usage | object | 菜单使用次数统计 |

#### **错误响应**
- **401 Unauthorized**: Token无效或已过期
- **500 Internal Server Error**: 服务器内部错误

---

## 4. 获取菜单树结构

### **端点**
```http
GET /api/v1/menus/tree
```

### **描述**
获取完整的菜单树结构，仅管理员可访问。

### **请求参数**

#### **Headers**
```json
{
  "Authorization": "Bearer {access_token}",
  "Content-Type": "application/json"
}
```

#### **Query Parameters**
无

### **响应格式**

#### **成功响应 (200)**
```json
[
  {
    "id": "dashboard",
    "name": "dashboard",
    "title": "总览",
    "title_en": "Dashboard",
    "path": "/",
    "icon": "dashboard",
    "emoji": "🏠",
    "permission": "menu:dashboard",
    "menu_type": "menu",
    "sort_order": 1,
    "is_hidden": false,
    "status": "active",
    "meta": {
      "title": "总览",
      "title_en": "Dashboard",
      "keepAlive": true
    },
    "children": []
  },
  {
    "id": "trading_calendar",
    "name": "trading_calendar",
    "title": "交易日历管理",
    "title_en": "Trading Calendar",
    "path": "/trading-calendar",
    "icon": "calendar",
    "emoji": "📅",
    "permission": "menu:trading_calendar",
    "menu_type": "menu",
    "sort_order": 3,
    "is_hidden": false,
    "status": "active",
    "meta": {
      "title": "交易日历管理",
      "title_en": "Trading Calendar"
    },
    "children": [
      {
        "id": "trading_calendar_table",
        "name": "trading_calendar_table",
        "title": "交易日历表格",
        "title_en": "Trading Calendar Table",
        "path": "/trading-calendar-table",
        "permission": "trading_calendar:read",
        "menu_type": "menu",
        "sort_order": 1,
        "is_hidden": false,
        "status": "active",
        "meta": {
          "title": "交易日历表格",
          "title_en": "Trading Calendar Table"
        },
        "children": []
      }
    ]
  }
]
```

#### **错误响应**
- **401 Unauthorized**: Token无效或已过期
- **403 Forbidden**: 非管理员用户无权限
- **500 Internal Server Error**: 服务器内部错误

---

## 📊 数据类型定义

### **MenuTree对象**
```typescript
interface MenuTree {
  id: string;                    // 菜单唯一ID
  name: string;                  // 菜单名称
  title: string;                 // 显示标题
  title_en?: string;             // 英文标题
  path?: string;                 // 路由路径
  component?: string;            // 组件名称
  icon?: string;                 // 图标类名
  emoji?: string;                // 表情图标
  permission?: string;           // 所需权限
  menu_type: "menu" | "button" | "tab";  // 菜单类型
  sort_order: number;            // 排序值
  is_hidden: boolean;            // 是否隐藏
  status: string;                // 状态
  meta?: Record<string, any>;    // 元数据
  children: MenuTree[];          // 子菜单
}
```

### **UserMenuResponse对象**
```typescript
interface UserMenuResponse {
  user_id: string;               // 用户ID
  user_type: string;             // 用户类型 (ADMIN/TENANT)
  permissions: string[];         // 用户权限列表
  menus: MenuTree[];             // 可访问菜单树
  updated_at: string;            // 更新时间 (ISO格式)
}
```

### **MenuPermissionCheck对象**
```typescript
interface MenuPermissionCheck {
  menu_id: string;               // 菜单ID
  permission: string;            // 所需权限
  has_permission: boolean;       // 是否有权限
}
```

### **MenuStatsResponse对象**
```typescript
interface MenuStatsResponse {
  total_menus: number;           // 菜单总数
  accessible_menus: number;      // 可访问菜单数
  permission_coverage: number;   // 权限覆盖率 (0-1)
  menu_usage: Record<string, number>; // 菜单使用统计
}
```

---

## 🚀 使用示例

### **JavaScript/TypeScript**
```javascript
// 获取用户菜单
const response = await fetch('/api/v1/auth/user-menus', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const userMenus = await response.json();

// 检查菜单权限
const permissionCheck = await fetch('/api/v1/auth/check-menu-permission?menu_id=dashboard', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const hasPermission = await permissionCheck.json();
```

### **cURL**
```bash
# 获取用户菜单
curl -X GET "http://192.168.8.168:8001/api/v1/auth/user-menus" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 检查菜单权限
curl -X POST "http://192.168.8.168:8001/api/v1/auth/check-menu-permission?menu_id=dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ⚠️ 注意事项

1. **认证必需**: 所有API都需要有效的Bearer Token
2. **权限控制**: 根据用户类型和权限返回不同的菜单
3. **缓存策略**: 菜单数据建议在客户端缓存，减少请求频率
4. **错误处理**: 客户端需要妥善处理认证失败和权限不足的情况
5. **数据格式**: 所有时间字段使用ISO 8601格式

---

## 📝 更新记录

- **v1.0.0** (2025-09-20): 初始版本，包含4个核心API端点