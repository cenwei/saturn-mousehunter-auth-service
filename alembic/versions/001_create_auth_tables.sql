-- Saturn MouseHunter 认证服务数据库表结构

-- 1. 管理员用户表
CREATE TABLE mh_auth_admin_users (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 租户用户表
CREATE TABLE mh_auth_tenant_users (
    id VARCHAR(50) PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active BOOLEAN DEFAULT true,
    is_tenant_admin BOOLEAN DEFAULT false,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, username),
    UNIQUE(tenant_id, email)
);

-- 3. 角色表
CREATE TABLE mh_auth_roles (
    id VARCHAR(50) PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    role_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    scope VARCHAR(20) DEFAULT 'GLOBAL',
    is_system_role BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 权限表
CREATE TABLE mh_auth_permissions (
    id VARCHAR(50) PRIMARY KEY,
    permission_name VARCHAR(100) NOT NULL,
    permission_code VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    is_system_permission BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 用户角色关系表
CREATE TABLE mh_auth_user_roles (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    user_type VARCHAR(20) NOT NULL, -- 'ADMIN' or 'TENANT'
    role_id VARCHAR(50) NOT NULL REFERENCES mh_auth_roles(id),
    granted_by VARCHAR(50),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, user_type, role_id)
);

-- 6. 角色权限关系表
CREATE TABLE mh_auth_role_permissions (
    id VARCHAR(50) PRIMARY KEY,
    role_id VARCHAR(50) NOT NULL REFERENCES mh_auth_roles(id),
    permission_id VARCHAR(50) NOT NULL REFERENCES mh_auth_permissions(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- 7. 审计日志表
CREATE TABLE mh_auth_audit_logs (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    user_type VARCHAR(20),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    resource_id VARCHAR(50),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. 会话表
CREATE TABLE mh_auth_sessions (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_mh_auth_tenant_users_tenant ON mh_auth_tenant_users(tenant_id);
CREATE INDEX idx_mh_auth_user_roles_user ON mh_auth_user_roles(user_id, user_type);
CREATE INDEX idx_mh_auth_audit_logs_user ON mh_auth_audit_logs(user_id, user_type);
CREATE INDEX idx_mh_auth_audit_logs_created ON mh_auth_audit_logs(created_at);
CREATE INDEX idx_mh_auth_sessions_user ON mh_auth_sessions(user_id, user_type);
CREATE INDEX idx_mh_auth_sessions_token ON mh_auth_sessions(session_token);

-- 插入系统默认数据
INSERT INTO auth_roles (id, role_name, role_code, description, is_system_role) VALUES
('ROLE_SUPER_ADMIN', '超级管理员', 'SUPER_ADMIN', '系统超级管理员', true),
('ROLE_TENANT_ADMIN', '租户管理员', 'TENANT_ADMIN', '租户管理员', true),
('ROLE_TENANT_USER', '租户用户', 'TENANT_USER', '普通租户用户', true),
('ROLE_STRATEGY_MANAGER', '策略管理员', 'STRATEGY_MANAGER', '策略管理员', true),
('ROLE_RISK_MANAGER', '风控管理员', 'RISK_MANAGER', '风控管理员', true);

INSERT INTO auth_permissions (id, permission_name, permission_code, resource, action, is_system_permission) VALUES
('PERM_USER_READ', '用户查看', 'user:read', 'user', 'read', true),
('PERM_USER_WRITE', '用户管理', 'user:write', 'user', 'write', true),
('PERM_STRATEGY_READ', '策略查看', 'strategy:read', 'strategy', 'read', true),
('PERM_STRATEGY_WRITE', '策略管理', 'strategy:write', 'strategy', 'write', true),
('PERM_RISK_READ', '风控查看', 'risk:read', 'risk', 'read', true),
('PERM_RISK_WRITE', '风控管理', 'risk:write', 'risk', 'write', true);
