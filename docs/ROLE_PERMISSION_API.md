# 角色权限管理 API 文档

## 概述

本文档描述了 Saturn MouseHunter 认证服务中角色权限管理的 FastAPI 接口，用于前端开发集成。

**基础URL**: `http://192.168.8.168:8001/api/v1`

**认证方式**: Bearer Token (JWT)
- 所有接口都需要在 Header 中携带 `Authorization: Bearer {access_token}`
- 需要管理员权限才能访问

## 角色管理 API

### 1. 获取角色列表

**接口**: `GET /admin/roles/`

**描述**: 获取系统中所有角色的列表，支持分页和筛选

**请求参数**:
```typescript
interface RoleQuery {
  role_name?: string;      // 角色名称模糊查询 (可选)
  is_active?: boolean;     // 是否激活 (可选)
  is_superuser?: boolean;  // 是否超级用户 (可选)
  limit?: number;          // 每页数量，默认20，范围1-100 (可选)
  offset?: number;         // 偏移量，默认0 (可选)
}
```

**返回数据**:
```typescript
interface RoleOut {
  id: string;                    // 角色ID
  role_name: string;            // 角色名称
  role_code: string;            // 角色编码
  description?: string;         // 角色描述
  scope: "GLOBAL" | "TENANT" | "SYSTEM";  // 角色范围
  is_system_role: boolean;      // 是否系统角色
  is_active: boolean;           // 是否激活
  created_at: string;           // 创建时间 (ISO格式)
  updated_at: string;           // 更新时间 (ISO格式)
}

// 返回: RoleOut[]
```

**示例响应**:
```json
[
  {
    "id": "ROLE_SUPER_ADMIN",
    "role_name": "超级管理员",
    "role_code": "SUPER_ADMIN",
    "description": "系统超级管理员",
    "scope": "GLOBAL",
    "is_system_role": true,
    "is_active": true,
    "created_at": "2025-09-15T12:22:25.643852Z",
    "updated_at": "2025-09-15T12:22:25.643852Z"
  }
]
```

### 2. 创建角色

**接口**: `POST /admin/roles/`

**描述**: 创建新的角色

**请求体**:
```typescript
interface RoleIn {
  role_name: string;            // 角色名称 (必填，2-100字符)
  role_code: string;            // 角色编码 (必填，2-50字符，大写字母数字下划线)
  description?: string;         // 角色描述 (可选)
  scope?: "GLOBAL" | "TENANT" | "SYSTEM";  // 角色范围，默认GLOBAL
  is_system_role?: boolean;     // 是否系统角色，默认false
  is_active?: boolean;          // 是否激活，默认true
}
```

**返回数据**: `RoleOut`

**示例请求**:
```json
{
  "role_name": "测试角色",
  "role_code": "TEST_ROLE",
  "description": "这是一个测试角色",
  "scope": "GLOBAL",
  "is_system_role": false,
  "is_active": true
}
```

### 3. 获取角色详情

**接口**: `GET /admin/roles/{role_id}`

**描述**: 根据角色ID获取角色详细信息

**路径参数**:
- `role_id` (string): 角色ID

**返回数据**: `RoleOut`

### 4. 获取角色及其权限

**接口**: `GET /admin/roles/{role_id}/permissions`

**描述**: 获取角色及其关联的所有权限

**路径参数**:
- `role_id` (string): 角色ID

**返回数据**:
```typescript
interface RoleWithPermissions extends RoleOut {
  permissions: PermissionOut[];  // 角色拥有的权限列表
}
```

### 5. 更新角色

**接口**: `PUT /admin/roles/{role_id}`

**描述**: 更新角色信息

**路径参数**:
- `role_id` (string): 角色ID

**请求体**:
```typescript
interface RoleUpdate {
  role_name?: string;           // 角色名称 (可选，2-100字符)
  description?: string;         // 角色描述 (可选)
  scope?: "GLOBAL" | "TENANT" | "SYSTEM";  // 角色范围 (可选)
  is_active?: boolean;          // 是否激活 (可选)
}
```

