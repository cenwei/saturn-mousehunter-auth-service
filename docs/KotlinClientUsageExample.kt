/**
 * Saturn MouseHunter 菜单API - Kotlin Quickly 客户端使用示例
 *
 * 这个文件展示如何在Kotlin Quickly框架中使用菜单API进行UI集成
 */

import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.defaultRequest
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*

// ============================================================================
// 菜单API客户端服务类
// ============================================================================

/**
 * 菜单API客户端服务
 * 使用Kotlin Quickly框架进行HTTP请求和JSON序列化
 */
class MenuApiService {
    private val baseUrl = ApiEndpoints.BASE_URL
    private var authToken: String = ""

    // 配置HTTP客户端
    private val httpClient = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                coerceInputValues = true
                encodeDefaults = true
            })
        }

        defaultRequest {
            url(baseUrl)
            header(HttpHeaders.ContentType, ContentType.Application.Json)
        }
    }

    /**
     * 设置认证令牌
     */
    fun setAuthToken(token: String) {
        authToken = token
    }

    /**
     * 获取当前用户可访问的菜单
     */
    suspend fun getUserMenus(): Result<UserMenuResponseDTO> {
        return try {
            val response: HttpResponse = httpClient.get(ApiEndpoints.USER_MENUS) {
                header(HttpHeaders.Authorization, "Bearer $authToken")
            }

            if (response.status.isSuccess()) {
                val menuResponse = response.body<UserMenuResponseDTO>()
                Result.success(menuResponse)
            } else {
                val error = response.body<APIErrorDTO>()
                Result.failure(Exception("HTTP ${response.status.value}: ${error.detail}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 检查用户是否有指定菜单的访问权限
     */
    suspend fun checkMenuPermission(menuId: String): Result<MenuPermissionCheckDTO> {
        return try {
            val response: HttpResponse = httpClient.post(ApiEndpoints.CHECK_MENU_PERMISSION) {
                header(HttpHeaders.Authorization, "Bearer $authToken")
                parameter("menu_id", menuId)
            }

            if (response.status.isSuccess()) {
                val permissionCheck = response.body<MenuPermissionCheckDTO>()
                Result.success(permissionCheck)
            } else {
                val error = response.body<APIErrorDTO>()
                Result.failure(Exception("HTTP ${response.status.value}: ${error.detail}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 获取当前用户的菜单统计信息
     */
    suspend fun getMenuStats(): Result<MenuStatsDTO> {
        return try {
            val response: HttpResponse = httpClient.get(ApiEndpoints.MENU_STATS) {
                header(HttpHeaders.Authorization, "Bearer $authToken")
            }

            if (response.status.isSuccess()) {
                val menuStats = response.body<MenuStatsDTO>()
                Result.success(menuStats)
            } else {
                val error = response.body<APIErrorDTO>()
                Result.failure(Exception("HTTP ${response.status.value}: ${error.detail}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 获取完整菜单树结构 (仅管理员)
     */
    suspend fun getMenuTree(): Result<List<MenuItemDTO>> {
        return try {
            val response: HttpResponse = httpClient.get(ApiEndpoints.MENU_TREE) {
                header(HttpHeaders.Authorization, "Bearer $authToken")
            }

            if (response.status.isSuccess()) {
                val menuTree = response.body<List<MenuItemDTO>>()
                Result.success(menuTree)
            } else {
                val error = response.body<APIErrorDTO>()
                Result.failure(Exception("HTTP ${response.status.value}: ${error.detail}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 获取指定用户的可访问菜单 (仅管理员)
     */
    suspend fun getUserMenusById(userId: String): Result<UserMenuResponseDTO> {
        return try {
            val endpoint = ApiEndpoints.USER_MENUS_BY_ID.replace("{user_id}", userId)
            val response: HttpResponse = httpClient.get(endpoint) {
                header(HttpHeaders.Authorization, "Bearer $authToken")
            }

            if (response.status.isSuccess()) {
                val menuResponse = response.body<UserMenuResponseDTO>()
                Result.success(menuResponse)
            } else {
                val error = response.body<APIErrorDTO>()
                Result.failure(Exception("HTTP ${response.status.value}: ${error.detail}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 关闭HTTP客户端
     */
    fun close() {
        httpClient.close()
    }
}

// ============================================================================
// 菜单管理器类
// ============================================================================

/**
 * 菜单管理器 - 缓存菜单数据并提供便捷方法
 */
class MenuManager {
    private val apiService = MenuApiService()
    private var cachedMenus: List<MenuItemDTO> = emptyList()
    private var cachedUserResponse: UserMenuResponseDTO? = null
    private var lastUpdateTime: Long = 0
    private val cacheTimeout = 5 * 60 * 1000 // 5分钟缓存

    /**
     * 设置认证令牌
     */
    fun setAuthToken(token: String) {
        apiService.setAuthToken(token)
    }

    /**
     * 初始化菜单数据 (带缓存)
     */
    suspend fun initializeMenus(): Result<UserMenuResponseDTO> {
        val currentTime = System.currentTimeMillis()

        // 检查缓存是否有效
        if (cachedUserResponse != null && (currentTime - lastUpdateTime) < cacheTimeout) {
            return Result.success(cachedUserResponse!!)
        }

        return apiService.getUserMenus().also { result ->
            if (result.isSuccess) {
                cachedUserResponse = result.getOrNull()
                cachedMenus = cachedUserResponse?.menus ?: emptyList()
                lastUpdateTime = currentTime
            }
        }
    }

    /**
     * 获取扁平化的菜单映射 (便于快速查找)
     */
    fun getFlatMenuMap(): Map<String, MenuItemDTO> {
        val menuMap = mutableMapOf<String, MenuItemDTO>()

        fun flattenMenus(menus: List<MenuItemDTO>) {
            menus.forEach { menu ->
                menuMap[menu.id] = menu
                flattenMenus(menu.children)
            }
        }

        flattenMenus(cachedMenus)
        return menuMap
    }

    /**
     * 根据菜单ID查找菜单项
     */
    fun findMenuById(menuId: String): MenuItemDTO? {
        return getFlatMenuMap()[menuId]
    }

    /**
     * 获取根级菜单 (无父菜单)
     */
    fun getRootMenus(): List<MenuItemDTO> {
        return cachedMenus.filter { it.parentId == null }
    }

    /**
     * 根据权限过滤菜单
     */
    fun getMenusByPermission(permission: String): List<MenuItemDTO> {
        return getFlatMenuMap().values.filter { it.permission == permission }
    }

    /**
     * 检查菜单权限
     */
    suspend fun hasMenuPermission(menuId: String): Boolean {
        return apiService.checkMenuPermission(menuId)
            .getOrNull()?.hasPermission ?: false
    }

    /**
     * 获取菜单统计
     */
    suspend fun getStatistics(): Result<MenuStatsDTO> {
        return apiService.getMenuStats()
    }

    /**
     * 清理资源
     */
    fun cleanup() {
        apiService.close()
    }
}

// ============================================================================
// UI适配器类
// ============================================================================

/**
 * 菜单UI适配器 - 为UI框架提供便捷的数据转换
 */
class MenuUIAdapter(private val menuManager: MenuManager) {

    /**
     * 转换为导航菜单项
     */
    data class NavigationItem(
        val id: String,
        val title: String,
        val icon: String?,
        val path: String?,
        val children: List<NavigationItem> = emptyList(),
        val isActive: Boolean = false
    )

    /**
     * 将菜单DTO转换为导航项
     */
    fun convertToNavigationItems(menus: List<MenuItemDTO>): List<NavigationItem> {
        return menus.filter { !it.isHidden && it.status == "active" }
            .sortedBy { it.sortOrder }
            .map { menu ->
                NavigationItem(
                    id = menu.id,
                    title = menu.title,
                    icon = menu.icon ?: menu.emoji,
                    path = menu.path,
                    children = convertToNavigationItems(menu.children)
                )
            }
    }

    /**
     * 生成面包屑导航
     */
    fun generateBreadcrumbs(currentMenuId: String): List<NavigationItem> {
        val menuMap = menuManager.getFlatMenuMap()
        val breadcrumbs = mutableListOf<NavigationItem>()
        var currentMenu = menuMap[currentMenuId]

        while (currentMenu != null) {
            breadcrumbs.add(0, NavigationItem(
                id = currentMenu.id,
                title = currentMenu.title,
                icon = currentMenu.icon ?: currentMenu.emoji,
                path = currentMenu.path
            ))
            currentMenu = currentMenu.parentId?.let { menuMap[it] }
        }

        return breadcrumbs
    }

    /**
     * 获取用户权限摘要
     */
    fun getUserPermissionSummary(): Map<String, Any> {
        val userResponse = menuManager.cachedUserResponse ?: return emptyMap()
        return mapOf(
            "userId" to userResponse.userId,
            "userType" to userResponse.userType.name,
            "totalPermissions" to userResponse.permissions.size,
            "accessibleMenus" to userResponse.menus.size,
            "lastUpdated" to userResponse.updatedAt
        )
    }
}

// ============================================================================
// 使用示例
// ============================================================================

/**
 * 完整使用示例
 */
class MenuIntegrationExample {

    suspend fun demonstrateMenuUsage() {
        val menuManager = MenuManager()

        try {
            // 1. 设置认证令牌
            menuManager.setAuthToken("your_jwt_token_here")

            // 2. 初始化菜单数据
            val userMenusResult = menuManager.initializeMenus()

            if (userMenusResult.isSuccess) {
                val userResponse = userMenusResult.getOrThrow()
                println("用户 ${userResponse.userId} (${userResponse.userType}) 的菜单加载成功")
                println("可访问菜单数量: ${userResponse.menus.size}")
                println("用户权限: ${userResponse.permissions.joinToString()}")

                // 3. 创建UI适配器
                val uiAdapter = MenuUIAdapter(menuManager)

                // 4. 转换为导航项
                val navigationItems = uiAdapter.convertToNavigationItems(userResponse.menus)
                println("导航菜单项数量: ${navigationItems.size}")

                // 5. 检查特定菜单权限
                val hasTradeCalendarPermission = menuManager.hasMenuPermission(MenuIds.TRADING_CALENDAR)
                println("交易日历权限: $hasTradeCalendarPermission")

                // 6. 生成面包屑
                val breadcrumbs = uiAdapter.generateBreadcrumbs(MenuIds.DASHBOARD)
                println("面包屑导航: ${breadcrumbs.map { it.title }.joinToString(" > ")}")

                // 7. 获取统计信息
                val statsResult = menuManager.getStatistics()
                if (statsResult.isSuccess) {
                    val stats = statsResult.getOrThrow()
                    println("菜单统计 - 总数:${stats.totalMenus}, 可访问:${stats.accessibleMenus}, 覆盖率:${stats.permissionCoverage}%")
                }

                // 8. 查找特定菜单
                val dashboardMenu = menuManager.findMenuById(MenuIds.DASHBOARD)
                println("仪表板菜单: ${dashboardMenu?.title ?: "未找到"}")

            } else {
                println("菜单加载失败: ${userMenusResult.exceptionOrNull()?.message}")
            }

        } catch (e: Exception) {
            println("菜单集成示例执行失败: ${e.message}")
        } finally {
            // 9. 清理资源
            menuManager.cleanup()
        }
    }
}

// ============================================================================
// 错误处理工具
// ============================================================================

/**
 * 菜单API错误处理工具
 */
object MenuErrorHandler {

    /**
     * 处理API结果并提供用户友好的错误信息
     */
    fun <T> handleApiResult(
        result: Result<T>,
        onSuccess: (T) -> Unit,
        onError: ((String) -> Unit)? = null
    ) {
        result.fold(
            onSuccess = onSuccess,
            onFailure = { exception ->
                val errorMessage = when {
                    exception.message?.contains("401") == true -> "认证失败，请重新登录"
                    exception.message?.contains("403") == true -> "权限不足，无法访问该功能"
                    exception.message?.contains("404") == true -> "请求的菜单不存在"
                    exception.message?.contains("500") == true -> "服务器内部错误，请稍后重试"
                    else -> "网络错误: ${exception.message}"
                }
                onError?.invoke(errorMessage) ?: println("错误: $errorMessage")
            }
        )
    }

    /**
     * 检查网络连接并重试API调用
     */
    suspend fun <T> retryWithBackoff(
        maxRetries: Int = 3,
        baseDelay: Long = 1000,
        apiCall: suspend () -> Result<T>
    ): Result<T> {
        repeat(maxRetries) { attempt ->
            val result = apiCall()
            if (result.isSuccess) return result

            if (attempt < maxRetries - 1) {
                delay(baseDelay * (attempt + 1))
            }
        }
        return apiCall() // 最后一次尝试
    }
}