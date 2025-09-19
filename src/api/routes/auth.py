"""
认证服务 - 认证相关API路由
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from saturn_mousehunter_shared.log.logger import get_logger
from api.dependencies.auth import get_current_user_optional
from api.dependencies.services import get_jwt_utils
from application.utils import JWTUtils

log = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["认证"])


class TokenValidationRequest(BaseModel):
    """Token验证请求"""
    token: str


class TokenStatusResponse(BaseModel):
    """Token状态响应"""
    valid: bool
    expired: bool
    expires_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    time_until_expiry: Optional[int] = None  # 剩余秒数


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str


@router.post("/validate-token", response_model=TokenStatusResponse)
async def validate_token(
    request: TokenValidationRequest,
    jwt_utils: JWTUtils = Depends(get_jwt_utils)
):
    """
    验证Token状态

    这个端点帮助客户端检查Token的有效性和过期状态，
    避免客户端在协程中进行复杂的Token检查而导致取消错误
    """
    try:
        # 获取Token信息（不验证过期）
        expiry = jwt_utils.get_token_expiry(request.token)
        is_expired = jwt_utils.is_token_expired(request.token)

        # 尝试提取用户信息
        user_info = jwt_utils.extract_user_info(request.token) if not is_expired else None

        # 计算剩余时间
        time_until_expiry = None
        if expiry and not is_expired:
            time_until_expiry = int((expiry - datetime.now(timezone.utc)).total_seconds())

        response = TokenStatusResponse(
            valid=user_info is not None,
            expired=is_expired,
            expires_at=expiry,
            issued_at=user_info.get("issued_at") if user_info else None,
            user_id=user_info.get("user_id") if user_info else None,
            user_type=user_info.get("user_type") if user_info else None,
            time_until_expiry=time_until_expiry
        )

        log.debug(f"Token validation result: valid={response.valid}, expired={response.expired}")
        return response

    except Exception as e:
        log.error(f"Token validation error: {str(e)}")
        return TokenStatusResponse(
            valid=False,
            expired=True,
            expires_at=None,
            issued_at=None,
            user_id=None,
            user_type=None,
            time_until_expiry=None
        )


@router.post("/refresh-token")
async def refresh_token(
    request: RefreshTokenRequest,
    jwt_utils: JWTUtils = Depends(get_jwt_utils)
):
    """
    刷新访问Token

    使用刷新Token获取新的访问Token
    """
    try:
        # 验证刷新Token
        payload = jwt_utils.verify_token(request.refresh_token, "refresh_token")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新Token"
            )

        # 这里应该从数据库获取最新的用户权限
        # 为了简化，暂时使用Token中的信息
        new_access_token = jwt_utils.create_access_token(
            subject=payload.get("sub"),
            user_type=payload.get("user_type"),
            user_id=payload.get("user_id"),
            permissions=payload.get("permissions", []),
            roles=payload.get("roles", []),
            additional_claims=payload.get("tenant_id") and {"tenant_id": payload.get("tenant_id")} or None
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": jwt_utils.config.access_token_expire_minutes * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token刷新失败"
        )


@router.get("/user-info")
async def get_current_user_info(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    获取当前用户信息

    此端点不会抛出认证错误，而是返回null如果用户未认证
    """
    if not current_user:
        return {"authenticated": False, "user": None}

    return {
        "authenticated": True,
        "user": {
            "user_id": current_user.get("user_id"),
            "user_type": current_user.get("user_type"),
            "subject": current_user.get("subject"),
            "permissions": current_user.get("permissions", []),
            "roles": current_user.get("roles", []),
            "expires_at": current_user.get("expires_at")
        }
    }


@router.post("/logout")
async def logout(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    用户登出

    注意：JWT是无状态的，实际的Token失效需要客户端删除Token
    这个端点主要用于记录登出事件和清理服务器端状态（如果有的话）
    """
    if current_user:
        log.info(f"User logout: {current_user.get('user_id')}")

    return {"message": "登出成功"}