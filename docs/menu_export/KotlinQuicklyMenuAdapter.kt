/**
 * Saturn MHC Kotlin Quickly 前端菜单适配器
 *
 * 专为 Kotlin Quickly 框架设计的菜单服务端集成方案
 * 支持渐进式迁移和动态菜单管理
 */

import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName
import kotlinx.serialization.json.Json
import kotlinx.coroutines.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import kotlinx.datetime.Instant
import kotlinx.collections.immutable.PersistentList
import kotlinx.collections.immutable.persistentListOf
import kotlinx.collections.immutable.toPersistentList

// 菜单数据模型
@Serializable
data class MenuConfig(
    @SerialName("id") val id: String,
    @SerialName("name") val name: String,
    @SerialName("title") val title: String,
    @SerialName("title_en") val titleEn: String? = null,
    @SerialName("path") val path: String? = null,
    @SerialName("component") val component: String? = null,
    @SerialName("icon") val icon: String? = null,
    @SerialName("emoji") val emoji: String? = null,
    @SerialName("permission") val permission: String? = null,
    @SerialName("sort_order") val sortOrder: Int = 0,
    @SerialName("is_hidden") val isHidden: Boolean = false,
    @SerialName("is_external") val isExternal: Boolean = false,
    @SerialName("status") val status: String = "active",
    @SerialName("meta") val meta: Map<String, String>? = null,
    @SerialName("children") val children: List<MenuConfig>? = null
) {
    // 获取显示标题（支持多语言）
    fun getDisplayTitle(locale: String = "zh"): String {
        return when (locale) {
            "en" -> titleEn ?: title
            else -> title
        }
    }

    // 获取显示图标（优先使用emoji）
    fun getDisplayIcon(): String? = emoji ?: icon

    // 检查是否有子菜单
    fun hasChildren(): Boolean = !children.isNullOrEmpty()

    // 获取菜单深度
    fun getDepth(): Int {
        return if (hasChildren()) {
            1 + (children?.maxOfOrNull { it.getDepth() } ?: 0)
        } else {
            0
        }
    }
}

@Serializable
data class UserMenuResponse(
    @SerialName("user_id") val userId: String,
    @SerialName("user_type") val userType: String,
    @SerialName("permissions") val permissions: List<String>,
    @SerialName("menus") val menus: List<MenuConfig>,
    @SerialName("updated_at") val updatedAt: String
)

@Serializable
data class MenuPermissionCheck(
    @SerialName("menu_id") val menuId: String,
    @SerialName("permission") val permission: String,
    @SerialName("has_permission") val hasPermission: Boolean
)

@Serializable
data class MenuStatsResponse(
    @SerialName("total_menus") val totalMenus: Int,
    @SerialName("accessible_menus") val accessibleMenus: Int,
    @SerialName("permission_coverage") val permissionCoverage: Double,
    @SerialName("menu_usage") val menuUsage: Map<String, Int>
)

// 菜单适配器配置
data class MenuAdapterConfig(
    val apiBaseUrl: String,
    val fallbackToLocal: Boolean = true,
    val cacheTimeoutMs: Long = 5 * 60 * 1000, // 5分钟
    val enablePermissionCheck: Boolean = true,
    val debugMode: Boolean = false,
    val retryAttempts: Int = 3,
    val requestTimeoutMs: Long = 10_000
)

// 缓存项
private data class CacheItem<T>(
    val data: T,
    val timestamp: Long,
    val ttl: Long
) {
    fun isExpired(): Boolean = System.currentTimeMillis() - timestamp > ttl
}

/**
 * Kotlin Quickly 菜单适配器服务
 */
