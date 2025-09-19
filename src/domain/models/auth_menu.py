"""
认证服务 - 菜单权限模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class MenuType(str, Enum):
    """菜单类型"""
    MENU = "menu"      # 菜单项
    BUTTON = "button"  # 按钮
    TAB = "tab"        # 标签页


class MenuConfig(BaseModel):
    """菜单配置模型"""
    id: str = Field(..., description="菜单ID")
    name: str = Field(..., description="菜单名称")
    title: str = Field(..., description="菜单标题")
    title_en: Optional[str] = Field(None, description="英文标题")
    path: Optional[str] = Field(None, description="菜单路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="菜单图标")
    emoji: Optional[str] = Field(None, description="表情符号图标")
    parent_id: Optional[str] = Field(None, description="父菜单ID")
    permission: Optional[str] = Field(None, description="所需权限")
    menu_type: MenuType = Field(MenuType.MENU, description="菜单类型")
    sort_order: int = Field(0, description="排序顺序")
    is_hidden: bool = Field(False, description="是否隐藏")
    is_external: bool = Field(False, description="是否外部链接")
    status: str = Field("active", description="菜单状态")
    meta: Optional[Dict[str, Any]] = Field(None, description="菜单元数据")
    children: Optional[List['MenuConfig']] = Field(None, description="子菜单")

    class Config:
        from_attributes = True


class MenuTree(BaseModel):
    """菜单树结构"""
    id: str
    name: str
    title: str
    title_en: Optional[str] = None
    path: Optional[str] = None
    icon: Optional[str] = None
    emoji: Optional[str] = None
    permission: Optional[str] = None
    menu_type: MenuType = MenuType.MENU
    sort_order: int = 0
    is_hidden: bool = False
    status: str = "active"
    meta: Optional[Dict[str, Any]] = None
    children: List['MenuTree'] = []

    class Config:
        from_attributes = True


class UserMenuResponse(BaseModel):
    """用户菜单响应模型"""
    user_id: str = Field(..., description="用户ID")
    user_type: str = Field(..., description="用户类型")
    permissions: List[str] = Field(..., description="用户权限列表")
    menus: List[MenuTree] = Field(..., description="可访问菜单")
    updated_at: datetime = Field(..., description="更新时间")


class MenuPermissionCheck(BaseModel):
    """菜单权限检查模型"""
    menu_id: str = Field(..., description="菜单ID")
    permission: str = Field(..., description="所需权限")
    has_permission: bool = Field(..., description="是否有权限")


class MenuStatsResponse(BaseModel):
    """菜单统计响应"""
    total_menus: int = Field(..., description="菜单总数")
    accessible_menus: int = Field(..., description="可访问菜单数")
    permission_coverage: float = Field(..., description="权限覆盖率")
    menu_usage: Dict[str, int] = Field(..., description="菜单使用统计")


# Saturn MHC 完整菜单配置
SATURN_MHC_MENU_CONFIG = [
    # 🏠 核心模块
    MenuConfig(
        id="dashboard",
        name="dashboard",
        title="总览",
        title_en="Dashboard",
        path="/",
        component="Dashboard",
        icon="dashboard",
        emoji="🏠",
        permission="menu:dashboard",
        sort_order=1,
        meta={"title": "总览", "title_en": "Dashboard", "keepAlive": True}
    ),
    MenuConfig(
        id="market_config",
        name="market_config",
        title="市场配置",
        title_en="Market Config",
        path="/market-config",
        component="MarketConfig",
        icon="market",
        emoji="📊",
        permission="menu:market_config",
        sort_order=2,
        meta={"title": "市场配置", "title_en": "Market Config"}
    ),

    # 📅 交易相关
    MenuConfig(
        id="trading_calendar",
        name="trading_calendar",
        title="交易日历管理",
        title_en="Trading Calendar",
        path="/trading-calendar",
        component="TradingCalendar",
        icon="calendar",
        emoji="📅",
        permission="menu:trading_calendar",
        sort_order=3,
        meta={"title": "交易日历管理", "title_en": "Trading Calendar"},
        children=[
            MenuConfig(
                id="trading_calendar_table",
                name="trading_calendar_table",
                title="交易日历表格",
                title_en="Trading Calendar Table",
                path="/trading-calendar-table",
                component="TradingCalendarTable",
                parent_id="trading_calendar",
                permission="trading_calendar:read",
                sort_order=1,
                meta={"title": "交易日历表格", "title_en": "Trading Calendar Table"}
            )
        ]
    ),

    # 🎯 池管理
    MenuConfig(
        id="instrument_pool",
        name="instrument_pool",
        title="标的池管理",
        title_en="Instrument Pool",
        path="/instrument-pool",
        component="InstrumentPool",
        icon="pool",
        emoji="📈",
        permission="menu:instrument_pool",
        sort_order=4,
        meta={"title": "标的池管理", "title_en": "Instrument Pool"}
    ),
    MenuConfig(
        id="benchmark_pool",
        name="benchmark_pool",
        title="基准池管理",
        title_en="Pool Management",
        path="/benchmark-pool",
        component="BenchmarkPool",
        icon="pool",
        emoji="🎯",
        permission="menu:benchmark_pool",
        sort_order=5,
        meta={"title": "基准池管理", "title_en": "Pool Management"}
    ),
    MenuConfig(
        id="pool_intersection",
        name="pool_intersection",
        title="标的池交集",
        title_en="Pool Intersection",
        path="/pool-intersection",
        component="PoolIntersection",
        icon="intersection",
        emoji="🎯",
        permission="menu:pool_intersection",
        sort_order=6,
        meta={"title": "标的池交集", "title_en": "Pool Intersection"}
    ),

    # 🌐 基础设施
    MenuConfig(
        id="proxy_pool",
        name="proxy_pool",
        title="代理池管理",
        title_en="Proxy Pool",
        path="/proxy-pool",
        component="ProxyPool",
        icon="proxy",
        emoji="🌐",
        permission="menu:proxy_pool",
        sort_order=7,
        meta={"title": "代理池管理", "title_en": "Proxy Pool", "recently_updated": True}
    ),
    MenuConfig(
        id="kline_management",
        name="kline_management",
        title="K线数据管理",
        title_en="K-Line Management",
        path="/kline",
        component="KlineManagement",
        icon="kline",
        emoji="📈",
        permission="menu:kline_management",
        sort_order=8,
        meta={"title": "K线数据管理", "title_en": "K-Line Management"}
    ),
    MenuConfig(
        id="cookie_management",
        name="cookie_management",
        title="Cookie管理",
        title_en="Cookie Management",
        path="/cookie-management",
        component="CookieManagement",
        icon="cookie",
        emoji="🍪",
        permission="menu:cookie_management",
        sort_order=9,
        meta={"title": "Cookie管理", "title_en": "Cookie Management"}
    ),

    # 🔐 认证与权限
    MenuConfig(
        id="auth_service",
        name="auth_service",
        title="认证服务管理",
        title_en="Auth Service",
        path="/auth-service",
        component="AuthService",
        icon="auth",
        emoji="🔐",
        permission="menu:auth_service",
        sort_order=10,
        meta={"title": "认证服务管理", "title_en": "Auth Service"}
    ),
    MenuConfig(
        id="user_management",
        name="user_management",
        title="用户管理",
        title_en="User Management",
        path="/user-management",
        component="UserManagement",
        icon="users",
        emoji="👤",
        permission="menu:user_management",
        sort_order=11,
        meta={"title": "用户管理", "title_en": "User Management"},
        children=[
            MenuConfig(
                id="admin_users",
                name="admin_users",
                title="管理员用户",
                title_en="Admin Users",
                path="/user-management/admin",
                component="AdminUsers",
                parent_id="user_management",
                permission="user:read",
                sort_order=1,
                meta={"title": "管理员用户", "title_en": "Admin Users"}
            ),
            MenuConfig(
                id="tenant_users",
                name="tenant_users",
                title="租户用户",
                title_en="Tenant Users",
                path="/user-management/tenant",
                component="TenantUsers",
                parent_id="user_management",
                permission="user:read",
                sort_order=2,
                meta={"title": "租户用户", "title_en": "Tenant Users"}
            )
        ]
    ),
    MenuConfig(
        id="role_management",
        name="role_management",
        title="角色管理",
        title_en="Role Management",
        path="/role-management",
        component="RoleManagement",
        icon="role",
        emoji="👥",
        permission="menu:role_management",
        sort_order=12,
        meta={"title": "角色管理", "title_en": "Role Management"},
        children=[
            MenuConfig(
                id="role_list",
                name="role_list",
                title="角色列表",
                title_en="Role List",
                path="/role-management/list",
                component="RoleList",
                parent_id="role_management",
                permission="role:read",
                sort_order=1,
                meta={"title": "角色列表", "title_en": "Role List"}
            )
        ]
    ),
    MenuConfig(
        id="permission_management",
        name="permission_management",
        title="权限管理",
        title_en="Permission Management",
        path="/permission-management",
        component="PermissionManagement",
        icon="permission",
        emoji="🔐",
        permission="menu:permission_management",
        sort_order=13,
        meta={"title": "权限管理", "title_en": "Permission Management"}
    ),

    # 🚀 高级功能
    MenuConfig(
        id="strategy_engine",
        name="strategy_engine",
        title="策略引擎管理",
        title_en="Strategy Engine",
        path="/strategy-engine",
        component="StrategyEngine",
        icon="strategy",
        emoji="🚀",
        permission="menu:strategy_engine",
        sort_order=14,
        meta={"title": "策略引擎管理", "title_en": "Strategy Engine"}
    ),
    MenuConfig(
        id="universe",
        name="universe",
        title="标的池",
        title_en="Universe",
        path="/universe",
        component="Universe",
        icon="universe",
        permission="menu:universe",
        sort_order=15,
        meta={"title": "标的池", "title_en": "Universe"}
    ),
    MenuConfig(
        id="api_explorer",
        name="api_explorer",
        title="接口探索",
        title_en="API Explorer",
        path="/api-explorer",
        component="ApiExplorer",
        icon="api",
        permission="menu:api_explorer",
        sort_order=16,
        meta={"title": "接口探索", "title_en": "API Explorer"}
    ),

    # 🎨 开发与调试
    MenuConfig(
        id="table_demo",
        name="table_demo",
        title="表格控件演示",
        title_en="Table Demo",
        path="/table-demo",
        component="TableDemo",
        icon="table",
        emoji="📊",
        permission="menu:table_demo",
        sort_order=17,
        meta={"title": "表格控件演示", "title_en": "Table Demo"}
    ),
    MenuConfig(
        id="skin_theme_demo",
        name="skin_theme_demo",
        title="皮肤主题演示",
        title_en="Skin Theme Demo",
        path="/skin-theme-demo",
        component="SkinThemeDemo",
        icon="theme",
        emoji="🎨",
        permission="menu:skin_theme_demo",
        sort_order=18,
        meta={"title": "皮肤主题演示", "title_en": "Skin Theme Demo"}
    ),
    MenuConfig(
        id="logs",
        name="logs",
        title="日志",
        title_en="Logs",
        path="/logs",
        component="Logs",
        icon="logs",
        permission="menu:logs",
        sort_order=19,
        meta={"title": "日志", "title_en": "Logs"}
    )
]

# 权限映射配置
MENU_PERMISSIONS = {
    # 核心业务权限
    "menu:dashboard": ["ADMIN", "TENANT", "LIMITED"],
    "menu:market_config": ["ADMIN", "TENANT"],

    # 交易相关权限
    "menu:trading_calendar": ["ADMIN", "TENANT"],
    "trading_calendar:read": ["ADMIN", "TENANT"],
    "trading_calendar:write": ["ADMIN"],

    # 池管理权限
    "menu:instrument_pool": ["ADMIN", "TENANT"],
    "menu:benchmark_pool": ["ADMIN", "TENANT"],
    "menu:pool_intersection": ["ADMIN"],

    # 基础设施权限
    "menu:proxy_pool": ["ADMIN"],
    "menu:kline_management": ["ADMIN", "TENANT"],
    "menu:cookie_management": ["ADMIN"],

    # 认证权限
    "menu:auth_service": ["ADMIN"],
    "menu:user_management": ["ADMIN"],
    "user:read": ["ADMIN"],
    "menu:role_management": ["ADMIN"],
    "role:read": ["ADMIN"],
    "menu:permission_management": ["ADMIN"],

    # 高级功能权限
    "menu:strategy_engine": ["ADMIN", "TENANT"],
    "menu:universe": ["ADMIN", "TENANT"],
    "menu:api_explorer": ["ADMIN"],

    # 开发工具权限
    "menu:table_demo": ["ADMIN", "TENANT"],
    "menu:skin_theme_demo": ["ADMIN", "TENANT"],
    "menu:logs": ["ADMIN"]
}

# 保留原有菜单配置用于向后兼容
DEFAULT_MENU_CONFIG = [
    MenuConfig(
        id="dashboard",
        name="dashboard",
        title="仪表盘",
        path="/dashboard",
        component="Dashboard",
        icon="dashboard",
        permission="menu:dashboard",
        sort_order=1,
        meta={"title": "仪表盘", "keepAlive": True}
    ),
    MenuConfig(
        id="user_management",
        name="user_management",
        title="用户管理",
        path="/users",
        icon="users",
        permission="menu:user_management",
        sort_order=2,
        meta={"title": "用户管理"},
        children=[
            MenuConfig(
                id="admin_users",
                name="admin_users",
                title="管理员用户",
                path="/users/admin",
                component="AdminUsers",
                parent_id="user_management",
                permission="user:read",
                sort_order=1,
                meta={"title": "管理员用户"}
            ),
            MenuConfig(
                id="tenant_users",
                name="tenant_users",
                title="租户用户",
                path="/users/tenant",
                component="TenantUsers",
                parent_id="user_management",
                permission="user:read",
                sort_order=2,
                meta={"title": "租户用户"}
            )
        ]
    ),
    MenuConfig(
        id="role_management",
        name="role_management",
        title="角色管理",
        path="/roles",
        icon="role",
        permission="menu:role_management",
        sort_order=3,
        meta={"title": "角色管理"},
        children=[
            MenuConfig(
                id="role_list",
                name="role_list",
                title="角色列表",
                path="/roles/list",
                component="RoleList",
                parent_id="role_management",
                permission="role:read",
                sort_order=1,
                meta={"title": "角色列表"}
            ),
            MenuConfig(
                id="permission_list",
                name="permission_list",
                title="权限列表",
                path="/roles/permissions",
                component="PermissionList",
                parent_id="role_management",
                permission="role:read",
                sort_order=2,
                meta={"title": "权限列表"}
            )
        ]
    ),
    MenuConfig(
        id="strategy_management",
        name="strategy_management",
        title="策略管理",
        path="/strategy",
        icon="strategy",
        permission="menu:strategy",
        sort_order=4,
        meta={"title": "策略管理"},
        children=[
            MenuConfig(
                id="strategy_list",
                name="strategy_list",
                title="策略列表",
                path="/strategy/list",
                component="StrategyList",
                parent_id="strategy_management",
                permission="strategy:read",
                sort_order=1,
                meta={"title": "策略列表"}
            ),
            MenuConfig(
                id="strategy_create",
                name="strategy_create",
                title="创建策略",
                path="/strategy/create",
                component="StrategyCreate",
                parent_id="strategy_management",
                permission="strategy:write",
                sort_order=2,
                meta={"title": "创建策略"}
            )
        ]
    ),
    MenuConfig(
        id="risk_management",
        name="risk_management",
        title="风控管理",
        path="/risk",
        icon="risk",
        permission="menu:risk",
        sort_order=5,
        meta={"title": "风控管理"},
        children=[
            MenuConfig(
                id="risk_monitor",
                name="risk_monitor",
                title="风控监控",
                path="/risk/monitor",
                component="RiskMonitor",
                parent_id="risk_management",
                permission="risk:monitor",
                sort_order=1,
                meta={"title": "风控监控"}
            ),
            MenuConfig(
                id="risk_rules",
                name="risk_rules",
                title="风控规则",
                path="/risk/rules",
                component="RiskRules",
                parent_id="risk_management",
                permission="risk:write",
                sort_order=2,
                meta={"title": "风控规则"}
            )
        ]
    ),
    MenuConfig(
        id="system_management",
        name="system_management",
        title="系统设置",
        path="/system",
        icon="system",
        permission="menu:system",
        sort_order=6,
        meta={"title": "系统设置"},
        children=[
            MenuConfig(
                id="system_config",
                name="system_config",
                title="系统配置",
                path="/system/config",
                component="SystemConfig",
                parent_id="system_management",
                permission="system:config",
                sort_order=1,
                meta={"title": "系统配置"}
            ),
            MenuConfig(
                id="system_monitor",
                name="system_monitor",
                title="系统监控",
                path="/system/monitor",
                component="SystemMonitor",
                parent_id="system_management",
                permission="system:monitor",
                sort_order=2,
                meta={"title": "系统监控"}
            )
        ]
    ),
    MenuConfig(
        id="reports",
        name="reports",
        title="报表中心",
        path="/reports",
        icon="reports",
        permission="menu:reports",
        sort_order=7,
        meta={"title": "报表中心"},
        children=[
            MenuConfig(
                id="user_reports",
                name="user_reports",
                title="用户报表",
                path="/reports/users",
                component="UserReports",
                parent_id="reports",
                permission="report:read",
                sort_order=1,
                meta={"title": "用户报表"}
            ),
            MenuConfig(
                id="strategy_reports",
                name="strategy_reports",
                title="策略报表",
                path="/reports/strategy",
                component="StrategyReports",
                parent_id="reports",
                permission="report:read",
                sort_order=2,
                meta={"title": "策略报表"}
            )
        ]
    ),
    MenuConfig(
        id="audit_logs",
        name="audit_logs",
        title="审计日志",
        path="/audit",
        icon="audit",
        permission="menu:audit",
        sort_order=8,
        meta={"title": "审计日志"},
        children=[
            MenuConfig(
                id="login_logs",
                name="login_logs",
                title="登录日志",
                path="/audit/login",
                component="LoginLogs",
                parent_id="audit_logs",
                permission="audit:read",
                sort_order=1,
                meta={"title": "登录日志"}
            ),
            MenuConfig(
                id="operation_logs",
                name="operation_logs",
                title="操作日志",
                path="/audit/operation",
                component="OperationLogs",
                parent_id="audit_logs",
                permission="audit:read",
                sort_order=2,
                meta={"title": "操作日志"}
            )
        ]
    )
]