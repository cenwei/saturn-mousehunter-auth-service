# Saturn MouseHunter - 菜单批量导入API文档

## 📋 概述

本文档描述菜单管理相关的API接口，特别是批量导入功能，供前端开发使用。

## 🔗 基础配置

- **服务地址**: `http://192.168.8.168:8005`
- **API前缀**: `/api/v1/menus`
- **认证方式**: Bearer Token (管理员权限)
- **响应格式**: JSON

---

## 1. 批量导入菜单

### **端点**
```http
POST /api/v1/menus/batch-import
```

### **描述**
批量导入菜单配置，支持全量覆盖或增量导入。

### **权限要求**
仅管理员可使用 (`user_type: ADMIN`)

### **请求参数**

#### **Headers**
```json
{
  "Authorization": "Bearer {admin_access_token}",
  "Content-Type": "application/json"
}
```

#### **Request Body**
```json
{
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
      "parent_id": null,
      "permission": "menu:dashboard",
      "menu_type": "menu",
      "sort_order": 1,
      "is_hidden": false,
      "is_external": false,
      "status": "active",
      "meta": {
        "title": "总览",
        "title_en": "Dashboard",
        "keepAlive": true
      }
    },
    {
      "id": "trading_calendar_table",
      "name": "trading_calendar_table",
      "title": "交易日历表格",
      "title_en": "Trading Calendar Table",
      "path": "/trading-calendar-table",
      "component": "TradingCalendarTable",
      "icon": null,
      "emoji": null,
      "parent_id": "trading_calendar",
      "permission": "trading_calendar:read",
      "menu_type": "menu",
      "sort_order": 1,
      "is_hidden": false,
      "is_external": false,
      "status": "active",
      "meta": {
        "title": "交易日历表格",
        "title_en": "Trading Calendar Table"
      }
    }
  ],
  "clear_existing": false
}
```

#### **字段说明**
| 字段 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| menus | array | 是 | 菜单配置列表 |
| clear_existing | boolean | 否 | 是否清除现有菜单 (默认: false) |

#### **菜单对象字段**
| 字段 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| id | string | 是 | 菜单唯一ID |
| name | string | 是 | 菜单名称 |
| title | string | 是 | 显示标题 |
| title_en | string | 否 | 英文标题 |
| path | string | 否 | 路由路径 |
| component | string | 否 | 组件名称 |
| icon | string | 否 | 图标类名 |
| emoji | string | 否 | 表情图标 |
| parent_id | string | 否 | 父菜单ID |
| permission | string | 否 | 所需权限 |
| menu_type | string | 否 | 菜单类型 (menu/button/tab) |
| sort_order | number | 否 | 排序值 (默认: 0) |
| is_hidden | boolean | 否 | 是否隐藏 (默认: false) |
| is_external | boolean | 否 | 是否外部链接 (默认: false) |
| status | string | 否 | 状态 (默认: active) |
| meta | object | 否 | 元数据 |

### **响应格式**

#### **成功响应 (200)**
```json
{
  "success": true,
  "message": "成功导入 2 个菜单",
  "data": {
    "imported_count": 2,
    "clear_existing": false
  }
}
```

#### **错误响应**
- **401 Unauthorized**: Token无效或已过期
- **403 Forbidden**: 非管理员用户无权限
- **500 Internal Server Error**: 服务器内部错误

---

## 2. 其他菜单管理接口

### **获取菜单列表**
```http
GET /api/v1/menus
```
**查询参数**:
- `parent_id` (可选): 父菜单ID
- `status` (可选): 菜单状态过滤

### **创建单个菜单**
```http
POST /api/v1/menus
```

### **更新菜单**
```http
PUT /api/v1/menus/{menu_id}
```

### **删除菜单**
```http
DELETE /api/v1/menus/{menu_id}
```

### **获取菜单树结构**
```http
GET /api/v1/menus/tree
```

### **获取单个菜单详情**
```http
GET /api/v1/menus/{menu_id}
```

---

## 🚀 使用示例

### **JavaScript/TypeScript**
```javascript
// 批量导入菜单
async function batchImportMenus(menuData, clearExisting = false) {
  const response = await fetch('/api/v1/menus/batch-import', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      menus: menuData,
      clear_existing: clearExisting
    })
  });

  if (!response.ok) {
    throw new Error(`导入失败: ${response.status}`);
  }

  return await response.json();
}

// 使用示例
const menuConfig = [
  {
    id: "dashboard",
    name: "dashboard",
    title: "总览",
    path: "/",
    permission: "menu:dashboard",
    sort_order: 1
  }
  // ... 更多菜单
];

try {
  const result = await batchImportMenus(menuConfig, false);
  console.log(`✅ 成功导入 ${result.data.imported_count} 个菜单`);
} catch (error) {
  console.error('❌ 导入失败:', error.message);
}
```

### **cURL**
```bash
# 批量导入菜单
curl -X POST "http://192.168.8.168:8005/api/v1/menus/batch-import" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "menus": [
      {
        "id": "dashboard",
        "name": "dashboard",
        "title": "总览",
        "path": "/",
        "permission": "menu:dashboard",
        "sort_order": 1
      }
    ],
    "clear_existing": false
  }'
```

---

## 📊 批量导入策略

### **增量导入 (推荐)**
```json
{
  "menus": [...],
  "clear_existing": false
}
```
- 保留现有菜单
- 新增或更新指定菜单
- 安全性高

### **全量覆盖 (谨慎使用)**
```json
{
  "menus": [...],
  "clear_existing": true
}
```
- 清除所有现有菜单
- 导入新的菜单配置
- 适用于完全重构

---

## ⚠️ 注意事项

1. **管理员权限**: 所有菜单管理操作都需要管理员权限
2. **数据验证**: 确保菜单ID唯一，父子关系正确
3. **权限映射**: permission字段需要与权限系统对应
4. **层级结构**: parent_id应引用已存在的菜单ID
5. **备份策略**: 建议在批量导入前备份现有菜单配置

---

## 📝 更新记录

- **v1.0.0** (2025-09-20): 初始版本，支持批量导入和CRUD操作