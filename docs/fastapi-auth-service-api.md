# Saturn MouseHunter 认证服务 FastAPI 文档

**服务前缀**: `/api/v1/auth`
**服务名称**: saturn-mousehunter-auth-service
**版本**: 1.0.0
**服务地址**: http://192.168.8.168:8001

## 服务概述

认证服务提供JWT认证、用户管理功能，支持管理员和租户用户的认证授权。

## API 端点

### 🏠 基础端点

#### GET `/`
**描述**: 根路径
**响应**: 服务基本信息

#### GET `/health`
**描述**: 健康检查
**响应**:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2025-09-14T23:51:32.376502+00:00"
}
```

### 🔐 认证端点

#### POST `/api/v1/auth/login`
**描述**: 用户登录
**前缀**: `/api/v1/auth`

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_info": {
    "username": "admin",
    "user_type": "admin_user",
    "is_active": true
  }
}
```

**测试用户**:
- 用户名: `admin`
- 密码: `admin123`

#### GET `/api/v1/auth/verify`
**描述**: 验证JWT令牌
**前缀**: `/api/v1/auth`

**查询参数**:
- `token` (string, required): JWT令牌

**响应**:
```json
{
  "valid": true,
  "user_info": {
    "user_id": "admin",
    "username": "admin",
    "user_type": "admin_user"
  }
}
```

### 👤 用户端点

#### GET `/api/v1/users/me`
**描述**: 获取当前用户信息
**前缀**: `/api/v1/users`

**请求头**:
```
Authorization: Bearer <JWT_TOKEN>
```

**响应**:
```json
{
  "user_id": "admin",
  "username": "admin",
  "user_type": "admin_user",
  "is_active": true,
  "permissions": ["user:read", "user:write"]
}
```

## 认证流程

### 1. 登录获取令牌
```bash
curl -X POST http://192.168.8.168:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. 使用令牌访问受保护端点
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://192.168.8.168:8001/api/v1/users/me
```

### 3. 验证令牌有效性
```bash
curl "http://192.168.8.168:8001/api/v1/auth/verify?token=<TOKEN>"
```

## 数据模型

### LoginRequest
```typescript
{
  username: string;
  password: string;
}
```

### LoginResponse
```typescript
{
  access_token: string;
  token_type: string; // "bearer"
  user_info: {
    username: string;
    user_type: string;
    is_active: boolean;
  };
}
```

### JWT Payload
```typescript
{
  user_id: string;
  username: string;
  user_type: string; // "admin_user" | "tenant_user"
  exp: number; // 过期时间戳
  iat: number; // 签发时间戳
}
```

## 错误响应

### 401 Unauthorized
```json
{
  "detail": "用户名或密码错误"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 安全配置

- **JWT算法**: HS256
- **令牌过期时间**: 24小时
- **刷新令牌**: 支持
- **密码加密**: bcrypt

## 集成示例

### Python FastAPI 客户端
```python
import httpx

class AuthClient:
    def __init__(self, base_url="http://192.168.8.168:8001"):
        self.base_url = base_url
        self.token = None

    async def login(self, username: str, password: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            data = response.json()
            self.token = data["access_token"]
            return data

    async def get_current_user(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            return response.json()
```

### JavaScript 客户端
```javascript
class AuthClient {
  constructor(baseUrl = 'http://192.168.8.168:8001') {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async getCurrentUser() {
    const response = await fetch(`${this.baseUrl}/api/v1/users/me`, {
      headers: {'Authorization': `Bearer ${this.token}`}
    });
    return response.json();
  }
}
```

## 部署信息

- **端口**: 8001
- **协议**: HTTP
- **环境**: 开发环境
- **文档地址**: http://192.168.8.168:8001/docs
- **OpenAPI规范**: http://192.168.8.168:8001/openapi.json

## 依赖服务

- **数据库**: PostgreSQL (认证数据存储)
- **共享库**: saturn-mousehunter-shared (日志、工具)

---

**更新时间**: 2025-09-15
**文档版本**: 1.0.0