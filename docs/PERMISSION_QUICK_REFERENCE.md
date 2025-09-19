# 权限系统快速参考

## 🎯 权限编码速查表

### 用户管理
- `user:read` - 查看用户信息
- `user:write` - 管理用户（增删改）

### 角色管理
- `role:read` - 查看角色信息
- `role:write` - 管理角色（增删改）

### 系统管理
- `system:admin` - 系统管理权限

## 👑 预定义角色

### 超级管理员 (super_admin)
```
权限: user:read, user:write, role:read, role:write, system:admin
用途: 系统最高权限
```

## 🔧 API装饰器

### 权限验证
```python
# 需要特定权限
@Depends(require_permissions(["user:read"]))

# 需要特定角色
@Depends(require_roles(["super_admin"]))

# 仅管理员用户
@Depends(get_admin_user)

# 仅租户用户
@Depends(get_tenant_user)
```

## 📊 用户类型

- `ADMIN` - 管理员用户（系统级）
- `TENANT` - 租户用户（租户级）

## 🎭 角色范围

- `GLOBAL` - 全局角色（跨租户）
- `TENANT` - 租户角色（租户内）
- `SYSTEM` - 系统角色（系统级）

## 🔗 常用API

```bash
# 角色管理
GET    /api/v1/roles                    # 角色列表
POST   /api/v1/roles                    # 创建角色
PUT    /api/v1/roles/{id}               # 更新角色
DELETE /api/v1/roles/{id}               # 删除角色

# 权限管理
GET    /api/v1/permissions              # 权限列表
POST   /api/v1/permissions              # 创建权限

# 用户权限
GET    /api/v1/users/{id}/roles         # 用户角色
POST   /api/v1/users/{id}/roles         # 分配角色
DELETE /api/v1/users/{id}/roles/{rid}   # 移除角色
```

## 💡 权限验证流程

1. 用户请求 → 提取JWT Token
2. 解析Token → 获取用户信息
3. 查询用户角色 → 获取角色权限
4. 权限验证 → 允许/拒绝访问

## 🚀 快速开始

### 1. 创建权限
```json
POST /api/v1/permissions
{
  "permission_name": "产品管理",
  "permission_code": "product:write",
  "resource": "product",
  "action": "write"
}
```

### 2. 创建角色
```json
POST /api/v1/roles
{
  "role_name": "产品经理",
  "role_code": "PRODUCT_MANAGER",
  "scope": "TENANT"
}
```

### 3. 分配权限给角色
```json
POST /api/v1/roles/{role_id}/permissions
{
  "permission_ids": ["PERM_PRODUCT_WRITE"]
}
```

### 4. 分配角色给用户
```json
POST /api/v1/users/{user_id}/roles
{
  "role_ids": ["ROLE_PRODUCT_MANAGER"]
}
```

---
**更多详情**: 查看 [完整权限系统文档](PERMISSION_SYSTEM.md) 和 [API文档](PERMISSION_API.md)