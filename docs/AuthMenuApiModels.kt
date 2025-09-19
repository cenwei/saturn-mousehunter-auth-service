/**
 * Saturn MouseHunter Auth Service - Menu Management API Models
 *
 * 用于Kotlin Quickly客户端的菜单管理序列化对象
 *
 * @version 1.0.0
 * @author Saturn MouseHunter Team
 * @date 2025-09-19
 *
 * API Base URL: http://192.168.8.168:8001/api/v1
 *
 * 维护规则:
 * 1. JSON字段变更时必须同步更新@SerialName映射
 * 2. API端点不允许随意修改，保持版本连续性
 */

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * 菜单类型枚举
 */
@Serializable
enum class MenuType(val value: String) {
    @SerialName("menu")
    MENU("menu"),

    @SerialName("button")
    BUTTON("button"),

    @SerialName("tab")
    TAB("tab")
}

/**
 * 菜单配置模型
 */
@Serializable
data class MenuConfig(
    @SerialName("id") val id: String,
    @SerialName("name") val name: String,
    @SerialName("title") val title: String,
    @SerialName("path") val path: String? = null,
    @SerialName("component") val component: String? = null,
    @SerialName("icon") val icon: String? = null,
    @SerialName("parent_id") val parentId: String? = null,
    @SerialName("permission") val permission: String? = null,
    @SerialName("menu_type") val menuType: MenuType = MenuType.MENU,
    @SerialName("sort_order") val sortOrder: Int = 0,
    @SerialName("is_hidden") val isHidden: Boolean = false,
    @SerialName("is_external") val isExternal: Boolean = false,
    @SerialName("meta") val meta: Map<String, String> = emptyMap(),
    @SerialName("children") val children: List<MenuConfig> = emptyList()
)

/**
 * 菜单树结构
 */
@Serializable
data class MenuTree(
    @SerialName("id") val id: String,
    @SerialName("name") val name: String,
    @SerialName("title") val title: String,
    @SerialName("path") val path: String? = null,
    @SerialName("icon") val icon: String? = null,
    @SerialName("permission") val permission: String? = null,
    @SerialName("menu_type") val menuType: MenuType = MenuType.MENU,
    @SerialName("sort_order") val sortOrder: Int = 0,
    @SerialName("is_hidden") val isHidden: Boolean = false,
    @SerialName("meta") val meta: Map<String, String> = emptyMap(),
    @SerialName("children") val children: List<MenuTree> = emptyList()
)

/**
 * 用户菜单响应模型
 */
@Serializable
data class UserMenuResponse(
    @SerialName("user_id") val userId: String,
    @SerialName("user_type") val userType: String,
    @SerialName("permissions") val permissions: List<String>,
    @SerialName("menus") val menus: List<MenuTree>,
    @SerialName("updated_at") val updatedAt: String
)

/**
 * 菜单权限检查模型
 */
@Serializable
data class MenuPermissionCheck(
    @SerialName("menu_id") val menuId: String,
    @SerialName("permission") val permission: String,
    @SerialName("has_permission") val hasPermission: Boolean
)

/**
 * 菜单统计响应
 */
@Serializable
data class MenuStatsResponse(
    @SerialName("total_menus") val totalMenus: Int,
    @SerialName("accessible_menus") val accessibleMenus: Int,
    @SerialName("permission_coverage") val permissionCoverage: Double,
    @SerialName("menu_usage") val menuUsage: Map<String, Int>
)

/**
 * 仪表盘数据响应
 */
@Serializable
data class DashboardDataResponse(
    @SerialName("user_count") val userCount: Int,
    @SerialName("active_strategies") val activeStrategies: Int,
    @SerialName("risk_alerts") val riskAlerts: Int,
    @SerialName("system_health") val systemHealth: String,
    @SerialName("updated_at") val updatedAt: String
)

/**
 * 系统配置响应
 */
@Serializable
data class SystemConfigResponse(
    @SerialName("app_name") val appName: String,
    @SerialName("version") val version: String,
    @SerialName("features") val features: SystemFeatures,
    @SerialName("limits") val limits: SystemLimits
)

/**
 * 系统功能配置
 */
@Serializable
data class SystemFeatures(
    @SerialName("multi_tenant") val multiTenant: Boolean,
    @SerialName("rbac") val rbac: Boolean,
    @SerialName("audit_log") val auditLog: Boolean
)

/**
 * 系统限制配置
 */
@Serializable
data class SystemLimits(
    @SerialName("max_users") val maxUsers: Int,
    @SerialName("max_strategies") val maxStrategies: Int
)

/**
 * API错误响应
 */
