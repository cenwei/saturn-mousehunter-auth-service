"""
认证服务简单测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """测试模块导入"""
    try:
        from domain.models import AdminUserIn, AdminUserOut
        from application.services.admin_user_service import AdminUserService
        from application.utils.password_utils import PasswordUtils
        from application.utils.jwt_utils import JWTUtils
        print("✅ 所有核心模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_password_utils():
    """测试密码工具"""
    try:
        from application.utils.password_utils import PasswordUtils

        password = "test123456"

        # 测试密码哈希
        hash1 = PasswordUtils.hash_password(password)
        hash2 = PasswordUtils.hash_password(password)
        assert hash1 != hash2, "两次哈希结果应该不同"

        # 测试密码验证
        assert PasswordUtils.verify_password(password, hash1), "密码验证应该成功"
        assert not PasswordUtils.verify_password("wrong", hash1), "错误密码验证应该失败"

        # 测试密码生成
        generated = PasswordUtils.generate_password(12)
        assert len(generated) == 12, "生成的密码长度应该正确"

        print("✅ 密码工具测试通过")
        return True
    except Exception as e:
        print(f"❌ 密码工具测试失败: {e}")
        return False

def test_jwt_utils():
    """测试JWT工具"""
    try:
        from application.utils.jwt_utils import JWTUtils

        user_data = {
            "user_id": "test123",
            "username": "testuser",
            "user_type": "admin_user"
        }

        # 测试令牌创建
        access_token = JWTUtils.create_access_token(user_data)
        refresh_token = JWTUtils.create_refresh_token(user_data)

        assert access_token, "访问令牌应该被创建"
        assert refresh_token, "刷新令牌应该被创建"
        assert access_token != refresh_token, "访问令牌和刷新令牌应该不同"

        # 测试令牌验证
        payload = JWTUtils.verify_token(access_token)
        assert payload["user_id"] == "test123", "用户ID应该正确"
        assert payload["username"] == "testuser", "用户名应该正确"

        print("✅ JWT工具测试通过")
        return True
    except Exception as e:
        print(f"❌ JWT工具测试失败: {e}")
        return False

def test_models():
    """测试域模型"""
    try:
        from domain.models import AdminUserIn, AdminUserOut

        # 测试用户输入模型
        user_in = AdminUserIn(
            username="testuser",
            email="test@example.com",
            password="test123456",
            full_name="Test User",
            is_active=True,
            created_by="system"
        )

        assert user_in.username == "testuser", "用户名应该正确"
        assert user_in.email == "test@example.com", "邮箱应该正确"

        print("✅ 域模型测试通过")
        return True
    except Exception as e:
        print(f"❌ 域模型测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🔍 开始认证服务测试...")
    print("=" * 50)

    tests = [
        ("模块导入", test_imports),
        ("密码工具", test_password_utils),
        ("JWT工具", test_jwt_utils),
        ("域模型", test_models)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n📋 测试: {name}")
        if test_func():
            passed += 1
        else:
            print(f"   跳过后续测试...")
            break

    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！认证服务基础功能正常")
        return True
    else:
        print("⚠️  部分测试失败，需要检查代码")
        return False

if __name__ == "__main__":
    run_all_tests()