# Saturn MouseHunter 认证服务 API 文档

## 服务概述
- **名称**: Saturn MouseHunter Auth Service
- **版本**: 1.0.0
- **端口**: 8001
- **基础URL**: http://192.168.8.168:8001

## 核心接口

### 🏥 健康检查
```http
GET /health
```
**响应示例**:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2025-09-14T10:22:47.843570+00:00"
}
```

### 🔐 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```
**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_info": {
    "username": "admin",
    "user_type": "admin_user",
    "is_active": true
  }
}
```

### 🎫 令牌验证
```http
GET /api/v1/auth/verify?token={jwt_token}
```

### 👤 获取当前用户
```http
GET /api/v1/users/me
Authorization: Bearer {jwt_token}
```
**响应示例**:
```json
{
  "username": "admin",
  "user_type": "admin_user",
  "is_active": true
}
```

## 认证方式
- **类型**: Bearer Token (JWT)
- **请求头**: `Authorization: Bearer {access_token}`
- **令牌有效期**: 24小时

## 错误响应
```json
{
  "detail": "错误描述"
}
```

**常见错误码**:
- `401`: 认证失败
- `404`: 资源不存在
- `422`: 请求参数错误

## 测试用户
- **用户名**: admin
- **密码**: admin123
- **类型**: admin_user