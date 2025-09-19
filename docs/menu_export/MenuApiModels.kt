/**
 * Saturn MHC Menu Configuration - Kotlin Serialization Classes
 * Generated on: 2025-09-19T23:39:13.842956
 *
 * 这些类用于Saturn MHC前端与菜单API的数据交换
 */

import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName

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
)

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

/**
 * 菜单权限类型枚举
 */
enum class UserType(val value: String) {
    ADMIN("ADMIN"),
    TENANT("TENANT"),
    LIMITED("LIMITED")
}

/**
 * 菜单类型枚举
 */
enum class MenuType(val value: String) {
    MENU("menu"),
    BUTTON("button"),
    TAB("tab")
}
