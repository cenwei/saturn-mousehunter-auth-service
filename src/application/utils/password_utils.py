"""
认证服务 - 密码工具类
"""
import hashlib
import secrets
import string
from passlib.context import CryptContext
from saturn_mousehunter_shared.log.logger import get_logger

log = get_logger(__name__)

# 密码上下文配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordUtils:
    """密码工具类"""

    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        if not password:
            raise ValueError("密码不能为空")

        try:
            return pwd_context.hash(password)
        except Exception as e:
            log.error(f"密码哈希失败: {e}")
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        if not plain_password or not hashed_password:
            return False

        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            log.error(f"密码验证失败: {e}")
            return False

    @staticmethod
    def generate_password(length: int = 12,
                         include_uppercase: bool = True,
                         include_lowercase: bool = True,
                         include_digits: bool = True,
                         include_special: bool = True) -> str:
        """生成随机密码"""
        if length < 4:
            raise ValueError("密码长度至少为4位")

        characters = ""
        required_chars = []

        if include_lowercase:
            characters += string.ascii_lowercase
            required_chars.append(secrets.choice(string.ascii_lowercase))

        if include_uppercase:
            characters += string.ascii_uppercase
            required_chars.append(secrets.choice(string.ascii_uppercase))

        if include_digits:
            characters += string.digits
            required_chars.append(secrets.choice(string.digits))

        if include_special:
            special_chars = "!@#$%^&*()-_+=[]{}|;:,.<>?"
            characters += special_chars
            required_chars.append(secrets.choice(special_chars))

        if not characters:
            raise ValueError("至少需要包含一种字符类型")

        # 生成剩余字符
        remaining_length = length - len(required_chars)
        if remaining_length > 0:
            for _ in range(remaining_length):
                required_chars.append(secrets.choice(characters))

        # 打乱字符顺序
        password_chars = required_chars.copy()
        secrets.SystemRandom().shuffle(password_chars)

        return ''.join(password_chars)

    @staticmethod
    def validate_password_strength(password: str,
                                  min_length: int = 8,
                                  require_uppercase: bool = True,
                                  require_lowercase: bool = True,
                                  require_digit: bool = True,
                                  require_special: bool = False) -> tuple[bool, list[str]]:
        """验证密码强度"""
        errors = []

        if not password:
            errors.append("密码不能为空")
            return False, errors

        if len(password) < min_length:
            errors.append(f"密码长度不能少于{min_length}位")

        if require_uppercase and not any(c.isupper() for c in password):
            errors.append("密码必须包含至少一个大写字母")

        if require_lowercase and not any(c.islower() for c in password):
            errors.append("密码必须包含至少一个小写字母")

        if require_digit and not any(c.isdigit() for c in password):
            errors.append("密码必须包含至少一个数字")

        if require_special:
            special_chars = set("!@#$%^&*()-_+=[]{}|;:,.<>?")
            if not any(c in special_chars for c in password):
                errors.append("密码必须包含至少一个特殊字符")

        # 检查常见弱密码
        weak_passwords = [
            "password", "123456", "123456789", "12345678", "12345",
            "1234567", "password123", "admin", "qwerty", "abc123"
        ]

        if password.lower() in weak_passwords:
            errors.append("不能使用常见的弱密码")

        return len(errors) == 0, errors

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """生成盐值"""
        return secrets.token_hex(length)

    @staticmethod
    def hash_with_salt(password: str, salt: str) -> str:
        """使用盐值哈希密码（兼容性方法）"""
        return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def is_password_compromised(password: str) -> bool:
        """检查密码是否在已泄露密码库中（简化实现）"""
        # 这里可以集成 HaveIBeenPwned API 或其他密码泄露检查服务
        # 目前只检查最常见的弱密码
        common_passwords = {
            "password", "123456", "123456789", "12345678", "12345",
            "1234567", "password123", "admin", "qwerty", "abc123",
            "welcome", "monkey", "1234567890", "login", "princess"
        }

        return password.lower() in common_passwords

    @staticmethod
    def calculate_password_entropy(password: str) -> float:
        """计算密码熵值"""
        if not password:
            return 0.0

        # 计算字符集大小
        charset_size = 0

        if any(c.islower() for c in password):
            charset_size += 26  # 小写字母

        if any(c.isupper() for c in password):
            charset_size += 26  # 大写字母

        if any(c.isdigit() for c in password):
            charset_size += 10  # 数字

        if any(c in "!@#$%^&*()-_+=[]{}|;:,.<>?" for c in password):
            charset_size += 22  # 特殊字符

        # 计算熵值：H = log2(N^L)，其中N是字符集大小，L是密码长度
        import math
        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
            return entropy

        return 0.0

    @staticmethod
    def get_password_strength_level(password: str) -> str:
        """获取密码强度等级"""
        entropy = PasswordUtils.calculate_password_entropy(password)

        if entropy >= 60:
            return "很强"
        elif entropy >= 36:
            return "强"
        elif entropy >= 28:
            return "中等"
        elif entropy >= 18:
            return "弱"
        else:
            return "很弱"