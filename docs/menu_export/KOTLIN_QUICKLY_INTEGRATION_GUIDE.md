# Kotlin Quickly 前端菜单服务端集成指南

专为 **Kotlin Quickly** 框架设计的菜单服务端集成方案，将硬编码菜单迁移到动态服务端配置。

## 📋 概述

### 🎯 适用场景
- **Kotlin Quickly** 前端框架
- **Saturn MHC** 项目菜单系统
- **服务端驱动** 的菜单配置
- **RBAC权限** 集成

### 🏗️ 架构设计

```
Kotlin Quickly 应用
       │
   ┌───▼────────────────────────────┐
   │  KotlinQuicklyMenuAdapter      │  ← 菜单适配器
   │  ├─ 缓存管理                    │
   │  ├─ 权限检查                    │
   │  ├─ 错误处理                    │
   │  └─ 数据转换                    │
   └───┬────────────────────────────┘
       │
   ┌───▼────────────────────────────┐
   │  认证服务 API                   │  ← 服务端
   │  ├─ /api/v1/auth/user-menus   │
   │  ├─ /api/v1/auth/check-permission │
   │  └─ /api/v1/menus/*           │
   └───┬────────────────────────────┘
       │
   ┌───▼────────────────────────────┐
   │  菜单配置数据库                  │  ← 数据存储
   │  ├─ 19个根菜单                 │
   │  ├─ 23个权限映射               │
   │  └─ 多语言支持                  │
   └────────────────────────────────┘
```

## 🚀 快速开始

### 1. 依赖配置

在你的 `build.gradle.kts` 中添加必要依赖：

```kotlin
dependencies {
    // Kotlin Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")

    // Ktor Client (HTTP客户端)
    implementation("io.ktor:ktor-client-core:2.3.5")
    implementation("io.ktor:ktor-client-cio:2.3.5")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.5")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")

    // DateTime
    implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.4.1")
}
```

### 2. 复制适配器文件

```bash
# 将菜单适配器复制到你的项目中
cp KotlinQuicklyMenuAdapter.kt src/main/kotlin/menu/
cp MenuApiModels.kt src/main/kotlin/menu/models/
```

### 3. 初始化菜单系统

```kotlin
// MenuManager.kt
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*

class MenuManager {
    private val httpClient = HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }
    }

    private val menuAdapter = KotlinQuicklyMenuAdapter(
        config = MenuAdapterConfig(
            apiBaseUrl = "http://192.168.8.168:8001",
            fallbackToLocal = true,
            cacheTimeoutMs = 5 * 60 * 1000, // 5分钟缓存
            enablePermissionCheck = true,
            debugMode = BuildConfig.DEBUG
        ),
        httpClient = httpClient
    )

    suspend fun initialize(authToken: String?): Result<List<MenuConfig>> {
        return menuAdapter.getUserMenus(authToken)
    }

    suspend fun checkPermission(menuId: String, token: String?): Boolean {
        return menuAdapter.checkMenuPermission(menuId, token)
            .getOrDefault(false)
    }

    fun getVisibleMenus(menus: List<MenuConfig>): List<MenuConfig> {
        return menuAdapter.filterVisibleMenus(menus)
    }

    fun clearCache() {
        menuAdapter.clearCache()
    }
}
```

## 📱 Kotlin Quickly 具体实现

### 1. 主应用初始化

```kotlin
// App.kt
class SaturnMHCApp : Application() {
    private lateinit var menuManager: MenuManager
    private var appMenus: List<MenuConfig> = emptyList()

    override fun onCreate() {
        super.onCreate()

        // 初始化菜单管理器
        menuManager = MenuManager()

        // 异步加载菜单
        lifecycleScope.launch {
            initializeMenuSystem()
        }
    }

    private suspend fun initializeMenuSystem() {
        try {
            // 获取认证token
            val authToken = SharedPreferences.getString("auth_token", null)

            // 加载菜单
            val result = menuManager.initialize(authToken)

            if (result.isSuccess) {
                appMenus = menuManager.getVisibleMenus(result.getOrThrow())

                // 通知UI更新
                notifyMenusLoaded(appMenus)

                Log.i("MenuSystem", "✅ Loaded ${appMenus.size} menus successfully")
            } else {
                Log.e("MenuSystem", "❌ Failed to load menus: ${result.exceptionOrNull()?.message}")
            }

        } catch (e: Exception) {
            Log.e("MenuSystem", "❌ Menu initialization error", e)
        }
    }

    private fun notifyMenusLoaded(menus: List<MenuConfig>) {
        // 使用 EventBus 或其他方式通知UI组件
        EventBus.getDefault().post(MenusLoadedEvent(menus))
    }
}
```

