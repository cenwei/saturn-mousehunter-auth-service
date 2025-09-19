-- =====================================================
-- Saturn MouseHunter 认证服务 - 完整数据库初始化脚本
-- =====================================================

-- 1. 创建完整的角色数据
INSERT INTO mh_auth_roles (id, role_code, role_name, description, scope, is_system_role, is_active, created_at, updated_at)
VALUES
  -- 系统级角色
  ('ROLE_SUPER_ADMIN', 'super_admin', '超级管理员', '拥有所有权限的系统管理员', 'SYSTEM', true, true, NOW(), NOW()),

  -- 租户级角色
  ('ROLE_TENANT_ADMIN', 'tenant_admin', '租户管理员', '租户内的管理员角色', 'TENANT', true, true, NOW(), NOW()),
  ('ROLE_TENANT_USER', 'tenant_user', '租户用户', '普通租户用户角色', 'TENANT', true, true, NOW(), NOW()),

  -- 业务专用角色
  ('ROLE_STRATEGY_MANAGER', 'strategy_manager', '策略管理员', '负责策略管理的专用角色', 'GLOBAL', true, true, NOW(), NOW()),
  ('ROLE_RISK_MANAGER', 'risk_manager', '风控管理员', '负责风险控制的专用角色', 'GLOBAL', true, true, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  role_name = EXCLUDED.role_name,
  description = EXCLUDED.description,
  scope = EXCLUDED.scope,
  updated_at = NOW();

-- 2. 创建完整的权限数据
INSERT INTO mh_auth_permissions (id, permission_code, permission_name, resource, action, description, is_system_permission, created_at, updated_at)
VALUES
  -- 用户管理权限
  ('PERM_USER_READ', 'user:read', '用户查看', 'user', 'read', '查看用户信息和列表', true, NOW(), NOW()),
  ('PERM_USER_WRITE', 'user:write', '用户管理', 'user', 'write', '创建、更新、删除用户', true, NOW(), NOW()),
  ('PERM_USER_CREATE', 'user:create', '用户创建', 'user', 'create', '创建新用户', true, NOW(), NOW()),
  ('PERM_USER_UPDATE', 'user:update', '用户更新', 'user', 'update', '更新用户信息', true, NOW(), NOW()),
  ('PERM_USER_DELETE', 'user:delete', '用户删除', 'user', 'delete', '删除用户', true, NOW(), NOW()),

  -- 角色管理权限
  ('PERM_ROLE_READ', 'role:read', '角色查看', 'role', 'read', '查看角色信息和列表', true, NOW(), NOW()),
  ('PERM_ROLE_WRITE', 'role:write', '角色管理', 'role', 'write', '创建、更新、删除角色', true, NOW(), NOW()),
  ('PERM_ROLE_CREATE', 'role:create', '角色创建', 'role', 'create', '创建新角色', true, NOW(), NOW()),
  ('PERM_ROLE_UPDATE', 'role:update', '角色更新', 'role', 'update', '更新角色信息', true, NOW(), NOW()),
  ('PERM_ROLE_DELETE', 'role:delete', '角色删除', 'role', 'delete', '删除角色', true, NOW(), NOW()),
  ('PERM_ROLE_ASSIGN', 'role:assign', '角色分配', 'role', 'assign', '分配角色给用户', true, NOW(), NOW()),

  -- 权限管理权限
  ('PERM_PERMISSION_READ', 'permission:read', '权限查看', 'permission', 'read', '查看权限信息和列表', true, NOW(), NOW()),
  ('PERM_PERMISSION_WRITE', 'permission:write', '权限管理', 'permission', 'write', '创建、更新、删除权限', true, NOW(), NOW()),

  -- 系统管理权限
  ('PERM_SYSTEM_ADMIN', 'system:admin', '系统管理', 'system', 'admin', '系统级管理权限', true, NOW(), NOW()),
  ('PERM_SYSTEM_CONFIG', 'system:config', '系统配置', 'system', 'config', '系统配置管理', true, NOW(), NOW()),
  ('PERM_SYSTEM_MONITOR', 'system:monitor', '系统监控', 'system', 'monitor', '系统监控查看', true, NOW(), NOW()),

  -- 菜单访问权限
  ('PERM_MENU_DASHBOARD', 'menu:dashboard', '仪表盘菜单', 'menu', 'access', '访问仪表盘菜单', false, NOW(), NOW()),
  ('PERM_MENU_USER_MGMT', 'menu:user_management', '用户管理菜单', 'menu', 'access', '访问用户管理菜单', false, NOW(), NOW()),
  ('PERM_MENU_ROLE_MGMT', 'menu:role_management', '角色管理菜单', 'menu', 'access', '访问角色管理菜单', false, NOW(), NOW()),
  ('PERM_MENU_PERMISSION_MGMT', 'menu:permission_management', '权限管理菜单', 'menu', 'access', '访问权限管理菜单', false, NOW(), NOW()),
  ('PERM_MENU_SYSTEM', 'menu:system', '系统设置菜单', 'menu', 'access', '访问系统设置菜单', false, NOW(), NOW()),
  ('PERM_MENU_STRATEGY', 'menu:strategy', '策略管理菜单', 'menu', 'access', '访问策略管理菜单', false, NOW(), NOW()),
  ('PERM_MENU_RISK', 'menu:risk', '风控管理菜单', 'menu', 'access', '访问风控管理菜单', false, NOW(), NOW()),
  ('PERM_MENU_REPORTS', 'menu:reports', '报表菜单', 'menu', 'access', '访问报表菜单', false, NOW(), NOW()),
  ('PERM_MENU_AUDIT', 'menu:audit', '审计日志菜单', 'menu', 'access', '访问审计日志菜单', false, NOW(), NOW()),

  -- 业务功能权限
  ('PERM_STRATEGY_READ', 'strategy:read', '策略查看', 'strategy', 'read', '查看策略信息', false, NOW(), NOW()),
  ('PERM_STRATEGY_WRITE', 'strategy:write', '策略管理', 'strategy', 'write', '创建、更新、删除策略', false, NOW(), NOW()),
  ('PERM_STRATEGY_EXECUTE', 'strategy:execute', '策略执行', 'strategy', 'execute', '执行策略操作', false, NOW(), NOW()),

  ('PERM_RISK_READ', 'risk:read', '风控查看', 'risk', 'read', '查看风控信息', false, NOW(), NOW()),
  ('PERM_RISK_WRITE', 'risk:write', '风控管理', 'risk', 'write', '创建、更新、删除风控规则', false, NOW(), NOW()),
  ('PERM_RISK_MONITOR', 'risk:monitor', '风控监控', 'risk', 'monitor', '风控实时监控', false, NOW(), NOW()),

  -- 审计权限
  ('PERM_AUDIT_READ', 'audit:read', '审计查看', 'audit', 'read', '查看审计日志', false, NOW(), NOW()),
  ('PERM_AUDIT_EXPORT', 'audit:export', '审计导出', 'audit', 'export', '导出审计数据', false, NOW(), NOW()),

  -- 报表权限
  ('PERM_REPORT_READ', 'report:read', '报表查看', 'report', 'read', '查看各类报表', false, NOW(), NOW()),
  ('PERM_REPORT_EXPORT', 'report:export', '报表导出', 'report', 'export', '导出报表数据', false, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  permission_name = EXCLUDED.permission_name,
  description = EXCLUDED.description,
  updated_at = NOW();

-- 3. 创建角色权限关联 - 超级管理员 (拥有所有权限)
INSERT INTO mh_auth_role_permissions (id, role_id, permission_id, granted_by, granted_at, created_at, updated_at)
VALUES
  -- 超级管理员 - 用户管理权限
  ('RP_SUPER_ADMIN_USER_READ', 'ROLE_SUPER_ADMIN', 'PERM_USER_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_USER_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_USER_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_USER_CREATE', 'ROLE_SUPER_ADMIN', 'PERM_USER_CREATE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_USER_UPDATE', 'ROLE_SUPER_ADMIN', 'PERM_USER_UPDATE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_USER_DELETE', 'ROLE_SUPER_ADMIN', 'PERM_USER_DELETE', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 超级管理员 - 角色管理权限
  ('RP_SUPER_ADMIN_ROLE_READ', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_CREATE', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_CREATE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_UPDATE', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_UPDATE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_DELETE', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_DELETE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_ASSIGN', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_ASSIGN', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 超级管理员 - 权限管理权限
  ('RP_SUPER_ADMIN_PERMISSION_READ', 'ROLE_SUPER_ADMIN', 'PERM_PERMISSION_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_PERMISSION_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_PERMISSION_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 超级管理员 - 系统管理权限
  ('RP_SUPER_ADMIN_SYSTEM', 'ROLE_SUPER_ADMIN', 'PERM_SYSTEM_ADMIN', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_SYSTEM_CONFIG', 'ROLE_SUPER_ADMIN', 'PERM_SYSTEM_CONFIG', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_SYSTEM_MONITOR', 'ROLE_SUPER_ADMIN', 'PERM_SYSTEM_MONITOR', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 超级管理员 - 所有菜单权限
  ('RP_SUPER_ADMIN_MENU_DASHBOARD', 'ROLE_SUPER_ADMIN', 'PERM_MENU_DASHBOARD', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_USER', 'ROLE_SUPER_ADMIN', 'PERM_MENU_USER_MGMT', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_ROLE', 'ROLE_SUPER_ADMIN', 'PERM_MENU_ROLE_MGMT', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_PERMISSION', 'ROLE_SUPER_ADMIN', 'PERM_MENU_PERMISSION_MGMT', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_SYSTEM', 'ROLE_SUPER_ADMIN', 'PERM_MENU_SYSTEM', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_STRATEGY', 'ROLE_SUPER_ADMIN', 'PERM_MENU_STRATEGY', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_RISK', 'ROLE_SUPER_ADMIN', 'PERM_MENU_RISK', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_REPORTS', 'ROLE_SUPER_ADMIN', 'PERM_MENU_REPORTS', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_MENU_AUDIT', 'ROLE_SUPER_ADMIN', 'PERM_MENU_AUDIT', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 超级管理员 - 业务权限
  ('RP_SUPER_ADMIN_STRATEGY_READ', 'ROLE_SUPER_ADMIN', 'PERM_STRATEGY_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_STRATEGY_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_STRATEGY_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_STRATEGY_EXECUTE', 'ROLE_SUPER_ADMIN', 'PERM_STRATEGY_EXECUTE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_RISK_READ', 'ROLE_SUPER_ADMIN', 'PERM_RISK_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_RISK_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_RISK_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_RISK_MONITOR', 'ROLE_SUPER_ADMIN', 'PERM_RISK_MONITOR', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_AUDIT_READ', 'ROLE_SUPER_ADMIN', 'PERM_AUDIT_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_AUDIT_EXPORT', 'ROLE_SUPER_ADMIN', 'PERM_AUDIT_EXPORT', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_REPORT_READ', 'ROLE_SUPER_ADMIN', 'PERM_REPORT_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_REPORT_EXPORT', 'ROLE_SUPER_ADMIN', 'PERM_REPORT_EXPORT', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 4. 创建角色权限关联 - 租户管理员
INSERT INTO mh_auth_role_permissions (id, role_id, permission_id, granted_by, granted_at, created_at, updated_at)
VALUES
  -- 租户管理员 - 用户管理权限 (租户范围内)
  ('RP_TENANT_ADMIN_USER_READ', 'ROLE_TENANT_ADMIN', 'PERM_USER_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_USER_CREATE', 'ROLE_TENANT_ADMIN', 'PERM_USER_CREATE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_USER_UPDATE', 'ROLE_TENANT_ADMIN', 'PERM_USER_UPDATE', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 租户管理员 - 角色查看权限
  ('RP_TENANT_ADMIN_ROLE_READ', 'ROLE_TENANT_ADMIN', 'PERM_ROLE_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_ROLE_ASSIGN', 'ROLE_TENANT_ADMIN', 'PERM_ROLE_ASSIGN', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 租户管理员 - 菜单权限
  ('RP_TENANT_ADMIN_MENU_DASHBOARD', 'ROLE_TENANT_ADMIN', 'PERM_MENU_DASHBOARD', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_MENU_USER', 'ROLE_TENANT_ADMIN', 'PERM_MENU_USER_MGMT', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_MENU_STRATEGY', 'ROLE_TENANT_ADMIN', 'PERM_MENU_STRATEGY', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_MENU_REPORTS', 'ROLE_TENANT_ADMIN', 'PERM_MENU_REPORTS', 'SYSTEM', NOW(), NOW(), NOW()),

  -- 租户管理员 - 业务权限
  ('RP_TENANT_ADMIN_STRATEGY_READ', 'ROLE_TENANT_ADMIN', 'PERM_STRATEGY_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_STRATEGY_WRITE', 'ROLE_TENANT_ADMIN', 'PERM_STRATEGY_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_ADMIN_REPORT_READ', 'ROLE_TENANT_ADMIN', 'PERM_REPORT_READ', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 5. 创建角色权限关联 - 策略管理员
INSERT INTO mh_auth_role_permissions (id, role_id, permission_id, granted_by, granted_at, created_at, updated_at)
VALUES
  -- 策略管理员权限
  ('RP_STRATEGY_MGR_MENU_DASHBOARD', 'ROLE_STRATEGY_MANAGER', 'PERM_MENU_DASHBOARD', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_STRATEGY_MGR_MENU_STRATEGY', 'ROLE_STRATEGY_MANAGER', 'PERM_MENU_STRATEGY', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_STRATEGY_MGR_STRATEGY_READ', 'ROLE_STRATEGY_MANAGER', 'PERM_STRATEGY_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_STRATEGY_MGR_STRATEGY_WRITE', 'ROLE_STRATEGY_MANAGER', 'PERM_STRATEGY_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_STRATEGY_MGR_STRATEGY_EXECUTE', 'ROLE_STRATEGY_MANAGER', 'PERM_STRATEGY_EXECUTE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_STRATEGY_MGR_REPORT_READ', 'ROLE_STRATEGY_MANAGER', 'PERM_REPORT_READ', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 6. 创建角色权限关联 - 风控管理员
INSERT INTO mh_auth_role_permissions (id, role_id, permission_id, granted_by, granted_at, created_at, updated_at)
VALUES
  -- 风控管理员权限
  ('RP_RISK_MGR_MENU_DASHBOARD', 'ROLE_RISK_MANAGER', 'PERM_MENU_DASHBOARD', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_RISK_MGR_MENU_RISK', 'ROLE_RISK_MANAGER', 'PERM_MENU_RISK', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_RISK_MGR_RISK_READ', 'ROLE_RISK_MANAGER', 'PERM_RISK_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_RISK_MGR_RISK_WRITE', 'ROLE_RISK_MANAGER', 'PERM_RISK_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_RISK_MGR_RISK_MONITOR', 'ROLE_RISK_MANAGER', 'PERM_RISK_MONITOR', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_RISK_MGR_AUDIT_READ', 'ROLE_RISK_MANAGER', 'PERM_AUDIT_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_RISK_MGR_REPORT_READ', 'ROLE_RISK_MANAGER', 'PERM_REPORT_READ', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 7. 创建角色权限关联 - 租户用户
INSERT INTO mh_auth_role_permissions (id, role_id, permission_id, granted_by, granted_at, created_at, updated_at)
VALUES
  -- 租户用户基础权限
  ('RP_TENANT_USER_MENU_DASHBOARD', 'ROLE_TENANT_USER', 'PERM_MENU_DASHBOARD', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_USER_STRATEGY_READ', 'ROLE_TENANT_USER', 'PERM_STRATEGY_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_TENANT_USER_REPORT_READ', 'ROLE_TENANT_USER', 'PERM_REPORT_READ', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 8. 给默认admin用户分配超级管理员角色
INSERT INTO mh_auth_user_roles (id, user_id, user_type, role_id, granted_by, granted_at, created_at, updated_at)
VALUES ('UR_ADMIN_001_SUPER', 'ADMIN_001', 'ADMIN', 'ROLE_SUPER_ADMIN', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 9. 验证数据完整性
SELECT 'Roles created:' as info;
SELECT id, role_name, role_code, scope, is_system_role
FROM mh_auth_roles
ORDER BY is_system_role DESC, role_name;

SELECT 'Permissions created:' as info;
SELECT COUNT(*) as total_permissions,
       SUM(CASE WHEN is_system_permission THEN 1 ELSE 0 END) as system_permissions,
       SUM(CASE WHEN NOT is_system_permission THEN 1 ELSE 0 END) as business_permissions
FROM mh_auth_permissions;

SELECT 'Role-Permission associations:' as info;
SELECT r.role_name, COUNT(rp.permission_id) as permission_count
FROM mh_auth_roles r
LEFT JOIN mh_auth_role_permissions rp ON r.id = rp.role_id
GROUP BY r.id, r.role_name
ORDER BY permission_count DESC;

SELECT 'Admin user permissions:' as info;
SELECT DISTINCT p.permission_code, p.permission_name
FROM mh_auth_user_roles ur
JOIN mh_auth_role_permissions rp ON ur.role_id = rp.role_id
JOIN mh_auth_permissions p ON rp.permission_id = p.id
WHERE ur.user_id = 'ADMIN_001' AND ur.user_type = 'ADMIN'
ORDER BY p.permission_code;