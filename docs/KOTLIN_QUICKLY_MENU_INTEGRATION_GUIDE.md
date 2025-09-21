# Saturn MouseHunter 菜单模块 - Kotlin Quickly UI对接指南

## 📋 概述

本文档为使用 **Kotlin Quickly** 框架的前端提供完整的菜单模块API对接规范，确保接口调用准确无误。

## 🎯 核心DTO定义

### 依赖配置

在你的 `build.gradle.kts` 中添加以下依赖：

```kotlin
dependencies {
    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-cio:2.3.7")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
}
```

### 序列化配置

```kotlin
// 在你的模块中添加
plugins {
    kotlin("plugin.serialization") version "1.9.22"
}
```

## 🔗 API端点规范

### 基础配置

```kotlin
object ApiConfig {
    const val BASE_URL = "http://192.168.8.168:8001/api/v1"
    const val TIMEOUT_MILLIS = 30000L

    // 端点路径
    const val USER_MENUS = "/auth/user-menus"
    const val CHECK_MENU_PERMISSION = "/auth/check-menu-permission"
    const val MENU_STATS = "/auth/menu-stats"
    const val MENU_TREE = "/menus/tree"
    const val USER_MENUS_BY_ID = "/users/{user_id}/menus"
}
```

## 📱 Kotlin Quickly 集成示例

### 1. 基础菜单服务类

```kotlin
class MenuService @Inject constructor() {
    private val apiService = MenuApiService()
    private val _menuState = MutableStateFlow<MenuState>(MenuState.Loading)
    val menuState: StateFlow<MenuState> = _menuState.asStateFlow()

    sealed class MenuState {
        object Loading : MenuState()
        data class Success(val menus: List<MenuItemDTO>) : MenuState()
        data class Error(val message: String) : MenuState()
    }

    suspend fun loadUserMenus(authToken: String) {
        _menuState.value = MenuState.Loading

        apiService.setAuthToken(authToken)
        apiService.getUserMenus().fold(
            onSuccess = { response ->
                _menuState.value = MenuState.Success(response.menus)
            },
            onFailure = { exception ->
                _menuState.value = MenuState.Error(exception.message ?: "未知错误")
            }
        )
    }
}
```

### 2. Composable UI 组件

```kotlin
@Composable
fun MenuNavigationDrawer(
    menuService: MenuService,
    onMenuItemClick: (MenuItemDTO) -> Unit
) {
    val menuState by menuService.menuState.collectAsState()

    when (menuState) {
        is MenuService.MenuState.Loading -> {
            CircularProgressIndicator()
        }
        is MenuService.MenuState.Success -> {
            LazyColumn {
                items(menuState.menus) { menu ->
                    MenuListItem(
                        menu = menu,
                        onClick = { onMenuItemClick(menu) }
                    )
                }
            }
        }
        is MenuService.MenuState.Error -> {
            ErrorMessage(message = menuState.message)
        }
    }
}

@Composable
fun MenuListItem(
    menu: MenuItemDTO,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp)
            .clickable { onClick() }
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 图标
            menu.emoji?.let { emoji ->
                Text(
                    text = emoji,
                    fontSize = 20.sp,
                    modifier = Modifier.padding(end = 12.dp)
                )
            }

            // 标题
            Text(
                text = menu.title,
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.weight(1f)
            )

            // 子菜单指示器
            if (menu.children.isNotEmpty()) {
                Icon(
                    imageVector = Icons.Default.KeyboardArrowRight,
                    contentDescription = "有子菜单"
                )
            }
        }
    }
}
```

### 3. ViewModel 集成

```kotlin
@HiltViewModel
class MainViewModel @Inject constructor(
    private val menuService: MenuService,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _currentMenu = MutableStateFlow<MenuItemDTO?>(null)
    val currentMenu: StateFlow<MenuItemDTO?> = _currentMenu.asStateFlow()

    private val _breadcrumbs = MutableStateFlow<List<MenuItemDTO>>(emptyList())
    val breadcrumbs: StateFlow<List<MenuItemDTO>> = _breadcrumbs.asStateFlow()

    fun initializeMenus() {
        viewModelScope.launch {
            val authToken = authRepository.getAuthToken()
            if (authToken != null) {
                menuService.loadUserMenus(authToken)
            }
        }
    }

    fun navigateToMenu(menu: MenuItemDTO) {
        _currentMenu.value = menu
        updateBreadcrumbs(menu)
    }

    private fun updateBreadcrumbs(menu: MenuItemDTO) {
        // 生成面包屑逻辑
        val breadcrumbList = generateBreadcrumbPath(menu)
        _breadcrumbs.value = breadcrumbList
    }
}
```