### 2. 主菜单组件

```kotlin
// MainMenuComponent.kt
class MainMenuComponent : BaseMenuComponent() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var menuAdapter: MenuRecyclerAdapter
    private var currentLocale: String = "zh"

    fun initialize(recyclerView: RecyclerView) {
        this.recyclerView = recyclerView
        setupRecyclerView()

        // 监听菜单加载事件
        EventBus.getDefault().register(this)
    }

    private fun setupRecyclerView() {
        menuAdapter = MenuRecyclerAdapter(
            menus = emptyList(),
            onMenuClick = { menu -> onMenuClick(menu) },
            onPermissionCheck = { menuId -> checkPermissionAsync(menuId) }
        )

        recyclerView.adapter = menuAdapter
        recyclerView.layoutManager = LinearLayoutManager(context)
    }

    @Subscribe(threadMode = ThreadMode.MAIN)
    fun onMenusLoaded(event: MenusLoadedEvent) {
        // 更新菜单列表
        menuAdapter.updateMenus(event.menus)

        // 隐藏loading状态
        hideLoading()
    }

    override fun onMenuClick(menu: MenuConfig) {
        lifecycleScope.launch {
            // 检查权限
            if (menu.permission != null) {
                val hasPermission = hasMenuPermission(menu.id, getAuthToken())
                if (!hasPermission) {
                    showPermissionDeniedDialog(menu.title)
                    return@launch
                }
            }

            // 导航到目标页面
            navigateToMenu(menu)
        }
    }

    private fun navigateToMenu(menu: MenuConfig) {
        menu.path?.let { path ->
            when (path) {
                "/" -> navigateToActivity(DashboardActivity::class.java)
                "/market-config" -> navigateToActivity(MarketConfigActivity::class.java)
                "/trading-calendar" -> navigateToActivity(TradingCalendarActivity::class.java)
                "/proxy-pool" -> navigateToActivity(ProxyPoolActivity::class.java)
                // 更多路由映射...
                else -> {
                    // 动态路由处理
                    navigateToWebView(path)
                }
            }
        }
    }

    private fun navigateToActivity(activityClass: Class<*>) {
        val intent = Intent(context, activityClass)
        context.startActivity(intent)
    }

    private fun navigateToWebView(path: String) {
        val intent = Intent(context, WebViewActivity::class.java).apply {
            putExtra("url", "http://localhost:8080$path")
        }
        context.startActivity(intent)
    }

    override fun renderMenuItem(menu: MenuConfig, level: Int): String {
        // Kotlin Quickly 中通常不需要手动渲染HTML
        // 这里返回调试信息
        val indent = "  ".repeat(level)
        return "$indent${getMenuIcon(menu)} ${getMenuTitle(menu, currentLocale)}"
    }

    fun switchLanguage(locale: String) {
        currentLocale = locale
        menuAdapter.setLocale(locale)
        menuAdapter.notifyDataSetChanged()
    }

    private fun checkPermissionAsync(menuId: String) {
        lifecycleScope.launch {
            val hasPermission = hasMenuPermission(menuId, getAuthToken())
            // 更新UI权限状态
            updateMenuPermissionState(menuId, hasPermission)
        }
    }

    private fun getAuthToken(): String? {
        return SharedPreferences.getString("auth_token", null)
    }

    override fun onDestroy() {
        super.onDestroy()
        EventBus.getDefault().unregister(this)
    }
}
```

### 3. 菜单RecyclerView适配器