class KotlinQuicklyMenuAdapter(
    private val config: MenuAdapterConfig,
    private val httpClient: HttpClient
) {
    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }

    // 内存缓存
    private val menuCache = mutableMapOf<String, CacheItem<List<MenuConfig>>>()
    private val permissionCache = mutableMapOf<String, CacheItem<Boolean>>()

    // 本地fallback菜单（硬编码备份）
    private val localMenus: List<MenuConfig> = listOf(
        MenuConfig(
            id = "dashboard",
            name = "dashboard",
            title = "总览",
            titleEn = "Dashboard",
            path = "/",
            icon = "dashboard",
            emoji = "🏠",
            permission = "menu:dashboard",
            sortOrder = 1,
            meta = mapOf("title" to "总览", "title_en" to "Dashboard", "keepAlive" to "true")
        ),
        MenuConfig(
            id = "market_config",
            name = "market_config",
            title = "市场配置",
            titleEn = "Market Config",
            path = "/market-config",
            icon = "market",
            emoji = "📊",
            permission = "menu:market_config",
            sortOrder = 2
        ),
        // 更多本地菜单...
    )

    /**
     * 获取用户菜单（主入口）
     */
    suspend fun getUserMenus(token: String? = null): Result<List<MenuConfig>> {
        return try {
            if (config.debugMode) {
                println("🔍 Loading user menus...")
            }

            // 尝试从服务端获取
            val serverMenus = token?.let { fetchServerMenus(it) }

            if (serverMenus?.isSuccess == true) {
                val menus = serverMenus.getOrThrow()
                if (config.debugMode) {
                    println("🌐 Loaded ${menus.size} menus from server")
                }
                Result.success(menus)
            } else {
                // Fallback到本地菜单
                if (config.fallbackToLocal) {
                    if (config.debugMode) {
                        println("📱 Using local fallback menus: ${localMenus.size}")
                    }
                    Result.success(localMenus)
                } else {
                    Result.failure(Exception("No menus available"))
                }
            }
        } catch (e: Exception) {
            if (config.debugMode) {
                println("❌ Failed to load menus: ${e.message}")
            }

            if (config.fallbackToLocal) {
                Result.success(localMenus)
            } else {
                Result.failure(e)
            }
        }
    }

    /**
     * 从服务端获取菜单
     */
    private suspend fun fetchServerMenus(token: String): Result<List<MenuConfig>>? {
        val cacheKey = "menus_$token"

        // 检查缓存
        menuCache[cacheKey]?.let { cached ->
            if (!cached.isExpired()) {
                if (config.debugMode) {
                    println("💾 Using cached menus")
                }
                return Result.success(cached.data)
            }
        }

        return try {
            val response = httpClient.get("${config.apiBaseUrl}/api/v1/auth/user-menus") {
                header("Authorization", "Bearer $token")
                header("Content-Type", "application/json")
                timeout {
                    requestTimeoutMillis = config.requestTimeoutMs
                }
            }

            if (response.status.isSuccess()) {
                val userMenuResponse: UserMenuResponse = response.body()
                val menus = transformServerMenus(userMenuResponse.menus)

                // 缓存结果
                menuCache[cacheKey] = CacheItem(
                    data = menus,
                    timestamp = System.currentTimeMillis(),
                    ttl = config.cacheTimeoutMs
                )

                Result.success(menus)
            } else {
                Result.failure(Exception("HTTP ${response.status.value}: ${response.status.description}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 转换服务端菜单格式
     */
    private fun transformServerMenus(serverMenus: List<MenuConfig>): List<MenuConfig> {
        return serverMenus.map { menu ->
            menu.copy(
                // 处理图标优先级：emoji > icon
                icon = menu.emoji ?: menu.icon,
                // 处理子菜单
                children = menu.children?.let { transformServerMenus(it) }
            )
        }.sortedBy { it.sortOrder }
    }

    /**
     * 检查菜单权限
     */
    suspend fun checkMenuPermission(menuId: String, token: String? = null): Result<Boolean> {
        if (!config.enablePermissionCheck || token == null) {
            return Result.success(true)
        }

        val cacheKey = "${menuId}_$token"

        // 检查缓存
        permissionCache[cacheKey]?.let { cached ->
            if (!cached.isExpired()) {
                return Result.success(cached.data)
            }
        }

        return try {
            val response = httpClient.get("${config.apiBaseUrl}/api/v1/auth/check-menu-permission") {
                parameter("menu_id", menuId)
                header("Authorization", "Bearer $token")
                header("Content-Type", "application/json")
            }

            if (response.status.isSuccess()) {
                val result: MenuPermissionCheck = response.body()

                // 缓存结果
                permissionCache[cacheKey] = CacheItem(
                    data = result.hasPermission,
                    timestamp = System.currentTimeMillis(),
                    ttl = config.cacheTimeoutMs
                )

                Result.success(result.hasPermission)
            } else {
                Result.success(false)
            }
        } catch (e: Exception) {
            if (config.debugMode) {
                println("❌ Permission check failed: ${e.message}")
            }
            Result.success(false)
        }
    }

    /**
     * 过滤可见菜单
     */
    fun filterVisibleMenus(menus: List<MenuConfig>): List<MenuConfig> {
        return menus
            .filter { !it.isHidden }
            .map { menu ->
                menu.copy(
                    children = menu.children?.let { filterVisibleMenus(it) }
                )
            }
            .sortedBy { it.sortOrder }
    }

    /**
     * 根据权限过滤菜单
     */
    suspend fun filterMenusByPermissions(
        menus: List<MenuConfig>,
        userPermissions: Set<String>
    ): List<MenuConfig> {
        val filtered = mutableListOf<MenuConfig>()

        for (menu in menus) {
            val hasPermission = menu.permission == null || userPermissions.contains(menu.permission)

            if (hasPermission) {
                val filteredChildren = menu.children?.let {
                    filterMenusByPermissions(it, userPermissions)
                } ?: emptyList()

                filtered.add(menu.copy(children = filteredChildren.ifEmpty { null }))
            }
        }

        return filtered.sortedBy { it.sortOrder }
    }

    /**
     * 查找菜单项
     */
    fun findMenuItem(menus: List<MenuConfig>, predicate: (MenuConfig) -> Boolean): MenuConfig? {
        for (menu in menus) {
            if (predicate(menu)) {
                return menu
            }
            menu.children?.let { children ->
                findMenuItem(children, predicate)?.let { return it }
            }
        }
        return null
    }

    /**
     * 构建面包屑导航
     */
    fun buildBreadcrumb(menus: List<MenuConfig>, targetPath: String): List<MenuConfig> {
        val breadcrumb = mutableListOf<MenuConfig>()

        fun findPath(menuList: List<MenuConfig>): Boolean {
            for (menu in menuList) {
                breadcrumb.add(menu)

                if (menu.path == targetPath) {
                    return true
                }

                if (menu.children != null && findPath(menu.children)) {
                    return true
                }

                breadcrumb.removeLastOrNull()
            }
            return false
        }

        findPath(menus)
        return breadcrumb
    }

    /**
     * 获取菜单统计信息
     */
    fun getMenuStats(menus: List<MenuConfig>): MenuStats {
        val flatMenus = flattenMenus(menus)
        return MenuStats(
            totalMenus = flatMenus.size,
            rootMenus = menus.size,
            childMenus = flatMenus.size - menus.size,
            withPermissions = flatMenus.count { it.permission != null },
            maxDepth = menus.maxOfOrNull { it.getDepth() } ?: 0
        )
    }

    /**
     * 展平菜单列表
     */
    private fun flattenMenus(menus: List<MenuConfig>): List<MenuConfig> {
        val flattened = mutableListOf<MenuConfig>()
        for (menu in menus) {
            flattened.add(menu)
            menu.children?.let { flattened.addAll(flattenMenus(it)) }
        }
        return flattened
    }

    /**
     * 清除缓存
     */
    fun clearCache() {
        menuCache.clear()
        permissionCache.clear()
        if (config.debugMode) {
            println("🗑️ Cache cleared")
        }
    }

    /**
     * 获取缓存统计
     */
    fun getCacheStats(): CacheStats {
        return CacheStats(
            menuCacheSize = menuCache.size,
            permissionCacheSize = permissionCache.size,
            menuCacheHits = menuCache.values.count { !it.isExpired() },
            permissionCacheHits = permissionCache.values.count { !it.isExpired() }
        )
    }
}

// 数据类
data class MenuStats(
    val totalMenus: Int,
    val rootMenus: Int,
    val childMenus: Int,
    val withPermissions: Int,
    val maxDepth: Int
)

data class CacheStats(
    val menuCacheSize: Int,
    val permissionCacheSize: Int,
    val menuCacheHits: Int,
    val permissionCacheHits: Int
)

/**
 * 菜单工具类
 */
object MenuUtils {
    /**
     * 菜单列表转换为树形结构（如果需要）
     */
    fun buildMenuTree(flatMenus: List<MenuConfig>): List<MenuConfig> {
        val menuMap = flatMenus.associateBy { it.id }
        val rootMenus = mutableListOf<MenuConfig>()

        for (menu in flatMenus) {
            val parentId = menu.meta?.get("parent_id")
            if (parentId == null) {
                rootMenus.add(menu)
            } else {
                // 此处可以处理父子关系，但当前设计中children已经包含
            }
        }

        return rootMenus.sortedBy { it.sortOrder }
    }

    /**
     * 生成菜单ID路径
     */
    fun generateMenuPath(menus: List<MenuConfig>, targetId: String): List<String> {
        val path = mutableListOf<String>()

        fun findPath(menuList: List<MenuConfig>): Boolean {
            for (menu in menuList) {
                path.add(menu.id)

                if (menu.id == targetId) {
                    return true
                }

                if (menu.children != null && findPath(menu.children)) {
                    return true
                }

                path.removeLastOrNull()
            }
            return false
        }

        findPath(menus)
        return path
    }

    /**
     * 验证菜单配置
     */
    fun validateMenuConfig(menus: List<MenuConfig>): ValidationResult {
        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()
        val allMenus = flattenMenus(menus)

        // 检查ID唯一性
        val ids = allMenus.map { it.id }
        val duplicateIds = ids.groupBy { it }.filter { it.value.size > 1 }.keys
        if (duplicateIds.isNotEmpty()) {
            errors.add("Duplicate menu IDs: $duplicateIds")
        }

        // 检查路径唯一性
        val paths = allMenus.mapNotNull { it.path }
        val duplicatePaths = paths.groupBy { it }.filter { it.value.size > 1 }.keys
        if (duplicatePaths.isNotEmpty()) {
            errors.add("Duplicate menu paths: $duplicatePaths")
        }

        // 检查权限格式
        val invalidPermissions = allMenus
            .mapNotNull { it.permission }
            .filter { !it.matches(Regex("^[a-z_]+:[a-z_]+$")) }
        if (invalidPermissions.isNotEmpty()) {
            warnings.add("Invalid permission format: $invalidPermissions")
        }

        return ValidationResult(
            isValid = errors.isEmpty(),
            errors = errors,
            warnings = warnings,
            totalMenus = allMenus.size
        )
    }

    private fun flattenMenus(menus: List<MenuConfig>): List<MenuConfig> {
        val flattened = mutableListOf<MenuConfig>()
        for (menu in menus) {
            flattened.add(menu)
            menu.children?.let { flattened.addAll(flattenMenus(it)) }
        }
        return flattened
    }
}

data class ValidationResult(
    val isValid: Boolean,
    val errors: List<String>,
    val warnings: List<String>,
    val totalMenus: Int
)

/**
 * Kotlin Quickly 菜单组件基类
 */
abstract class BaseMenuComponent {
    protected var menuAdapter: KotlinQuicklyMenuAdapter? = null
    protected var menus: List<MenuConfig> = emptyList()
    protected var loading: Boolean = false
    protected var error: String? = null

    /**
     * 初始化菜单适配器
     */
    fun initializeMenuAdapter(adapter: KotlinQuicklyMenuAdapter) {
        this.menuAdapter = adapter
    }

    /**
     * 加载菜单
     */
    suspend fun loadMenus(token: String?) {
        loading = true
        error = null

        try {
            val result = menuAdapter?.getUserMenus(token)
            if (result?.isSuccess == true) {
                menus = menuAdapter?.filterVisibleMenus(result.getOrThrow()) ?: emptyList()
            } else {
                error = result?.exceptionOrNull()?.message ?: "Failed to load menus"
            }
        } catch (e: Exception) {
            error = e.message
        } finally {
            loading = false
        }
    }

    /**
     * 检查菜单权限
     */
    suspend fun hasMenuPermission(menuId: String, token: String?): Boolean {
        return menuAdapter?.checkMenuPermission(menuId, token)?.getOrDefault(false) ?: false
    }

    /**
     * 处理菜单点击
     */
    abstract fun onMenuClick(menu: MenuConfig)

    /**
     * 渲染菜单项
     */
    abstract fun renderMenuItem(menu: MenuConfig, level: Int = 0): String

    /**
     * 获取菜单显示标题
     */
    protected fun getMenuTitle(menu: MenuConfig, locale: String = "zh"): String {
        return menu.getDisplayTitle(locale)
    }

    /**
     * 获取菜单显示图标
     */
    protected fun getMenuIcon(menu: MenuConfig): String {
        return menu.getDisplayIcon() ?: "📄"
    }
}

/**
 * 使用示例
 */
class SaturnMHCMenuExample : BaseMenuComponent() {

    override fun onMenuClick(menu: MenuConfig) {
        println("Menu clicked: ${menu.title} (${menu.path})")
        // 处理导航逻辑
        menu.path?.let {
            // 导航到对应页面
            navigateToPage(it)
        }
    }

    override fun renderMenuItem(menu: MenuConfig, level: Int): String {
        val indent = "  ".repeat(level)
        val icon = getMenuIcon(menu)
        val title = getMenuTitle(menu)

        val childrenHtml = menu.children?.joinToString("\n") {
            renderMenuItem(it, level + 1)
        } ?: ""

        return """
            $indent<div class="menu-item level-$level">
            $indent  <span class="menu-icon">$icon</span>
            $indent  <span class="menu-title">$title</span>
            $indent  ${if (menu.hasChildren()) "<div class=\"menu-children\">\n$childrenHtml\n$indent  </div>" else ""}
            $indent</div>
        """.trimIndent()
    }

    private fun navigateToPage(path: String) {
        // Kotlin Quickly 导航逻辑
        println("Navigating to: $path")
    }
}

/**
 * 初始化代码示例
 */
suspend fun initializeSaturnMHCMenuSystem() {
    // 1. 创建HTTP客户端
    val httpClient = HttpClient()

    // 2. 配置菜单适配器
    val config = MenuAdapterConfig(
        apiBaseUrl = "http://192.168.8.168:8001",
        fallbackToLocal = true,
        cacheTimeoutMs = 5 * 60 * 1000, // 5分钟
        enablePermissionCheck = true,
        debugMode = true
    )

    // 3. 创建菜单适配器
    val menuAdapter = KotlinQuicklyMenuAdapter(config, httpClient)

    // 4. 创建菜单组件
    val menuComponent = SaturnMHCMenuExample()
    menuComponent.initializeMenuAdapter(menuAdapter)

    // 5. 加载菜单
    val token = "your_auth_token_here"
    menuComponent.loadMenus(token)

    // 6. 使用菜单
    println("Menu system initialized successfully!")
}