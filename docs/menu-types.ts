/**
 * Saturn MouseHunter 菜单模块 - TypeScript DTO定义
 *
 * 这个文件包含所有菜单相关的TypeScript类型定义，确保前端与API的类型安全
 */

// ============================================================================
// 基础类型定义
// ============================================================================

/**
 * 菜单类型枚举
 */
export enum MenuType {
  MENU = 'menu',
  BUTTON = 'button',
  TAB = 'tab'
}

/**
 * 用户类型枚举
 */
export enum UserType {
  ADMIN = 'ADMIN',
  TENANT = 'TENANT',
  LIMITED = 'LIMITED'
}

/**
 * 菜单状态枚举
 */
export enum MenuStatus {
  ACTIVE = 'active',
  DISABLED = 'disabled'
}

// ============================================================================
// 核心DTO定义
// ============================================================================

/**
 * 菜单项DTO - 基础菜单数据结构
 */
export interface MenuItemDTO {
  /** 菜单唯一ID */
  id: string;

  /** 菜单名称 (英文标识符) */
  name: string;

  /** 显示标题 (中文) */
  title: string;

  /** 英文标题 */
  title_en?: string;

  /** 路由路径 */
  path?: string;

  /** 组件名称 */
  component?: string;

  /** 图标类名 */
  icon?: string;

  /** 表情图标 */
  emoji?: string;

  /** 父菜单ID */
  parent_id?: string;

  /** 所需权限 */
  permission?: string;

  /** 菜单类型 */
  menu_type: MenuType;

  /** 排序值 (数字越小越靠前) */
  sort_order: number;

  /** 是否隐藏 */
  is_hidden: boolean;

  /** 是否外部链接 */
  is_external?: boolean;

  /** 菜单状态 */
  status: MenuStatus;

  /** 元数据 */
  meta?: Record<string, any>;

  /** 子菜单列表 */
  children?: MenuItemDTO[];
}

/**
 * 用户菜单响应DTO - API返回的用户菜单数据
 */
export interface UserMenuResponseDTO {
  /** 用户ID */
  user_id: string;

  /** 用户类型 */
  user_type: UserType;

  /** 用户权限列表 */
  permissions: string[];

  /** 可访问菜单树 */
  menus: MenuItemDTO[];

  /** 更新时间 (ISO格式) */
  updated_at: string;
}

/**
 * 菜单权限检查DTO - 权限验证结果
 */
export interface MenuPermissionCheckDTO {
  /** 菜单ID */
  menu_id: string;

  /** 所需权限 */
  permission: string;

  /** 是否有权限 */
  has_permission: boolean;
}

/**
 * 菜单统计DTO - 菜单使用统计数据
 */
export interface MenuStatsDTO {
  /** 菜单总数 */
  total_menus: number;

  /** 可访问菜单数 */
  accessible_menus: number;

  /** 权限覆盖率 (0-100) */
  permission_coverage: number;

  /** 菜单使用统计 {菜单ID: 使用次数} */
  menu_usage: Record<string, number>;
}

// ============================================================================
// API请求/响应类型
// ============================================================================

/**
 * API错误响应DTO
 */
export interface APIErrorDTO {
  /** 错误描述 */
  detail: string;

  /** HTTP状态码 */
  status_code: number;
}

/**
 * API基础响应包装器
 */
export interface APIResponse<T> {
  /** 响应数据 */
  data?: T;

  /** 是否成功 */
  success: boolean;

  /** 错误信息 */
  error?: APIErrorDTO;
}

// ============================================================================
// 常量定义
// ============================================================================

/**
 * 系统核心菜单ID常量
 */
export const MENU_IDS = {
  // 核心业务模块
  DASHBOARD: 'dashboard',
  MARKET_CONFIG: 'market_config',
  TRADING_CALENDAR: 'trading_calendar',

  // 池管理模块
  INSTRUMENT_POOL: 'instrument_pool',
  BENCHMARK_POOL: 'benchmark_pool',
  POOL_INTERSECTION: 'pool_intersection',

  // 基础设施模块
  PROXY_POOL: 'proxy_pool',
  KLINE_MANAGEMENT: 'kline_management',
  COOKIE_MANAGEMENT: 'cookie_management',

  // 认证权限模块
  AUTH_SERVICE: 'auth_service',
  USER_MANAGEMENT: 'user_management',
  ROLE_MANAGEMENT: 'role_management',
  PERMISSION_MANAGEMENT: 'permission_management',

  // 高级功能模块
  STRATEGY_ENGINE: 'strategy_engine',
  UNIVERSE: 'universe',
  API_EXPLORER: 'api_explorer',

  // 开发工具模块
  TABLE_DEMO: 'table_demo',
  SKIN_THEME_DEMO: 'skin_theme_demo',
  LOGS: 'logs'
} as const;