@Serializable
data class ErrorResponse(
    @SerialName("detail") val detail: String
)

/**
 * 验证错误详情
 */
@Serializable
data class ValidationError(
    @SerialName("type") val type: String,
    @SerialName("loc") val location: List<String>,
    @SerialName("msg") val message: String,
    @SerialName("input") val input: String? = null
)

/**
 * 验证错误响应
 */
@Serializable
data class ValidationErrorResponse(
    @SerialName("detail") val detail: List<ValidationError>
)

/**
 * Auth微服务菜单管理API客户端
 */
class AuthMenuApiClient(private val baseUrl: String = "http://192.168.8.168:8001/api/v1") {

    /**
     * 获取当前用户可访问的菜单
     *
     * GET /auth/user-menus
     * 权限要求: 已认证用户
     */
    suspend fun getUserMenus(token: String): UserMenuResponse {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }

    /**
     * 获取完整菜单树结构
     *
     * GET /menus/tree
     * 权限要求: 管理员用户
     */
    suspend fun getMenuTree(token: String): List<MenuTree> {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }

    /**
     * 检查菜单权限
     *
     * POST /auth/check-menu-permission?menu_id={menuId}
     * 权限要求: 已认证用户
     */
    suspend fun checkMenuPermission(token: String, menuId: String): MenuPermissionCheck {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }

    /**
     * 获取指定用户的可访问菜单
     *
     * GET /users/{userId}/menus
     * 权限要求: 管理员用户或查看自己的菜单
     */
    suspend fun getUserMenusById(token: String, userId: String): UserMenuResponse {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }

    /**
     * 获取菜单统计信息
     *
     * GET /auth/menu-stats
     * 权限要求: 已认证用户
     */
    suspend fun getMenuStats(token: String): MenuStatsResponse {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }

    /**
     * 获取仪表盘数据
     *
     * GET /dashboard/data
     * 权限要求: menu:dashboard
     */
    suspend fun getDashboardData(token: String): DashboardDataResponse {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }

    /**
     * 获取系统配置
     *
     * GET /system/config
     * 权限要求: menu:system
     */
    suspend fun getSystemConfig(token: String): SystemConfigResponse {
        // 实现HTTP请求逻辑
        TODO("实现API调用")
    }
}

/**
 * 菜单管理工具类
 */
object MenuUtils {

    /**
     * 根据权限过滤菜单
     */
    fun filterMenusByPermissions(
        menus: List<MenuTree>,
        userPermissions: Set<String>
    ): List<MenuTree> {
        return menus.mapNotNull { menu ->
            if (menu.permission == null || menu.permission in userPermissions) {
                menu.copy(
                    children = filterMenusByPermissions(menu.children, userPermissions)
                )
            } else {
                null
            }
        }
    }

    /**
     * 扁平化菜单树
     */
    fun flattenMenuTree(menus: List<MenuTree>): List<MenuTree> {
        val result = mutableListOf<MenuTree>()

        fun flatten(menuList: List<MenuTree>) {
            menuList.forEach { menu ->
                result.add(menu)
                if (menu.children.isNotEmpty()) {
                    flatten(menu.children)
                }
            }
        }

        flatten(menus)
        return result
    }

    /**
     * 根据ID查找菜单
     */
    fun findMenuById(menus: List<MenuTree>, menuId: String): MenuTree? {
        menus.forEach { menu ->
            if (menu.id == menuId) {
                return menu
            }
            val found = findMenuById(menu.children, menuId)
            if (found != null) {
                return found
            }
        }
        return null
    }
}

/**
 * 使用示例
 */
object MenuApiUsageExample {

    suspend fun example() {
        val client = AuthMenuApiClient()
        val token = "your-jwt-token-here"

        try {
            // 获取用户菜单
            val userMenus = client.getUserMenus(token)
            println("用户 ${userMenus.userId} 有 ${userMenus.menus.size} 个可访问菜单")

            // 检查特定菜单权限
            val permissionCheck = client.checkMenuPermission(token, "dashboard")
            println("仪表盘访问权限: ${permissionCheck.hasPermission}")

            // 获取菜单统计
            val stats = client.getMenuStats(token)
            println("菜单统计 - 总数: ${stats.totalMenus}, 可访问: ${stats.accessibleMenus}")

            // 过滤菜单
            val userPermissions = setOf("menu:dashboard", "menu:strategy", "strategy:read")
            val filteredMenus = MenuUtils.filterMenusByPermissions(userMenus.menus, userPermissions)
            println("根据权限过滤后菜单数: ${filteredMenus.size}")

        } catch (e: Exception) {
            println("API调用失败: ${e.message}")
        }
    }
}