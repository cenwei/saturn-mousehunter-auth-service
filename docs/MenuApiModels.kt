/**
 * Saturn MouseHunter 菜单模块 - Kotlin Quickly DTO定义
 *
 * 这个文件包含所有菜单相关的Kotlin数据类定义，确保与API的类型安全
 * 使用Kotlin Quickly框架进行序列化
 */

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// ============================================================================
// 基础枚举定义
// ============================================================================

/**
 * 菜单类型枚举
 */
@Serializable
enum class MenuType {
    @SerialName("menu")
    MENU,

    @SerialName("button")
    BUTTON,

    @SerialName("tab")
    TAB
}

/**
 * 用户类型枚举
 */
@Serializable
enum class UserType {
    @SerialName("ADMIN")
    ADMIN,

    @SerialName("TENANT")
    TENANT,

    @SerialName("LIMITED")
    LIMITED
}

/**
 * 菜单状态枚举
 */
@Serializable
enum class MenuStatus {
    @SerialName("active")
    ACTIVE,

    @SerialName("disabled")
    DISABLED
}

// ============================================================================
// 核心DTO定义
// ============================================================================

/**
 * 菜单项DTO - 基础菜单数据结构
 */
@Serializable
data class MenuItemDTO(
    /** 菜单唯一ID */
    @SerialName("id")
    val id: String,

    /** 菜单名称 (英文标识符) */
    @SerialName("name")
    val name: String,

    /** 显示标题 (中文) */
    @SerialName("title")
    val title: String,

    /** 英文标题 */
    @SerialName("title_en")
    val titleEn: String? = null,

    /** 路由路径 */
    @SerialName("path")
    val path: String? = null,

    /** 组件名称 */
    @SerialName("component")
    val component: String? = null,

    /** 图标类名 */
    @SerialName("icon")
    val icon: String? = null,

    /** 表情图标 */
    @SerialName("emoji")
    val emoji: String? = null,

    /** 父菜单ID */
    @SerialName("parent_id")
    val parentId: String? = null,

    /** 所需权限 */
    @SerialName("permission")
    val permission: String? = null,

    /** 菜单类型 */
    @SerialName("menu_type")
    val menuType: MenuType,

    /** 排序值 (数字越小越靠前) */
    @SerialName("sort_order")
    val sortOrder: Int,

    /** 是否隐藏 */
    @SerialName("is_hidden")
    val isHidden: Boolean,

    /** 是否外部链接 */
    @SerialName("is_external")
    val isExternal: Boolean = false,

    /** 菜单状态 */
    @SerialName("status")
    val status: String,

    /** 元数据 */
    @SerialName("meta")
    val meta: Map<String, String> = emptyMap(),

    /** 子菜单列表 */
    @SerialName("children")
    val children: List<MenuItemDTO> = emptyList()
)

/**
 * 用户菜单响应DTO - API返回的用户菜单数据
 */
@Serializable
data class UserMenuResponseDTO(
    /** 用户ID */
    @SerialName("user_id")
    val userId: String,

    /** 用户类型 */
    @SerialName("user_type")
    val userType: UserType,

    /** 用户权限列表 */
    @SerialName("permissions")
    val permissions: List<String>,

    /** 可访问菜单树 */
    @SerialName("menus")
    val menus: List<MenuItemDTO>,

    /** 更新时间 (ISO格式) */
    @SerialName("updated_at")
    val updatedAt: String
)

/**
 * 菜单权限检查DTO - 权限验证结果
 */
@Serializable
data class MenuPermissionCheckDTO(
    /** 菜单ID */
    @SerialName("menu_id")
    val menuId: String,

    /** 所需权限 */
    @SerialName("permission")
    val permission: String,

    /** 是否有权限 */
    @SerialName("has_permission")
    val hasPermission: Boolean
)

/**
 * 菜单统计DTO - 菜单使用统计数据
 */
@Serializable
data class MenuStatsDTO(
    /** 菜单总数 */
    @SerialName("total_menus")
    val totalMenus: Int,

    /** 可访问菜单数 */
    @SerialName("accessible_menus")
    val accessibleMenus: Int,

    /** 权限覆盖率 (0-100) */
    @SerialName("permission_coverage")
    val permissionCoverage: Double,

    /** 菜单使用统计 {菜单ID: 使用次数} */
    @SerialName("menu_usage")
    val menuUsage: Map<String, Int>
)