```kotlin
// MenuRecyclerAdapter.kt
class MenuRecyclerAdapter(
    private var menus: List<MenuConfig>,
    private val onMenuClick: (MenuConfig) -> Unit,
    private val onPermissionCheck: (String) -> Unit
) : RecyclerView.Adapter<MenuRecyclerAdapter.MenuViewHolder>() {

    private var locale: String = "zh"
    private val permissionStates = mutableMapOf<String, Boolean>()

    fun updateMenus(newMenus: List<MenuConfig>) {
        this.menus = newMenus
        notifyDataSetChanged()
    }

    fun setLocale(locale: String) {
        this.locale = locale
    }

    fun updatePermissionState(menuId: String, hasPermission: Boolean) {
        permissionStates[menuId] = hasPermission
        // 找到对应item并更新
        val position = findMenuPosition(menuId)
        if (position >= 0) {
            notifyItemChanged(position)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MenuViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_menu, parent, false)
        return MenuViewHolder(view)
    }

    override fun onBindViewHolder(holder: MenuViewHolder, position: Int) {
        val menu = menus[position]
        holder.bind(menu)
    }

    override fun getItemCount(): Int = menus.size

    inner class MenuViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val iconView: TextView = itemView.findViewById(R.id.menu_icon)
        private val titleView: TextView = itemView.findViewById(R.id.menu_title)
        private val subtitleView: TextView = itemView.findViewById(R.id.menu_subtitle)
        private val arrowView: ImageView = itemView.findViewById(R.id.menu_arrow)
        private val permissionIndicator: View = itemView.findViewById(R.id.permission_indicator)

        fun bind(menu: MenuConfig) {
            // 设置图标（优先使用emoji）
            iconView.text = menu.getDisplayIcon() ?: "📄"

            // 设置标题（支持多语言）
            titleView.text = menu.getDisplayTitle(locale)

            // 设置副标题（路径或权限信息）
            subtitleView.text = menu.path ?: menu.permission
            subtitleView.visibility = if (subtitleView.text.isNullOrEmpty())
                View.GONE else View.VISIBLE

            // 设置箭头（如果有子菜单）
            arrowView.visibility = if (menu.hasChildren()) View.VISIBLE else View.GONE

            // 设置权限指示器
            val hasPermission = permissionStates[menu.id]
            when (hasPermission) {
                true -> {
                    permissionIndicator.setBackgroundColor(Color.GREEN)
                    permissionIndicator.visibility = View.VISIBLE
                }
                false -> {
                    permissionIndicator.setBackgroundColor(Color.RED)
                    permissionIndicator.visibility = View.VISIBLE
                }
                null -> {
                    permissionIndicator.visibility = View.GONE
                    // 异步检查权限
                    if (menu.permission != null) {
                        onPermissionCheck(menu.id)
                    }
                }
            }

            // 设置点击事件
            itemView.setOnClickListener {
                onMenuClick(menu)
            }

            // 设置长按事件（显示菜单详情）
            itemView.setOnLongClickListener {
                showMenuDetails(menu)
                true
            }
        }

        private fun showMenuDetails(menu: MenuConfig) {
            val details = """
                菜单ID: ${menu.id}
                标题: ${menu.title}
                路径: ${menu.path ?: "无"}
                权限: ${menu.permission ?: "无"}
                状态: ${menu.status}
                排序: ${menu.sortOrder}
            """.trimIndent()

            AlertDialog.Builder(itemView.context)
                .setTitle("菜单详情")
                .setMessage(details)
                .setPositiveButton("确定", null)
                .show()
        }
    }

    private fun findMenuPosition(menuId: String): Int {
        return menus.indexOfFirst { it.id == menuId }
    }
}
```

### 4. 权限中间件

```kotlin
// PermissionMiddleware.kt
class PermissionMiddleware(
    private val menuManager: MenuManager
) {

    suspend fun checkActivityPermission(
        activityClass: Class<*>,
        token: String?
    ): Boolean {
        // 映射Activity到菜单权限
        val permission = when (activityClass) {
            DashboardActivity::class.java -> "menu:dashboard"
            MarketConfigActivity::class.java -> "menu:market_config"
            TradingCalendarActivity::class.java -> "menu:trading_calendar"
            ProxyPoolActivity::class.java -> "menu:proxy_pool"
            // 更多映射...
            else -> null
        }

        return if (permission != null) {
            menuManager.checkPermission(permission, token)
        } else {
            true // 无权限要求的页面默认允许
        }
    }

    fun createPermissionIntent(
        context: Context,
        targetActivity: Class<*>,
        token: String?
    ): Intent? {
        return lifecycleScope.async {
            val hasPermission = checkActivityPermission(targetActivity, token)

            if (hasPermission) {
                Intent(context, targetActivity)
            } else {
                Intent(context, PermissionDeniedActivity::class.java).apply {
                    putExtra("target_activity", targetActivity.simpleName)
                }
            }
        }.await()
    }
}
```

### 5. 缓存管理

