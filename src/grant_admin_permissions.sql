-- =====================================================
-- 快速授权脚本 - 仅授权基础管理员权限
-- 注意：请先运行 complete_auth_init.sql 进行完整初始化
-- =====================================================

-- 1. 确保超级管理员角色存在（如果完整初始化未运行）
INSERT INTO mh_auth_roles (id, role_code, role_name, description, scope, is_system_role, is_active, created_at, updated_at)
VALUES ('ROLE_SUPER_ADMIN', 'super_admin', '超级管理员', '拥有所有权限的系统管理员', 'SYSTEM', true, true, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET updated_at = NOW();

-- 2. 确保基础权限存在（如果完整初始化未运行）
INSERT INTO mh_auth_permissions (id, permission_code, permission_name, resource, action, description, is_system_permission, created_at, updated_at)
VALUES
  ('PERM_USER_READ', 'user:read', '用户查看', 'user', 'read', '查看用户信息', true, NOW(), NOW()),
  ('PERM_USER_WRITE', 'user:write', '用户管理', 'user', 'write', '创建更新删除用户', true, NOW(), NOW()),
  ('PERM_ROLE_READ', 'role:read', '角色查看', 'role', 'read', '查看角色信息', true, NOW(), NOW()),
  ('PERM_ROLE_WRITE', 'role:write', '角色管理', 'role', 'write', '创建更新删除角色', true, NOW(), NOW()),
  ('PERM_SYSTEM_ADMIN', 'system:admin', '系统管理', 'system', 'admin', '系统管理权限', true, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET updated_at = NOW();

-- 3. 确保角色权限关联存在
INSERT INTO mh_auth_role_permissions (id, role_id, permission_id, granted_by, granted_at, created_at, updated_at)
VALUES
  ('RP_SUPER_ADMIN_USER_READ', 'ROLE_SUPER_ADMIN', 'PERM_USER_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_USER_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_USER_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_READ', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_READ', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_ROLE_WRITE', 'ROLE_SUPER_ADMIN', 'PERM_ROLE_WRITE', 'SYSTEM', NOW(), NOW(), NOW()),
  ('RP_SUPER_ADMIN_SYSTEM', 'ROLE_SUPER_ADMIN', 'PERM_SYSTEM_ADMIN', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 4. 给 admin 用户分配超级管理员角色
INSERT INTO mh_auth_user_roles (id, user_id, user_type, role_id, granted_by, granted_at, created_at, updated_at)
VALUES ('UR_ADMIN_001_SUPER', 'ADMIN_001', 'ADMIN', 'ROLE_SUPER_ADMIN', 'SYSTEM', NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 验证数据
SELECT 'Admin user permissions:' as info;
SELECT DISTINCT p.permission_code, p.permission_name
FROM mh_auth_user_roles ur
JOIN mh_auth_role_permissions rp ON ur.role_id = rp.role_id
JOIN mh_auth_permissions p ON rp.permission_id = p.id
WHERE ur.user_id = 'ADMIN_001' AND ur.user_type = 'ADMIN';