**返回数据**: `RoleOut`

**注意**: 系统角色只能修改描述和激活状态

### 6. 删除角色

**接口**: `DELETE /admin/roles/{role_id}`

**描述**: 删除角色（软删除）

**路径参数**:
- `role_id` (string): 角色ID

**返回数据**:
```typescript
{
  message: string;  // "角色删除成功"
}
```

**注意**: 系统角色不能删除

### 7. 获取系统角色列表

**接口**: `GET /admin/roles/system`

**描述**: 获取所有系统角色

**返回数据**: `RoleOut[]`

### 8. 获取角色总数

**接口**: `GET /admin/roles/count`

**描述**: 获取符合条件的角色总数

**请求参数**: 同角色列表接口的查询参数

**返回数据**:
```typescript
{
  count: number;  // 角色总数
}
```

## 权限管理 API

### 1. 获取权限列表

**接口**: `GET /admin/permissions/`

**描述**: 获取系统中所有权限的列表，支持分页和筛选

**请求参数**:
```typescript
interface PermissionQuery {
  permission_name?: string;     // 权限名称模糊查询 (可选)
  resource?: string;            // 资源名称 (可选)
  action?: string;              // 操作类型 (可选)
  is_system_permission?: boolean;  // 是否系统权限 (可选)
  limit?: number;               // 每页数量，默认20，范围1-100 (可选)
  offset?: number;              // 偏移量，默认0 (可选)
}
```

**返回数据**:
```typescript
interface PermissionOut {
  id: string;                   // 权限ID
  permission_name: string;      // 权限名称
  permission_code: string;      // 权限编码 (格式: resource:action)
  resource: string;             // 资源名称
  action: string;               // 操作类型
  description?: string;         // 权限描述
  is_system_permission: boolean; // 是否系统权限
  created_at: string;           // 创建时间 (ISO格式)
  updated_at: string;           // 更新时间 (ISO格式)
}

// 返回: PermissionOut[]
```

### 2. 创建权限

**接口**: `POST /admin/permissions/`

**描述**: 创建新的权限

**请求体**:
```typescript
interface PermissionIn {
  permission_name: string;      // 权限名称 (必填，2-100字符)
  permission_code: string;      // 权限编码 (必填，格式: resource:action)
  resource: string;             // 资源名称 (必填，2-100字符)
  action: string;               // 操作类型 (必填，2-50字符)
  description?: string;         // 权限描述 (可选)
  is_system_permission?: boolean; // 是否系统权限，默认false
}
```

**返回数据**: `PermissionOut`

**操作类型枚举**:
- `create` - 创建
- `read` - 读取
- `update` - 更新
- `delete` - 删除
- `write` - 写入
- `execute` - 执行
- `manage` - 管理

**示例请求**:
```json
{
  "permission_name": "测试权限",
  "permission_code": "test:read",
  "resource": "test",
  "action": "read",
  "description": "这是一个测试权限",
  "is_system_permission": false
}
```

### 3. 获取权限详情

**接口**: `GET /admin/permissions/{permission_id}`

**描述**: 根据权限ID获取权限详细信息

**路径参数**:
- `permission_id` (string): 权限ID

**返回数据**: `PermissionOut`

### 4. 更新权限

**接口**: `PUT /admin/permissions/{permission_id}`

**描述**: 更新权限信息

**路径参数**:
- `permission_id` (string): 权限ID

**请求体**:
```typescript
interface PermissionUpdate {
  permission_name?: string;     // 权限名称 (可选，2-100字符)
  description?: string;         // 权限描述 (可选)
}
```

**返回数据**: `PermissionOut`

**注意**: 系统权限不能修改，权限编码、资源、操作等核心信息不可修改