### 4. 权限检查集成

```kotlin
@Composable
fun ProtectedMenuContent(
    menuId: String,
    menuService: MenuService,
    content: @Composable () -> Unit
) {
    var hasPermission by remember { mutableStateOf<Boolean?>(null) }

    LaunchedEffect(menuId) {
        val menuManager = MenuManager()
        hasPermission = menuManager.hasMenuPermission(menuId)
        menuManager.cleanup()
    }

    when (hasPermission) {
        null -> CircularProgressIndicator()
        true -> content()
        false -> {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.padding(16.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Lock,
                    contentDescription = "无权限",
                    tint = MaterialTheme.colorScheme.error
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "您没有权限访问此功能",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}
```

## 🚨 错误处理最佳实践

### 1. 统一错误处理

```kotlin
class MenuErrorHandler {
    companion object {
        fun handleMenuError(
            error: Throwable,
            context: Context,
            onRetry: (() -> Unit)? = null
        ) {
            val message = when {
                error.message?.contains("401") == true -> {
                    "登录已过期，请重新登录"
                }
                error.message?.contains("403") == true -> {
                    "权限不足，无法访问"
                }
                error.message?.contains("404") == true -> {
                    "菜单不存在"
                }
                error.message?.contains("500") == true -> {
                    "服务器错误，请稍后重试"
                }
                else -> "网络连接异常: ${error.message}"
            }

            // 显示错误提示
            showErrorSnackbar(context, message, onRetry)
        }

        private fun showErrorSnackbar(
            context: Context,
            message: String,
            onRetry: (() -> Unit)?
        ) {
            // 实现错误提示逻辑
        }
    }
}
```

### 2. 网络重试机制

```kotlin
suspend fun <T> retryApiCall(
    maxRetries: Int = 3,
    initialDelay: Long = 1000L,
    apiCall: suspend () -> Result<T>
): Result<T> {
    repeat(maxRetries) { attempt ->
        val result = apiCall()

        if (result.isSuccess) {
            return result
        }

        if (attempt < maxRetries - 1) {
            delay(initialDelay * (2L.pow(attempt)))
        }
    }

    return apiCall() // 最后一次尝试
}
```

## 💾 数据缓存策略

### 1. 菜单数据缓存

```kotlin
class MenuCacheManager @Inject constructor(
    private val preferences: DataStore<Preferences>
) {
    private val MENU_CACHE_KEY = stringPreferencesKey("menu_cache")
    private val CACHE_TIMESTAMP_KEY = longPreferencesKey("cache_timestamp")
    private val CACHE_DURATION = 5 * 60 * 1000L // 5分钟

    suspend fun cacheMenus(menus: List<MenuItemDTO>) {
        val json = Json.encodeToString(menus)
        preferences.edit { prefs ->
            prefs[MENU_CACHE_KEY] = json
            prefs[CACHE_TIMESTAMP_KEY] = System.currentTimeMillis()
        }
    }

    suspend fun getCachedMenus(): List<MenuItemDTO>? {
        val currentTime = System.currentTimeMillis()

        return preferences.data.first().let { prefs ->
            val timestamp = prefs[CACHE_TIMESTAMP_KEY] ?: 0
            val json = prefs[MENU_CACHE_KEY]

            if (json != null && (currentTime - timestamp) < CACHE_DURATION) {
                Json.decodeFromString<List<MenuItemDTO>>(json)
            } else {
                null
            }
        }
    }

    suspend fun clearCache() {
        preferences.edit { prefs ->
            prefs.remove(MENU_CACHE_KEY)
            prefs.remove(CACHE_TIMESTAMP_KEY)
        }
    }
}
```

## 🔧 调试和测试工具

### 1. API调试工具

```kotlin
object MenuApiDebugger {
    private const val TAG = "MenuAPI"

    fun logApiCall(
        endpoint: String,
        method: String,
        headers: Map<String, String> = emptyMap(),
        body: String? = null
    ) {
        if (BuildConfig.DEBUG) {
            Log.d(TAG, "=== API调用 ===")
            Log.d(TAG, "端点: $endpoint")
            Log.d(TAG, "方法: $method")
            Log.d(TAG, "请求头: $headers")
            if (body != null) {
                Log.d(TAG, "请求体: $body")
            }
        }
    }

    fun logApiResponse(
        endpoint: String,
        statusCode: Int,
        response: String
    ) {
        if (BuildConfig.DEBUG) {
            Log.d(TAG, "=== API响应 ===")
            Log.d(TAG, "端点: $endpoint")
            Log.d(TAG, "状态码: $statusCode")
            Log.d(TAG, "响应: $response")
        }
    }
}
```

