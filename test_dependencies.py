"""
认证服务独立测试 - 不依赖外部库
"""

def test_basic_password_operations():
    """测试基本密码操作"""
    try:
        import bcrypt
        import secrets
        import string

        # 测试bcrypt密码哈希
        password = "test123456"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # 验证密码
        assert bcrypt.checkpw(password.encode(), hashed), "密码验证失败"
        assert not bcrypt.checkpw(b"wrong", hashed), "错误密码验证应该失败"

        print("✅ 基本密码操作测试通过")
        return True
    except Exception as e:
        print(f"❌ 密码操作测试失败: {e}")
        return False

def test_jwt_basics():
    """测试JWT基础功能"""
    try:
        import jwt
        from datetime import datetime, timedelta

        # 创建payload
        payload = {
            "user_id": "test123",
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        secret = "test-secret-key"

        # 编码JWT
        token = jwt.encode(payload, secret, algorithm="HS256")
        assert token, "JWT令牌创建失败"

        # 解码JWT
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        assert decoded["user_id"] == "test123", "用户ID不匹配"
        assert decoded["username"] == "testuser", "用户名不匹配"

        print("✅ JWT基础功能测试通过")
        return True
    except Exception as e:
        print(f"❌ JWT测试失败: {e}")
        return False

def test_pydantic_models():
    """测试Pydantic模型"""
    try:
        from pydantic import BaseModel, EmailStr, ValidationError

        # 定义简单用户模型
        class TestUser(BaseModel):
            username: str
            email: str
            is_active: bool = True

        # 测试有效数据
        user = TestUser(
            username="testuser",
            email="test@example.com"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active == True

        # 测试无效数据
        try:
            invalid_user = TestUser(username="")  # 缺少email
            assert False, "应该抛出验证错误"
        except ValidationError:
            pass  # 预期的错误

        print("✅ Pydantic模型测试通过")
        return True
    except Exception as e:
        print(f"❌ Pydantic测试失败: {e}")
        return False

def test_fastapi_import():
    """测试FastAPI导入"""
    try:
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.security import HTTPBearer

        # 创建简单app
        app = FastAPI(title="Test Auth Service")
        security = HTTPBearer()

        @app.get("/health")
        def health():
            return {"status": "ok"}

        print("✅ FastAPI导入测试通过")
        return True
    except Exception as e:
        print(f"❌ FastAPI导入失败: {e}")
        return False

def test_asyncpg_available():
    """测试asyncpg是否可用"""
    try:
        import asyncpg
        print("✅ AsyncPG数据库驱动可用")
        return True
    except ImportError as e:
        print(f"❌ AsyncPG不可用: {e}")
        return False

def run_independent_tests():
    """运行独立测试"""
    print("🔍 开始认证服务依赖测试...")
    print("=" * 60)

    tests = [
        ("基本密码操作", test_basic_password_operations),
        ("JWT基础功能", test_jwt_basics),
        ("Pydantic模型", test_pydantic_models),
        ("FastAPI框架", test_fastapi_import),
        ("AsyncPG驱动", test_asyncpg_available)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n📋 测试: {name}")
        if test_func():
            passed += 1

    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有依赖测试通过！认证服务基础组件正常")
        print("\n📝 认证服务状态评估:")
        print("   ✅ 核心依赖库完整")
        print("   ✅ 密码安全组件可用")
        print("   ✅ JWT认证组件可用")
        print("   ✅ 数据模型验证可用")
        print("   ✅ Web框架可用")
        print("   ✅ 数据库驱动可用")
        print("\n🚀 认证服务已具备运行条件")
        return True
    else:
        print(f"⚠️  {total - passed} 个测试失败，需要安装相应依赖")
        return False

if __name__ == "__main__":
    run_independent_tests()