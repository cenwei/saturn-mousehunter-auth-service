# 认证服务 API 测试集合

## 🚀 快速测试

### 1. 健康检查
```bash
curl http://192.168.8.168:8001/health
```

### 2. 用户登录
```bash
curl -X POST http://192.168.8.168:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 3. 获取用户信息
```bash
# 先获取token
TOKEN=$(curl -s -X POST http://192.168.8.168:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 使用token获取用户信息
curl -H "Authorization: Bearer $TOKEN" \
  http://192.168.8.168:8001/api/v1/users/me
```

## 📋 Postman集合

### Environment变量
```json
{
  "auth_base_url": "http://192.168.8.168:8001",
  "access_token": ""
}
```

### 请求集合
1. **Login** → 保存`access_token`到环境变量
2. **Get User Info** → 使用`{{access_token}}`
3. **Health Check** → 服务状态检查

## ⚡ 自动化测试脚本

启动完整测试:
```bash
cd /home/cenwei/workspace/saturn_mousehunter/saturn-mousehunter-auth-service
./test_full_api.sh
```

## 📊 预期响应格式

**登录成功**:
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

**用户信息**:
```json
{
  "username": "admin",
  "user_type": "admin_user",
  "is_active": true
}
```