### 5. 删除权限

**接口**: `DELETE /admin/permissions/{permission_id}`

**描述**: 删除权限（物理删除）

**路径参数**:
- `permission_id` (string): 权限ID

**返回数据**:
```typescript
{
  message: string;  // "权限删除成功"
}
```

**注意**: 系统权限不能删除，删除权限会同时删除相关的角色权限关联

### 6. 获取系统权限列表

**接口**: `GET /admin/permissions/system`

**描述**: 获取所有系统权限

**返回数据**: `PermissionOut[]`

**示例响应**:
```json
[
  {
    "id": "PERM_USER_READ",
    "permission_name": "用户查看",
    "permission_code": "user:read",
    "resource": "user",
    "action": "read",
    "description": null,
    "is_system_permission": true,
    "created_at": "2025-09-15T12:22:50.988067Z",
    "updated_at": "2025-09-15T12:22:50.988067Z"
  }
]
```

### 7. 根据资源获取权限列表

**接口**: `GET /admin/permissions/by-resource/{resource}`

**描述**: 获取指定资源的所有权限

**路径参数**:
- `resource` (string): 资源名称

**返回数据**: `PermissionOut[]`

### 8. 检查权限是否存在

**接口**: `GET /admin/permissions/check/{permission_code}`

**描述**: 检查指定权限编码是否已存在

**路径参数**:
- `permission_code` (string): 权限编码

**返回数据**:
```typescript
{
  exists: boolean;          // 是否存在
  permission_code: string;  // 权限编码
}
```

### 9. 获取权限总数

**接口**: `GET /admin/permissions/count`

**描述**: 获取符合条件的权限总数

**请求参数**: 同权限列表接口的查询参数

**返回数据**:
```typescript
{
  count: number;  // 权限总数
}
```

## 错误响应

所有接口在出错时会返回标准的错误响应：

```typescript
interface ErrorResponse {
  detail: string;  // 错误详情
}
```

**常见HTTP状态码**:
- `200` - 请求成功
- `400` - 请求参数错误
- `401` - 未认证或认证失败
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

## 前端集成建议

### 1. 认证Token管理

```typescript
// 设置认证头
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};
```

### 2. API调用示例

```typescript
// 获取角色列表
async function getRoles(query?: RoleQuery): Promise<RoleOut[]> {
  const params = new URLSearchParams(query as any);
  const response = await fetch(`/api/v1/admin/roles/?${params}`, {
    headers: authHeaders
  });
  return response.json();
}

// 创建角色
async function createRole(roleData: RoleIn): Promise<RoleOut> {
  const response = await fetch('/api/v1/admin/roles/', {
    method: 'POST',
    headers: authHeaders,
    body: JSON.stringify(roleData)
  });
  return response.json();
}
```

### 3. 表单验证规则

```typescript
// 角色表单验证
const roleValidation = {
  role_name: { required: true, minLength: 2, maxLength: 100 },
  role_code: {
    required: true,
    minLength: 2,
    maxLength: 50,
    pattern: /^[A-Z0-9_]+$/  // 大写字母数字下划线
  }
};

// 权限表单验证
const permissionValidation = {
  permission_name: { required: true, minLength: 2, maxLength: 100 },
  permission_code: {
    required: true,
    pattern: /^[a-z0-9_-]+:[a-z]+$/  // resource:action格式
  },
  action: {
    required: true,
    enum: ['create', 'read', 'update', 'delete', 'write', 'execute', 'manage']
  }
};
```

### 4. 数据类型定义

建议将以上所有TypeScript接口定义保存到独立的类型文件中：

```typescript
// types/auth.ts
export interface RoleOut { /* ... */ }
export interface RoleIn { /* ... */ }
export interface PermissionOut { /* ... */ }
export interface PermissionIn { /* ... */ }
// ... 其他接口定义
```

这样可以确保前后端类型一致性，减少集成错误。