/**
 * 菜单权限常量
 */
export const MENU_PERMISSIONS = {
  // 核心业务权限
  DASHBOARD: 'menu:dashboard',
  MARKET_CONFIG: 'menu:market_config',
  TRADING_CALENDAR: 'menu:trading_calendar',
  TRADING_CALENDAR_READ: 'trading_calendar:read',
  TRADING_CALENDAR_WRITE: 'trading_calendar:write',

  // 池管理权限
  INSTRUMENT_POOL: 'menu:instrument_pool',
  BENCHMARK_POOL: 'menu:benchmark_pool',
  POOL_INTERSECTION: 'menu:pool_intersection',

  // 基础设施权限
  PROXY_POOL: 'menu:proxy_pool',
  KLINE_MANAGEMENT: 'menu:kline_management',
  COOKIE_MANAGEMENT: 'menu:cookie_management',

  // 认证权限
  AUTH_SERVICE: 'menu:auth_service',
  USER_MANAGEMENT: 'menu:user_management',
  USER_READ: 'user:read',
  ROLE_MANAGEMENT: 'menu:role_management',
  ROLE_READ: 'role:read',
  PERMISSION_MANAGEMENT: 'menu:permission_management',

  // 高级功能权限
  STRATEGY_ENGINE: 'menu:strategy_engine',
  UNIVERSE: 'menu:universe',
  API_EXPLORER: 'menu:api_explorer',

  // 开发工具权限
  TABLE_DEMO: 'menu:table_demo',
  SKIN_THEME_DEMO: 'menu:skin_theme_demo',
  LOGS: 'menu:logs'
} as const;

/**
 * API端点常量
 */
export const API_ENDPOINTS = {
  BASE_URL: 'http://localhost:8080/api/v1',

  // 菜单相关端点
  USER_MENUS: '/auth/user-menus',
  CHECK_MENU_PERMISSION: '/auth/check-menu-permission',
  MENU_STATS: '/auth/menu-stats',
  MENU_TREE: '/menus/tree',
  USER_MENUS_BY_ID: '/users/{user_id}/menus'
} as const;

// ============================================================================
// 工具类型
// ============================================================================

/**
 * 菜单ID类型 - 限制为预定义的菜单ID
 */
export type MenuID = typeof MENU_IDS[keyof typeof MENU_IDS];

/**
 * 菜单权限类型 - 限制为预定义的权限
 */
export type MenuPermission = typeof MENU_PERMISSIONS[keyof typeof MENU_PERMISSIONS];

/**
 * 菜单树节点类型 - 递归菜单结构
 */
export type MenuTreeNode = MenuItemDTO & {
  children: MenuTreeNode[];
};

/**
 * 扁平菜单映射类型 - 用于快速查找
 */
export type MenuMap = Record<string, MenuItemDTO>;

// ============================================================================
// 类型守卫函数
// ============================================================================

/**
 * 检查是否为有效的菜单项
 */
export function isValidMenuItemDTO(obj: any): obj is MenuItemDTO {
  return (
    obj &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.sort_order === 'number' &&
    typeof obj.is_hidden === 'boolean' &&
    Object.values(MenuStatus).includes(obj.status)
  );
}

/**
 * 检查是否为有效的用户菜单响应
 */
export function isValidUserMenuResponseDTO(obj: any): obj is UserMenuResponseDTO {
  return (
    obj &&
    typeof obj.user_id === 'string' &&
    Object.values(UserType).includes(obj.user_type) &&
    Array.isArray(obj.permissions) &&
    Array.isArray(obj.menus) &&
    typeof obj.updated_at === 'string'
  );
}

/**
 * 检查是否为API错误响应
 */
export function isAPIErrorDTO(obj: any): obj is APIErrorDTO {
  return (
    obj &&
    typeof obj.detail === 'string' &&
    typeof obj.status_code === 'number'
  );
}