```kotlin
// MenuCacheManager.kt
object MenuCacheManager {
    private const val PREFS_NAME = "menu_cache"
    private const val KEY_CACHED_MENUS = "cached_menus"
    private const val KEY_CACHE_TIMESTAMP = "cache_timestamp"
    private const val CACHE_DURATION = 5 * 60 * 1000L // 5分钟

    fun saveMenusToCache(context: Context, menus: List<MenuConfig>) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val json = Json.encodeToString(menus)

        prefs.edit()
            .putString(KEY_CACHED_MENUS, json)
            .putLong(KEY_CACHE_TIMESTAMP, System.currentTimeMillis())
            .apply()
    }

    fun loadMenusFromCache(context: Context): List<MenuConfig>? {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val timestamp = prefs.getLong(KEY_CACHE_TIMESTAMP, 0)

        // 检查缓存是否过期
        if (System.currentTimeMillis() - timestamp > CACHE_DURATION) {
            return null
        }

        val json = prefs.getString(KEY_CACHED_MENUS, null) ?: return null

        return try {
            Json.decodeFromString<List<MenuConfig>>(json)
        } catch (e: Exception) {
            null
        }
    }

    fun clearCache(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().clear().apply()
    }

    fun isCacheValid(context: Context): Boolean {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val timestamp = prefs.getLong(KEY_CACHE_TIMESTAMP, 0)
        return System.currentTimeMillis() - timestamp <= CACHE_DURATION
    }
}
```

## 🔧 配置和定制

### 1. 环境配置

```kotlin
// Config.kt
object MenuConfig {
    const val API_BASE_URL = when (BuildConfig.BUILD_TYPE) {
        "debug" -> "http://192.168.8.168:8001"
        "staging" -> "https://staging-api.saturn-mhc.com"
        "release" -> "https://api.saturn-mhc.com"
        else -> "http://localhost:8001"
    }

    const val CACHE_TIMEOUT_MS = 5 * 60 * 1000L // 5分钟
    const val REQUEST_TIMEOUT_MS = 10_000L // 10秒
    const val ENABLE_DEBUG_LOGS = BuildConfig.DEBUG
    const val FALLBACK_TO_LOCAL = true
}
```

### 2. 主题和样式

```xml
<!-- res/layout/item_menu.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:padding="16dp"
    android:background="?attr/selectableItemBackground">

    <TextView
        android:id="@+id/menu_icon"
        android:layout_width="32dp"
        android:layout_height="32dp"
        android:layout_marginEnd="16dp"
        android:gravity="center"
        android:textSize="20sp" />

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">

        <TextView
            android:id="@+id/menu_title"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="16sp"
            android:textStyle="bold"
            android:textColor="?attr/colorOnSurface" />

        <TextView
            android:id="@+id/menu_subtitle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="12sp"
            android:textColor="?attr/colorOnSurfaceVariant"
            android:visibility="gone" />

    </LinearLayout>

    <View
        android:id="@+id/permission_indicator"
        android:layout_width="8dp"
        android:layout_height="8dp"
        android:layout_marginEnd="8dp"
        android:layout_gravity="center_vertical"
        android:background="@drawable/circle_indicator"
        android:visibility="gone" />

    <ImageView
        android:id="@+id/menu_arrow"
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:src="@drawable/ic_arrow_right"
        android:visibility="gone" />

</LinearLayout>
```

### 3. 错误处理

```kotlin
// MenuErrorHandler.kt
object MenuErrorHandler {

    fun handleMenuLoadError(context: Context, error: Throwable) {
        when (error) {
            is UnknownHostException -> {
                showError(context, "网络连接失败", "请检查网络连接后重试")
            }
            is SocketTimeoutException -> {
                showError(context, "请求超时", "服务器响应超时，请稍后重试")
            }
            is HttpException -> {
                when (error.code()) {
                    401 -> showError(context, "认证失败", "请重新登录")
                    403 -> showError(context, "权限不足", "您没有访问权限")
                    404 -> showError(context, "服务不存在", "菜单服务暂时不可用")
                    500 -> showError(context, "服务器错误", "服务器内部错误")
                    else -> showError(context, "请求失败", "HTTP ${error.code()}")
                }
            }
            else -> {
                showError(context, "未知错误", error.message ?: "加载菜单时发生错误")
            }
        }
    }

    private fun showError(context: Context, title: String, message: String) {
        AlertDialog.Builder(context)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("确定", null)
            .setNegativeButton("重试") { _, _ ->
                // 重新加载菜单
                EventBus.getDefault().post(RetryLoadMenusEvent())
            }
            .show()
    }
}
```

