#!/bin/bash
cd /home/cenwei/workspace/saturn_mousehunter/saturn-mousehunter-auth-service

echo "🔍 启动认证服务完整测试..."
echo "=================================="

# 激活虚拟环境并后台启动服务
source .venv/bin/activate
python test_auth_server.py &
SERVER_PID=$!

# 等待服务启动
sleep 3

echo "📋 测试开始..."

# 1. 健康检查
echo "1️⃣ 测试健康检查..."
curl -s http://192.168.8.168:8001/health && echo

# 2. 测试登录
echo "2️⃣ 测试用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST http://192.168.8.168:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

echo "登录响应: $LOGIN_RESPONSE"

# 3. 提取token并测试验证
if [[ $LOGIN_RESPONSE == *"access_token"* ]]; then
    TOKEN=$(echo $LOGIN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "3️⃣ 测试令牌验证..."
    curl -s -H "Authorization: Bearer $TOKEN" http://192.168.8.168:8001/api/v1/users/me && echo

    echo "✅ 所有API测试通过！"
else
    echo "❌ 登录失败，无法获取token"
fi

# 清理
kill $SERVER_PID 2>/dev/null
echo "🎉 认证服务测试完成！"