### 2. 单元测试示例

```kotlin
@Test
fun `test menu serialization and deserialization`() = runTest {
    // 测试菜单序列化
    val originalMenu = MenuItemDTO(
        id = "dashboard",
        name = "dashboard",
        title = "总览",
        titleEn = "Dashboard",
        path = "/",
        component = "Dashboard",
        icon = "dashboard",
        emoji = "🏠",
        parentId = null,
        permission = "menu:dashboard",
        menuType = MenuType.MENU,
        sortOrder = 1,
        isHidden = false,
        isExternal = false,
        status = "active",
        meta = mapOf("keepAlive" to "true"),
        children = emptyList()
    )

    val json = Json.encodeToString(originalMenu)
    val deserializedMenu = Json.decodeFromString<MenuItemDTO>(json)

    assertEquals(originalMenu.id, deserializedMenu.id)
    assertEquals(originalMenu.title, deserializedMenu.title)
    assertEquals(originalMenu.menuType, deserializedMenu.menuType)
}

@Test
fun `test api error handling`() = runTest {
    val mockApiService = mockk<MenuApiService>()
    val expectedError = APIErrorDTO("权限不足", 403)

    coEvery { mockApiService.getUserMenus() } returns Result.failure(
        Exception("HTTP 403: 权限不足")
    )

    val result = mockApiService.getUserMenus()

    assertTrue(result.isFailure)
    assertTrue(result.exceptionOrNull()?.message?.contains("403") == true)
}
```

## 📝 最佳实践和注意事项

### 1. 序列化注意事项

```kotlin
// ✅ 正确的序列化映射
@Serializable
data class MenuItemDTO(
    @SerialName("id") val id: String,
    @SerialName("is_hidden") val isHidden: Boolean, // 注意下划线映射
    @SerialName("menu_type") val menuType: MenuType  // 枚举类型映射
)

// ❌ 错误的做法
@Serializable
data class MenuItemDTO(
    val id: String,           // 缺少@SerialName映射
    val isHidden: Boolean,    // 字段名不匹配API
    val menuType: String      // 应该使用枚举类型
)
```

### 2. 空值处理

```kotlin
// ✅ 正确的空值处理
@Serializable
data class MenuItemDTO(
    @SerialName("title_en") val titleEn: String? = null,  // 可空字段
    @SerialName("meta") val meta: Map<String, String> = emptyMap(), // 默认值
    @SerialName("children") val children: List<MenuItemDTO> = emptyList() // 默认空列表
)
```

### 3. 性能优化

```kotlin
// 使用懒加载和缓存
class OptimizedMenuManager {
    private val menuCache by lazy { mutableMapOf<String, MenuItemDTO>() }
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun preloadMenus(userId: String) {
        scope.launch {
            // 预加载菜单数据
            loadUserMenusAsync(userId)
        }
    }
}
```

### 4. 内存管理

```kotlin
// 及时释放资源
class MenuActivity : AppCompatActivity() {
    private val menuManager = MenuManager()

    override fun onDestroy() {
        super.onDestroy()
        menuManager.cleanup() // 重要：释放HTTP客户端资源
    }
}
```

## 🎯 核心菜单项集成参考

```kotlin
object MenuIntegrationHelper {
    // 核心菜单路由映射
    val MENU_ROUTES = mapOf(
        MenuIds.DASHBOARD to "dashboard",
        MenuIds.TRADING_CALENDAR to "trading-calendar",
        MenuIds.PROXY_POOL to "proxy-pool",
        MenuIds.MARKET_CONFIG to "market-config"
    )

    // 菜单权限检查
    suspend fun checkAndNavigate(
        menuId: String,
        menuManager: MenuManager,
        navController: NavController
    ) {
        if (menuManager.hasMenuPermission(menuId)) {
            val route = MENU_ROUTES[menuId]
            if (route != null) {
                navController.navigate(route)
            }
        } else {
            // 显示权限不足提示
            showPermissionDeniedDialog()
        }
    }
}
```

这个最小化菜单模块确保了使用 **Kotlin Quickly** 框架的UI能够准确对接所有菜单相关功能，避免接口调用错误和序列化问题。