// ============================================================================
// API错误响应类型
// ============================================================================

/**
 * API错误响应DTO
 */
@Serializable
data class APIErrorDTO(
    /** 错误描述 */
    @SerialName("detail")
    val detail: String,

    /** HTTP状态码 */
    @SerialName("status_code")
    val statusCode: Int
)

/**
 * API基础响应包装器
 */
@Serializable
data class APIResponse<T>(
    /** 响应数据 */
    @SerialName("data")
    val data: T? = null,

    /** 是否成功 */
    @SerialName("success")
    val success: Boolean,

    /** 错误信息 */
    @SerialName("error")
    val error: APIErrorDTO? = null
)

// ============================================================================
// 常量定义
// ============================================================================

/**
 * 系统核心菜单ID常量
 */
object MenuIds {
    // 核心业务模块
    const val DASHBOARD = "dashboard"
    const val MARKET_CONFIG = "market_config"
    const val TRADING_CALENDAR = "trading_calendar"

    // 池管理模块
    const val INSTRUMENT_POOL = "instrument_pool"
    const val BENCHMARK_POOL = "benchmark_pool"
    const val POOL_INTERSECTION = "pool_intersection"

    // 基础设施模块
    const val PROXY_POOL = "proxy_pool"
    const val KLINE_MANAGEMENT = "kline_management"
    const val COOKIE_MANAGEMENT = "cookie_management"

    // 认证权限模块
    const val AUTH_SERVICE = "auth_service"
    const val USER_MANAGEMENT = "user_management"
    const val ROLE_MANAGEMENT = "role_management"
    const val PERMISSION_MANAGEMENT = "permission_management"

    // 高级功能模块
    const val STRATEGY_ENGINE = "strategy_engine"
    const val UNIVERSE = "universe"
    const val API_EXPLORER = "api_explorer"

    // 开发工具模块
    const val TABLE_DEMO = "table_demo"
    const val SKIN_THEME_DEMO = "skin_theme_demo"
    const val LOGS = "logs"
}

/**
 * 菜单权限常量
 */
object MenuPermissions {
    // 核心业务权限
    const val DASHBOARD = "menu:dashboard"
    const val MARKET_CONFIG = "menu:market_config"
    const val TRADING_CALENDAR = "menu:trading_calendar"
    const val TRADING_CALENDAR_READ = "trading_calendar:read"
    const val TRADING_CALENDAR_WRITE = "trading_calendar:write"

    // 池管理权限
    const val INSTRUMENT_POOL = "menu:instrument_pool"
    const val BENCHMARK_POOL = "menu:benchmark_pool"
    const val POOL_INTERSECTION = "menu:pool_intersection"

    // 基础设施权限
    const val PROXY_POOL = "menu:proxy_pool"
    const val KLINE_MANAGEMENT = "menu:kline_management"
    const val COOKIE_MANAGEMENT = "menu:cookie_management"

    // 认证权限
    const val AUTH_SERVICE = "menu:auth_service"
    const val USER_MANAGEMENT = "menu:user_management"
    const val USER_READ = "user:read"
    const val ROLE_MANAGEMENT = "menu:role_management"
    const val ROLE_READ = "role:read"
    const val PERMISSION_MANAGEMENT = "menu:permission_management"

    // 高级功能权限
    const val STRATEGY_ENGINE = "menu:strategy_engine"
    const val UNIVERSE = "menu:universe"
    const val API_EXPLORER = "menu:api_explorer"

    // 开发工具权限
    const val TABLE_DEMO = "menu:table_demo"
    const val SKIN_THEME_DEMO = "menu:skin_theme_demo"
    const val LOGS = "menu:logs"
}

/**
 * API端点常量
 */
object ApiEndpoints {
    const val BASE_URL = "http://192.168.8.168:8001/api/v1"

    // 菜单相关端点
    const val USER_MENUS = "/auth/user-menus"
    const val CHECK_MENU_PERMISSION = "/auth/check-menu-permission"
    const val MENU_STATS = "/auth/menu-stats"
    const val MENU_TREE = "/menus/tree"
    const val USER_MENUS_BY_ID = "/users/{user_id}/menus"
}