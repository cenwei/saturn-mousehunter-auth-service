"""
认证服务 - JWT工具类
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Union
import jwt
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.config.app_config import JWTConfig

log = get_logger(__name__)


class JWTUtils:
    """JWT工具类"""

    def __init__(self, jwt_config: JWTConfig):
        self.config = jwt_config

    def create_access_token(self,
                           subject: str,
                           user_type: str,
                           user_id: str,
                           permissions: list[str] = None,
                           roles: list[str] = None,
                           expires_delta: Optional[timedelta] = None,
                           additional_claims: Dict[str, Any] = None) -> str:
        """创建访问令牌"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.access_token_expire_minutes
            )

        claims = {
            "sub": subject,  # 主题（用户标识）
            "user_type": user_type,
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": self.config.issuer,
            "type": "access_token"
        }

        if permissions:
            claims["permissions"] = permissions

        if roles:
            claims["roles"] = roles

        if additional_claims:
            claims.update(additional_claims)

        try:
            token = jwt.encode(
                claims,
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            log.debug(f"Created access token for user: {user_id}")
            return token
        except Exception as e:
            log.error(f"Failed to create access token: {e}")
            raise

    def create_refresh_token(self,
                            subject: str,
                            user_type: str,
                            user_id: str,
                            expires_delta: Optional[timedelta] = None,
                            additional_claims: Dict[str, Any] = None) -> str:
        """创建刷新令牌"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self.config.refresh_token_expire_days
            )

        claims = {
            "sub": subject,
            "user_type": user_type,
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": self.config.issuer,
            "type": "refresh_token"
        }

        if additional_claims:
            claims.update(additional_claims)

        try:
            token = jwt.encode(
                claims,
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            log.debug(f"Created refresh token for user: {user_id}")
            return token
        except Exception as e:
            log.error(f"Failed to create refresh token: {e}")
            raise

    def decode_token(self, token: str) -> Dict[str, Any]:
        """解码JWT令牌"""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
                options={"verify_exp": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            log.warning("Token has expired")
            raise ValueError("令牌已过期")
        except jwt.InvalidTokenError as e:
            log.warning(f"Invalid token: {e}")
            raise ValueError("无效的令牌")
        except Exception as e:
            log.error(f"Failed to decode token: {e}")
            raise ValueError("令牌解析失败")

    def verify_token(self, token: str, token_type: str = None) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = self.decode_token(token)

            # 验证令牌类型
            if token_type and payload.get("type") != token_type:
                log.warning(f"Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}")
                return None

            # 验证发行者
            if payload.get("iss") != self.config.issuer:
                log.warning(f"Invalid issuer: {payload.get('iss')}")
                return None

            return payload

        except ValueError:
            # 令牌验证失败
            return None
        except Exception as e:
            log.error(f"Unexpected error during token verification: {e}")
            return None

    def extract_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """从令牌中提取用户信息"""
        payload = self.verify_token(token, "access_token")
        if not payload:
            return None

        return {
            "user_id": payload.get("user_id"),
            "user_type": payload.get("user_type"),
            "subject": payload.get("sub"),
            "permissions": payload.get("permissions", []),
            "roles": payload.get("roles", []),
            "expires_at": datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc),
            "issued_at": datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc)
        }

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """获取令牌过期时间"""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
                options={"verify_exp": False}  # 不验证过期时间，只获取信息
            )
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp, tz=timezone.utc)
            return None
        except Exception as e:
            log.error(f"Failed to get token expiry: {e}")
            return None

    def is_token_expired(self, token: str) -> bool:
        """检查令牌是否过期"""
        try:
            expiry = self.get_token_expiry(token)
            if expiry:
                return datetime.now(timezone.utc) > expiry
            return True  # 无法获取过期时间，认为已过期
        except Exception:
            return True

    def refresh_access_token(self, refresh_token: str,
                            permissions: list[str] = None,
                            roles: list[str] = None,
                            additional_claims: Dict[str, Any] = None) -> Optional[str]:
        """使用刷新令牌创建新的访问令牌"""
        payload = self.verify_token(refresh_token, "refresh_token")
        if not payload:
            log.warning("Invalid refresh token")
            return None

        # 创建新的访问令牌
        return self.create_access_token(
            subject=payload.get("sub"),
            user_type=payload.get("user_type"),
            user_id=payload.get("user_id"),
            permissions=permissions,
            roles=roles,
            additional_claims=additional_claims
        )

    def create_token_pair(self,
                         subject: str,
                         user_type: str,
                         user_id: str,
                         permissions: list[str] = None,
                         roles: list[str] = None,
                         additional_claims: Dict[str, Any] = None) -> Dict[str, str]:
        """创建访问令牌和刷新令牌对"""
        access_token = self.create_access_token(
            subject=subject,
            user_type=user_type,
            user_id=user_id,
            permissions=permissions,
            roles=roles,
            additional_claims=additional_claims
        )

        refresh_token = self.create_refresh_token(
            subject=subject,
            user_type=user_type,
            user_id=user_id,
            additional_claims=additional_claims
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.config.access_token_expire_minutes * 60
        }

    def validate_token_claims(self, token: str, required_permissions: list[str] = None,
                             required_roles: list[str] = None) -> bool:
        """验证令牌权限声明"""
        user_info = self.extract_user_info(token)
        if not user_info:
            return False

        user_permissions = set(user_info.get("permissions", []))
        user_roles = set(user_info.get("roles", []))

        # 检查权限
        if required_permissions:
            required_perms = set(required_permissions)
            if not required_perms.issubset(user_permissions):
                log.warning(f"Insufficient permissions. Required: {required_permissions}, Got: {list(user_permissions)}")
                return False

        # 检查角色
        if required_roles:
            required_role_set = set(required_roles)
            if not required_role_set.intersection(user_roles):  # 至少有一个匹配的角色
                log.warning(f"Insufficient roles. Required one of: {required_roles}, Got: {list(user_roles)}")
                return False

        return True

    def get_token_payload_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """获取令牌载荷（不验证签名，仅用于调试和日志）"""
        try:
            # 不验证签名，仅解码
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            return payload
        except Exception as e:
            log.error(f"Failed to decode token payload: {e}")
            return None