"""
认证服务 - 应用配置
"""
import os
from typing import List
from dataclasses import dataclass
from saturn_mousehunter_shared.log.logger import get_logger

log = get_logger(__name__)


@dataclass
class JWTConfig:
    """JWT配置"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "saturn-mousehunter-auth-service"

    def __post_init__(self):
        if len(self.secret_key) < 32:
            raise ValueError("JWT密钥长度不能少于32位")


@dataclass
class CORSConfig:
    """CORS配置"""
    allow_origins: List[str]
    allow_methods: List[str] = None
    allow_headers: List[str] = None
    allow_credentials: bool = True

    def __post_init__(self):
        if self.allow_methods is None:
            self.allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        if self.allow_headers is None:
            self.allow_headers = ["*"]


@dataclass
class SecurityConfig:
    """安全配置"""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = False
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_hours: int = 24
    require_email_verification: bool = False


@dataclass
class AppConfig:
    """应用配置"""
    app_name: str = "Saturn MouseHunter Auth Service"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    log_level: str = "INFO"
    jwt: JWTConfig = None
    cors: CORSConfig = None
    security: SecurityConfig = None

    def __post_init__(self):
        if self.jwt is None:
            self.jwt = get_jwt_config()
        if self.cors is None:
            self.cors = get_cors_config()
        if self.security is None:
            self.security = get_security_config()


def get_jwt_config() -> JWTConfig:
    """从环境变量获取JWT配置"""
    secret_key = os.getenv("AUTH_JWT_SECRET_KEY")
    if not secret_key:
        # 开发环境使用默认密钥，生产环境必须配置
        if os.getenv("AUTH_ENV", "development") == "production":
            raise ValueError("生产环境必须配置 AUTH_JWT_SECRET_KEY")
        secret_key = "saturn_mousehunter_auth_default_secret_key_for_development_only"
        log.warning("使用默认JWT密钥，生产环境请配置 AUTH_JWT_SECRET_KEY")

    return JWTConfig(
        secret_key=secret_key,
        algorithm=os.getenv("AUTH_JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        refresh_token_expire_days=int(os.getenv("AUTH_JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        issuer=os.getenv("AUTH_JWT_ISSUER", "saturn-mousehunter-auth-service"),
    )


def get_cors_config() -> CORSConfig:
    """从环境变量获取CORS配置"""
    origins_str = os.getenv("AUTH_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
    allow_origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    return CORSConfig(
        allow_origins=allow_origins,
        allow_credentials=os.getenv("AUTH_CORS_CREDENTIALS", "true").lower() == "true"
    )


def get_security_config() -> SecurityConfig:
    """从环境变量获取安全配置"""
    return SecurityConfig(
        password_min_length=int(os.getenv("AUTH_PASSWORD_MIN_LENGTH", "8")),
        password_require_uppercase=os.getenv("AUTH_PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
        password_require_lowercase=os.getenv("AUTH_PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
        password_require_digit=os.getenv("AUTH_PASSWORD_REQUIRE_DIGIT", "true").lower() == "true",
        password_require_special=os.getenv("AUTH_PASSWORD_REQUIRE_SPECIAL", "false").lower() == "true",
        max_login_attempts=int(os.getenv("AUTH_MAX_LOGIN_ATTEMPTS", "5")),
        lockout_duration_minutes=int(os.getenv("AUTH_LOCKOUT_DURATION_MINUTES", "30")),
        session_timeout_hours=int(os.getenv("AUTH_SESSION_TIMEOUT_HOURS", "24")),
        require_email_verification=os.getenv("AUTH_REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true",
    )


def get_app_config() -> AppConfig:
    """从环境变量获取应用配置"""
    return AppConfig(
        app_name=os.getenv("AUTH_APP_NAME", "Saturn MouseHunter Auth Service"),
        version=os.getenv("AUTH_VERSION", "1.0.0"),
        debug=os.getenv("AUTH_DEBUG", "false").lower() == "true",
        host=os.getenv("AUTH_HOST", "0.0.0.0"),
        port=int(os.getenv("AUTH_PORT", "8001")),
        reload=os.getenv("AUTH_RELOAD", "false").lower() == "true",
        log_level=os.getenv("AUTH_LOG_LEVEL", "INFO"),
    )