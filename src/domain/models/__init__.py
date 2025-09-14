"""
认证服务 Domain Models
"""

# 用户模型
from .auth_admin_user import (
    AdminUserIn, AdminUserOut, AdminUserUpdate, AdminUserQuery,
    AdminUserLogin, AdminUserResponse
)

from .auth_tenant_user import (
    TenantUserIn, TenantUserOut, TenantUserUpdate, TenantUserQuery,
    TenantUserLogin, TenantUserResponse
)

# 角色权限模型
from .auth_role import (
    RoleIn, RoleOut, RoleUpdate, RoleQuery, RoleWithPermissions,
    RoleScope
)

from .auth_permission import (
    PermissionIn, PermissionOut, PermissionUpdate, PermissionQuery
)

from .auth_user_role import (
    UserRoleIn, UserRoleOut, UserRoleUpdate, UserRoleQuery,
    UserRoleAssignment, UserPermissions, UserType
)

from .auth_role_permission import (
    RolePermissionIn, RolePermissionOut, RolePermissionQuery,
    RolePermissionAssignment
)

# 审计和会话模型
from .auth_audit_log import (
    AuditLogIn, AuditLogOut, AuditLogQuery, AuditLogStats
)

from .auth_session import (
    SessionIn, SessionOut, SessionUpdate, SessionQuery,
    SessionInfo, TokenPair, TokenRefreshRequest, SessionStats
)

__all__ = [
    # 管理员用户
    "AdminUserIn", "AdminUserOut", "AdminUserUpdate", "AdminUserQuery",
    "AdminUserLogin", "AdminUserResponse",

    # 租户用户
    "TenantUserIn", "TenantUserOut", "TenantUserUpdate", "TenantUserQuery",
    "TenantUserLogin", "TenantUserResponse",

    # 角色权限
    "RoleIn", "RoleOut", "RoleUpdate", "RoleQuery", "RoleWithPermissions", "RoleScope",
    "PermissionIn", "PermissionOut", "PermissionUpdate", "PermissionQuery",
    "UserRoleIn", "UserRoleOut", "UserRoleUpdate", "UserRoleQuery",
    "UserRoleAssignment", "UserPermissions", "UserType",
    "RolePermissionIn", "RolePermissionOut", "RolePermissionQuery",
    "RolePermissionAssignment",

    # 审计日志
    "AuditLogIn", "AuditLogOut", "AuditLogQuery", "AuditLogStats",

    # 会话管理
    "SessionIn", "SessionOut", "SessionUpdate", "SessionQuery",
    "SessionInfo", "TokenPair", "TokenRefreshRequest", "SessionStats"
]