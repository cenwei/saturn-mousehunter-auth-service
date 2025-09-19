# Saturn MouseHunter 认证服务 - 权限API文档

## API 概述

本文档描述了 Saturn MouseHunter 认证服务中权限管理相关的 API 接口。

**基础URL**: `/api/v1`

**认证方式**: Bearer Token (JWT)

## 🎭 角色管理 API

### 1. 获取角色列表

```http
GET /api/v1/roles
```

**权限要求**: `role:read`

**查询参数**:
```json
{
  "role_name": "string (可选) - 角色名称模糊查询",
  "role_code": "string (可选) - 角色编码",
  "scope": "string (可选) - 角色范围 [GLOBAL, TENANT, SYSTEM]",
  "is_system_role": "boolean (可选) - 是否系统角色",
  "is_active": "boolean (可选) - 是否激活",
  "limit": "integer (可选) - 每页数量，默认20",
  "offset": "integer (可选) - 偏移量，默认0"
}
```

**响应示例**:
```json
[
  {
    "id": "ROLE_SUPER_ADMIN",
    "role_name": "超级管理员",
    "role_code": "super_admin",
    "description": "拥有所有权限的系统管理员",
    "scope": "SYSTEM",
    "is_system_role": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 2. 获取角色详情

```http
GET /api/v1/roles/{role_id}
```

**权限要求**: `role:read`

**路径参数**:
- `role_id` (string): 角色ID

**响应示例**:
```json
{
  "id": "ROLE_SUPER_ADMIN",
  "role_name": "超级管理员",
  "role_code": "super_admin",
  "description": "拥有所有权限的系统管理员",
  "scope": "SYSTEM",
  "is_system_role": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "permissions": [
    {
      "id": "PERM_USER_READ",
      "permission_name": "用户查看",
      "permission_code": "user:read",
      "resource": "user",
      "action": "read",
      "description": "查看用户信息"
    }
  ]
}
```

### 3. 创建角色

```http
POST /api/v1/roles
```

**权限要求**: `role:write`

**请求体**:
```json
{
  "role_name": "产品经理",
  "role_code": "PRODUCT_MANAGER",
  "description": "负责产品管理的角色",
  "scope": "TENANT",
  "is_system_role": false
}
```

**响应示例**:
```json
{
  "id": "ROLE_001",
  "role_name": "产品经理",
  "role_code": "PRODUCT_MANAGER",
  "description": "负责产品管理的角色",
  "scope": "TENANT",
  "is_system_role": false,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. 更新角色

```http
PUT /api/v1/roles/{role_id}
```

**权限要求**: `role:write`

**路径参数**:
- `role_id` (string): 角色ID

**请求体**:
```json
{
  "role_name": "高级产品经理",
  "description": "负责高级产品管理的角色",
  "is_active": true
}
```

### 5. 删除角色

```http
DELETE /api/v1/roles/{role_id}
```

**权限要求**: `role:write`

**路径参数**:
- `role_id` (string): 角色ID

**响应**:
```json
{
  "message": "角色删除成功"
}
```

### 6. 获取角色权限

```http
GET /api/v1/roles/{role_id}/permissions
```

**权限要求**: `role:read`

**路径参数**:
- `role_id` (string): 角色ID

**响应示例**:
```json
[
  {
    "id": "PERM_USER_READ",
    "permission_name": "用户查看",
    "permission_code": "user:read",
    "resource": "user",
    "action": "read",
    "description": "查看用户信息",
    "is_system_permission": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 7. 分配权限给角色

```http
POST /api/v1/roles/{role_id}/permissions
```

**权限要求**: `role:write`

**路径参数**:
- `role_id` (string): 角色ID

**请求体**:
```json
{
  "permission_ids": ["PERM_USER_READ", "PERM_USER_WRITE"]
}
```

### 8. 移除角色权限

```http
DELETE /api/v1/roles/{role_id}/permissions/{permission_id}
```

**权限要求**: `role:write`

**路径参数**:
- `role_id` (string): 角色ID
- `permission_id` (string): 权限ID

## 🔐 权限管理 API

### 1. 获取权限列表

```http
GET /api/v1/permissions
```

**权限要求**: `role:read`

**查询参数**:
```json
{
  "permission_name": "string (可选) - 权限名称模糊查询",
  "resource": "string (可选) - 资源名称",
  "action": "string (可选) - 操作类型",
  "is_system_permission": "boolean (可选) - 是否系统权限",
  "limit": "integer (可选) - 每页数量，默认20",
  "offset": "integer (可选) - 偏移量，默认0"
}
```

**响应示例**:
```json
[
  {
    "id": "PERM_USER_READ",
    "permission_name": "用户查看",
    "permission_code": "user:read",
    "resource": "user",
    "action": "read",
    "description": "查看用户信息",
    "is_system_permission": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 2. 获取权限详情

```http
GET /api/v1/permissions/{permission_id}
```

**权限要求**: `role:read`

**路径参数**:
- `permission_id` (string): 权限ID

### 3. 创建权限

```http
POST /api/v1/permissions
```

**权限要求**: `role:write`

**请求体**:
```json
{
  "permission_name": "产品管理",
  "permission_code": "product:write",
  "resource": "product",
  "action": "write",
  "description": "产品的创建、更新、删除权限",
  "is_system_permission": false
}
```

### 4. 更新权限

```http
PUT /api/v1/permissions/{permission_id}
```

**权限要求**: `role:write`

**请求体**:
```json
{
  "permission_name": "高级产品管理",
  "description": "产品的完整管理权限"
}
```

### 5. 删除权限

```http
DELETE /api/v1/permissions/{permission_id}
```

**权限要求**: `role:write`

## 👤 用户权限管理 API

### 1. 获取用户角色

```http
GET /api/v1/users/{user_id}/roles
```

**权限要求**: `user:read`

**路径参数**:
- `user_id` (string): 用户ID

**响应示例**:
```json
[
  {
    "id": "UR_001",
    "user_id": "ADMIN_001",
    "user_type": "ADMIN",
    "role_id": "ROLE_SUPER_ADMIN",
    "role_name": "超级管理员",
    "role_code": "super_admin",
    "granted_by": "SYSTEM",
    "granted_at": "2024-01-01T00:00:00Z",
    "expires_at": null,
    "is_active": true
  }
]
```

### 2. 分配角色给用户

```http
POST /api/v1/users/{user_id}/roles
```

**权限要求**: `user:write`

**路径参数**:
- `user_id` (string): 用户ID

**请求体**:
```json
{
  "role_ids": ["ROLE_001", "ROLE_002"],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### 3. 移除用户角色

```http
DELETE /api/v1/users/{user_id}/roles/{role_id}
```

**权限要求**: `user:write`

**路径参数**:
- `user_id` (string): 用户ID
- `role_id` (string): 角色ID

### 4. 获取用户权限

```http
GET /api/v1/users/{user_id}/permissions
```

**权限要求**: `user:read`

**路径参数**:
- `user_id` (string): 用户ID

**响应示例**:
```json
{
  "user_id": "ADMIN_001",
  "user_type": "ADMIN",
  "permissions": [
    "user:read",
    "user:write",
    "role:read",
    "role:write",
    "system:admin"
  ],
  "roles": [
    "super_admin"
  ]
}
```

## 🔍 权限验证 API

### 1. 验证Token状态

```http
POST /api/v1/auth/validate-token
```

**请求体**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "valid": true,
  "expired": false,
  "expires_at": "2024-01-01T12:00:00Z",
  "issued_at": "2024-01-01T00:00:00Z",
  "user_id": "ADMIN_001",
  "user_type": "ADMIN",
  "time_until_expiry": 3600
}
```

### 2. 获取当前用户信息

```http
GET /api/v1/auth/user-info
```

**认证**: 可选

**响应示例**:
```json
{
  "authenticated": true,
  "user": {
    "user_id": "ADMIN_001",
    "user_type": "ADMIN",
    "subject": "admin",
    "permissions": [
      "user:read",
      "user:write",
      "role:read",
      "role:write",
      "system:admin"
    ],
    "roles": [
      "super_admin"
    ],
    "expires_at": "2024-01-01T12:00:00Z"
  }
}
```

### 3. 刷新Token

```http
POST /api/v1/auth/refresh-token
```

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 📊 统计和报告 API

### 1. 获取权限统计

```http
GET /api/v1/permissions/stats
```

**权限要求**: `role:read`

**响应示例**:
```json
{
  "total_permissions": 50,
  "system_permissions": 10,
  "custom_permissions": 40,
  "by_resource": {
    "user": 5,
    "role": 5,
    "product": 10,
    "order": 15
  },
  "by_action": {
    "read": 20,
    "write": 15,
    "create": 8,
    "update": 5,
    "delete": 2
  }
}
```

### 2. 获取角色统计

```http
GET /api/v1/roles/stats
```

**权限要求**: `role:read`

**响应示例**:
```json
{
  "total_roles": 25,
  "system_roles": 5,
  "custom_roles": 20,
  "by_scope": {
    "GLOBAL": 10,
    "TENANT": 12,
    "SYSTEM": 3
  },
  "active_roles": 23,
  "inactive_roles": 2
}
```

## ❌ 错误响应

### 权限不足 (403)
```json
{
  "detail": "权限不足"
}
```

### 未认证 (401)
```json
{
  "detail": "无效的访问令牌"
}
```

### 资源不存在 (404)
```json
{
  "detail": "角色不存在"
}
```

### 请求参数错误 (400)
```json
{
  "detail": "角色编码必须为大写字母、数字和下划线组合"
}
```

### 服务器错误 (500)
```json
{
  "detail": "服务器内部错误"
}
```

## 🔐 权限要求矩阵

| API端点 | 权限要求 | 用户类型 | 备注 |
|---------|----------|----------|------|
| GET /roles | role:read | ADMIN | 查看角色列表 |
| POST /roles | role:write | ADMIN | 创建角色 |
| PUT /roles/{id} | role:write | ADMIN | 更新角色 |
| DELETE /roles/{id} | role:write | ADMIN | 删除角色 |
| GET /permissions | role:read | ADMIN | 查看权限列表 |
| POST /permissions | role:write | ADMIN | 创建权限 |
| PUT /permissions/{id} | role:write | ADMIN | 更新权限 |
| DELETE /permissions/{id} | role:write | ADMIN | 删除权限 |
| GET /users/{id}/roles | user:read | ADMIN/TENANT | 查看用户角色 |
| POST /users/{id}/roles | user:write | ADMIN | 分配用户角色 |
| DELETE /users/{id}/roles/{rid} | user:write | ADMIN | 移除用户角色 |

## 📝 使用示例

### JavaScript 示例

```javascript
// 获取角色列表
const getRoles = async () => {
  const response = await fetch('/api/v1/roles', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};

// 创建角色
const createRole = async (roleData) => {
  const response = await fetch('/api/v1/roles', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(roleData)
  });
  return response.json();
};

// 分配角色给用户
const assignRoles = async (userId, roleIds) => {
  const response = await fetch(`/api/v1/users/${userId}/roles`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ role_ids: roleIds })
  });
  return response.json();
};
```

### Python 示例

```python
import requests

class AuthAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_roles(self, **params):
        """获取角色列表"""
        response = requests.get(
            f'{self.base_url}/roles',
            headers=self.headers,
            params=params
        )
        return response.json()

    def create_role(self, role_data):
        """创建角色"""
        response = requests.post(
            f'{self.base_url}/roles',
            headers=self.headers,
            json=role_data
        )
        return response.json()

    def assign_user_roles(self, user_id, role_ids):
        """分配用户角色"""
        response = requests.post(
            f'{self.base_url}/users/{user_id}/roles',
            headers=self.headers,
            json={'role_ids': role_ids}
        )
        return response.json()
```

---

**最后更新**: 2025-09-16
**版本**: 1.0.0
**维护者**: Saturn MouseHunter Team