## 📊 测试和验证

### 1. 单元测试

```kotlin
// MenuAdapterTest.kt
class MenuAdapterTest {

    private lateinit var mockHttpClient: HttpClient
    private lateinit var menuAdapter: KotlinQuicklyMenuAdapter

    @Before
    fun setup() {
        mockHttpClient = MockHttpClient()
        menuAdapter = KotlinQuicklyMenuAdapter(
            config = MenuAdapterConfig(
                apiBaseUrl = "http://test.com",
                fallbackToLocal = true,
                enablePermissionCheck = false,
                debugMode = true
            ),
            httpClient = mockHttpClient
        )
    }

    @Test
    fun `test getUserMenus with valid token returns success`() = runTest {
        // Mock successful response
        mockHttpClient.mockResponse("""
            {
                "user_id": "test_user",
                "user_type": "ADMIN",
                "permissions": ["menu:dashboard"],
                "menus": [
                    {
                        "id": "dashboard",
                        "title": "仪表盘",
                        "path": "/",
                        "emoji": "🏠"
                    }
                ],
                "updated_at": "2025-09-19T15:00:00Z"
            }
        """)

        val result = menuAdapter.getUserMenus("valid_token")

        assertTrue(result.isSuccess)
        val menus = result.getOrThrow()
        assertEquals(1, menus.size)
        assertEquals("dashboard", menus[0].id)
        assertEquals("🏠", menus[0].emoji)
    }

    @Test
    fun `test filterVisibleMenus removes hidden menus`() {
        val menus = listOf(
            MenuConfig(id = "visible", title = "Visible", isHidden = false),
            MenuConfig(id = "hidden", title = "Hidden", isHidden = true)
        )

        val filtered = menuAdapter.filterVisibleMenus(menus)

        assertEquals(1, filtered.size)
        assertEquals("visible", filtered[0].id)
    }
}
```

### 2. 集成测试

```kotlin
// MenuIntegrationTest.kt
@RunWith(AndroidJUnit4::class)
class MenuIntegrationTest {

    @Test
    fun testFullMenuLoadFlow() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)

        scenario.use {
            // 验证菜单加载
            onView(withId(R.id.menu_recycler_view))
                .check(matches(isDisplayed()))

            // 验证至少有一个菜单项
            onView(withId(R.id.menu_recycler_view))
                .check(matches(hasMinimumChildCount(1)))

            // 点击第一个菜单项
            onView(withId(R.id.menu_recycler_view))
                .perform(RecyclerViewActions.actionOnItemAtPosition<MenuViewHolder>(0, click()))
        }
    }
}
```

## 🔧 故障排除

### 常见问题

**Q: 菜单加载失败**
```kotlin
// 检查网络连接和API地址
if (!NetworkUtils.isConnected()) {
    Log.e("Menu", "No network connection")
    return
}

// 检查API响应
try {
    val response = httpClient.get("$apiBaseUrl/health")
    Log.d("Menu", "API Health: ${response.status}")
} catch (e: Exception) {
    Log.e("Menu", "API health check failed", e)
}
```

**Q: 权限检查不准确**
```kotlin
// 清除权限缓存
menuAdapter.clearCache()

// 重新检查权限
val hasPermission = menuAdapter.checkMenuPermission(menuId, token)
    .getOrDefault(false)
```

**Q: 缓存数据过期**
```kotlin
// 检查缓存状态
val isValid = MenuCacheManager.isCacheValid(context)
if (!isValid) {
    MenuCacheManager.clearCache(context)
    // 重新加载菜单
}
```

## 📚 相关资源

- [认证服务API文档](../MENU_MANAGEMENT_API.md)
- [权限系统设计](../PERMISSION_SYSTEM.md)
- [Kotlin Serialization文档](https://kotlinlang.org/docs/serialization.html)
- [Ktor Client文档](https://ktor.io/docs/getting-started-ktor-client.html)

---

通过这个专门为 Kotlin Quickly 设计的方案，你可以：

✅ **无缝迁移**：从硬编码菜单平滑过渡到服务端配置
✅ **权限集成**：完整的RBAC权限控制
✅ **性能优化**：智能缓存和异步加载
✅ **错误恢复**：robust的错误处理和fallback机制
✅ **多语言支持**：中英文菜单标题

现在你可以开始在 Kotlin Quickly 项目中集成这个菜单系统了！