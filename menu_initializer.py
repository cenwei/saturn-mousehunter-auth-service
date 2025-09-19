#!/usr/bin/env python3
"""
Saturn MHC 菜单初始化脚本

此脚本用于：
1. 初始化Saturn MHC完整菜单配置
2. 验证菜单权限映射
3. 生成菜单数据用于前端集成
4. 创建菜单配置备份
"""
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.models.auth_menu import (
    SATURN_MHC_MENU_CONFIG, MENU_PERMISSIONS, DEFAULT_MENU_CONFIG,
    MenuConfig, MenuTree
)
from domain.models.auth_user_role import UserType
from application.services.menu_permission_service import MenuPermissionService


class MockUserRoleRepo:
    """模拟用户角色仓库"""
    async def get_user_permissions(self, user_id: str, user_type: UserType):
        class MockPermissions:
            def __init__(self, permissions):
                self.permissions = permissions
        return MockPermissions([])


class MenuInitializer:
    """菜单初始化器"""

    def __init__(self):
        self.mock_repo = MockUserRoleRepo()
        self.menu_service = MenuPermissionService(self.mock_repo, use_saturn_mhc_menus=True)

    def generate_menu_statistics(self) -> Dict[str, Any]:
        """生成菜单统计信息"""
        stats = {
            "total_menus": len(SATURN_MHC_MENU_CONFIG),
            "total_permissions": len(MENU_PERMISSIONS),
            "root_menus": len(SATURN_MHC_MENU_CONFIG),
            "child_menus": 0,
            "menu_types": {},
            "permission_distribution": {},
            "generated_at": datetime.now().isoformat()
        }

        # 统计子菜单
        for menu in SATURN_MHC_MENU_CONFIG:
            if menu.children:
                stats["child_menus"] += len(menu.children)

        # 统计菜单类型
        all_menus = self._flatten_menus(SATURN_MHC_MENU_CONFIG)
        for menu in all_menus:
            menu_type = menu.menu_type.value
            stats["menu_types"][menu_type] = stats["menu_types"].get(menu_type, 0) + 1

        # 统计权限分布
        for permission, roles in MENU_PERMISSIONS.items():
            for role in roles:
                stats["permission_distribution"][role] = stats["permission_distribution"].get(role, 0) + 1

        return stats

    def _flatten_menus(self, menus: List[MenuConfig]) -> List[MenuConfig]:
        """展平菜单列表"""
        flattened = []
        for menu in menus:
            flattened.append(menu)
            if menu.children:
                flattened.extend(self._flatten_menus(menu.children))
        return flattened

    def generate_frontend_menu_config(self) -> Dict[str, Any]:
        """生成前端菜单配置"""
        def menu_to_frontend_format(menu: MenuConfig) -> Dict[str, Any]:
            """将菜单配置转换为前端格式"""
            frontend_menu = {
                "id": menu.id,
                "name": menu.name,
                "title": menu.title,
                "path": menu.path,
                "component": getattr(menu, 'component', None),
                "icon": menu.emoji if menu.emoji else menu.icon,
                "permission": menu.permission,
                "sort_order": menu.sort_order,
                "meta": {
                    "title": menu.title,
                    "keepAlive": menu.meta.get("keepAlive", False) if menu.meta else False,
                    "hidden": menu.is_hidden,
                    "external": menu.is_external
                }
            }

            # 添加英文标题
            if hasattr(menu, 'title_en') and menu.title_en:
                frontend_menu["title_en"] = menu.title_en
                frontend_menu["meta"]["title_en"] = menu.title_en

            # 处理子菜单
            if menu.children:
                frontend_menu["children"] = [
                    menu_to_frontend_format(child) for child in menu.children
                ]

            return frontend_menu

        frontend_config = {
            "menus": [menu_to_frontend_format(menu) for menu in SATURN_MHC_MENU_CONFIG],
            "permissions": MENU_PERMISSIONS,
            "config_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_menus": len(self._flatten_menus(SATURN_MHC_MENU_CONFIG))
        }

        return frontend_config

    def generate_kotlin_serialization_classes(self) -> str:
        """生成Kotlin序列化类"""
        kotlin_code = '''/**
 * Saturn MHC Menu Configuration - Kotlin Serialization Classes
 * Generated on: {timestamp}
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
enum class UserType(val value: String) {{
    ADMIN("ADMIN"),
    TENANT("TENANT"),
    LIMITED("LIMITED")
}}

/**
 * 菜单类型枚举
 */
enum class MenuType(val value: String) {{
    MENU("menu"),
    BUTTON("button"),
    TAB("tab")
}}
'''.format(timestamp=datetime.now().isoformat())

        return kotlin_code

    def validate_menu_configuration(self) -> Dict[str, Any]:
        """验证菜单配置"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }

        # 检查菜单ID唯一性
        all_menus = self._flatten_menus(SATURN_MHC_MENU_CONFIG)
        menu_ids = [menu.id for menu in all_menus]
        duplicate_ids = [mid for mid in set(menu_ids) if menu_ids.count(mid) > 1]
        if duplicate_ids:
            validation_result["errors"].append(f"重复的菜单ID: {duplicate_ids}")
            validation_result["is_valid"] = False

        # 检查权限映射完整性
        menu_permissions = set()
        for menu in all_menus:
            if menu.permission:
                menu_permissions.add(menu.permission)

        mapped_permissions = set(MENU_PERMISSIONS.keys())
        missing_permissions = menu_permissions - mapped_permissions
        if missing_permissions:
            validation_result["warnings"].append(f"缺少权限映射: {list(missing_permissions)}")

        unused_permissions = mapped_permissions - menu_permissions
        if unused_permissions:
            validation_result["warnings"].append(f"未使用的权限映射: {list(unused_permissions)}")

        # 检查路径唯一性
        menu_paths = [menu.path for menu in all_menus if menu.path]
        duplicate_paths = [path for path in set(menu_paths) if menu_paths.count(path) > 1]
        if duplicate_paths:
            validation_result["errors"].append(f"重复的菜单路径: {duplicate_paths}")
            validation_result["is_valid"] = False

        # 检查父子关系
        for menu in all_menus:
            if hasattr(menu, 'parent_id') and menu.parent_id:
                parent_exists = any(m.id == menu.parent_id for m in all_menus)
                if not parent_exists:
                    validation_result["errors"].append(f"菜单 {menu.id} 的父菜单 {menu.parent_id} 不存在")
                    validation_result["is_valid"] = False

        validation_result["summary"] = {
            "total_menus": len(all_menus),
            "unique_permissions": len(menu_permissions),
            "mapped_permissions": len(mapped_permissions),
            "unique_paths": len(set(menu_paths)),
            "errors_count": len(validation_result["errors"]),
            "warnings_count": len(validation_result["warnings"])
        }

        return validation_result

    async def test_user_permissions(self) -> Dict[str, Any]:
        """测试不同用户类型的权限"""
        permission_test = {
            "test_results": {},
            "coverage_analysis": {}
        }

        user_types = [UserType.ADMIN, UserType.TENANT, UserType.LIMITED]

        for user_type in user_types:
            try:
                # 获取用户菜单
                user_menus = await self.menu_service.get_user_accessible_menus(
                    f"test_{user_type.value.lower()}_user",
                    user_type
                )

                # 获取统计信息
                stats = await self.menu_service.get_menu_stats(
                    f"test_{user_type.value.lower()}_user",
                    user_type
                )

                permission_test["test_results"][user_type.value] = {
                    "accessible_menus": len(user_menus.menus),
                    "total_permissions": len(user_menus.permissions),
                    "coverage_percentage": stats.permission_coverage,
                    "menu_list": [
                        {
                            "id": menu.id,
                            "title": menu.title,
                            "path": menu.path,
                            "permission": menu.permission
                        }
                        for menu in user_menus.menus
                    ]
                }

            except Exception as e:
                permission_test["test_results"][user_type.value] = {
                    "error": str(e)
                }

        # 分析权限覆盖率
        permission_test["coverage_analysis"] = {
            "admin_coverage": permission_test["test_results"].get("ADMIN", {}).get("coverage_percentage", 0),
            "tenant_coverage": permission_test["test_results"].get("TENANT", {}).get("coverage_percentage", 0),
            "limited_coverage": permission_test["test_results"].get("LIMITED", {}).get("coverage_percentage", 0)
        }

        return permission_test

    def export_menu_data(self, output_dir: Path) -> Dict[str, str]:
        """导出菜单数据到文件"""
        output_dir.mkdir(exist_ok=True)
        exported_files = {}

        # 1. 菜单统计
        stats = self.generate_menu_statistics()
        stats_file = output_dir / "menu_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        exported_files["statistics"] = str(stats_file)

        # 2. 前端配置
        frontend_config = self.generate_frontend_menu_config()
        frontend_file = output_dir / "frontend_menu_config.json"
        with open(frontend_file, 'w', encoding='utf-8') as f:
            json.dump(frontend_config, f, ensure_ascii=False, indent=2)
        exported_files["frontend_config"] = str(frontend_file)

        # 3. Kotlin序列化类
        kotlin_code = self.generate_kotlin_serialization_classes()
        kotlin_file = output_dir / "MenuApiModels.kt"
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(kotlin_code)
        exported_files["kotlin_models"] = str(kotlin_file)

        # 4. 验证报告
        validation = self.validate_menu_configuration()
        validation_file = output_dir / "menu_validation_report.json"
        with open(validation_file, 'w', encoding='utf-8') as f:
            json.dump(validation, f, ensure_ascii=False, indent=2)
        exported_files["validation"] = str(validation_file)

        return exported_files


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Saturn MHC 菜单初始化脚本")
    parser.add_argument("--output-dir", "-o", type=str, default="./menu_export",
                       help="输出目录 (默认: ./menu_export)")
    parser.add_argument("--validate-only", "-v", action="store_true",
                       help="仅验证菜单配置，不导出文件")
    parser.add_argument("--test-permissions", "-t", action="store_true",
                       help="测试用户权限")
    parser.add_argument("--stats-only", "-s", action="store_true",
                       help="仅显示统计信息")

    args = parser.parse_args()

    print("🚀 Saturn MHC Menu Initializer")
    print("=" * 60)
    print()

    initializer = MenuInitializer()

    try:
        # 显示基本统计
        if not args.validate_only:
            print("📊 Menu Statistics:")
            stats = initializer.generate_menu_statistics()
            print(f"   Total menus: {stats['total_menus']}")
            print(f"   Root menus: {stats['root_menus']}")
            print(f"   Child menus: {stats['child_menus']}")
            print(f"   Total permissions: {stats['total_permissions']}")
            print(f"   Permission distribution:")
            for role, count in stats['permission_distribution'].items():
                print(f"     {role}: {count} permissions")
            print()

            if args.stats_only:
                return 0

        # 验证配置
        print("🔍 Validating Menu Configuration:")
        validation = initializer.validate_menu_configuration()
        if validation["is_valid"]:
            print("   ✅ Menu configuration is valid!")
        else:
            print("   ❌ Menu configuration has errors:")
            for error in validation["errors"]:
                print(f"     - {error}")

        if validation["warnings"]:
            print("   ⚠️  Warnings:")
            for warning in validation["warnings"]:
                print(f"     - {warning}")

        print(f"   Summary: {validation['summary']['total_menus']} menus, "
              f"{validation['summary']['errors_count']} errors, "
              f"{validation['summary']['warnings_count']} warnings")
        print()

        if args.validate_only:
            return 0 if validation["is_valid"] else 1

        # 测试权限
        if args.test_permissions:
            print("🔐 Testing User Permissions:")
            permission_test = await initializer.test_user_permissions()
            for user_type, result in permission_test["test_results"].items():
                if "error" in result:
                    print(f"   {user_type}: ❌ {result['error']}")
                else:
                    print(f"   {user_type}: {result['accessible_menus']} menus "
                          f"({result['coverage_percentage']:.1f}% coverage)")
            print()

        # 导出文件
        output_dir = Path(args.output_dir)
        print(f"📁 Exporting menu data to: {output_dir}")
        exported_files = initializer.export_menu_data(output_dir)

        print("   Exported files:")
        for file_type, file_path in exported_files.items():
            print(f"     {file_type}: {file_path}")
        print()

        # 生成使用说明
        readme_content = f"""# Saturn MHC Menu Configuration Export

Generated on: {datetime.now().isoformat()}

## Files Description

1. **menu_statistics.json** - 菜单统计信息
2. **frontend_menu_config.json** - 前端菜单配置
3. **MenuApiModels.kt** - Kotlin序列化类
4. **menu_validation_report.json** - 配置验证报告

## Usage

### Frontend Integration
```javascript
// Load menu configuration
import menuConfig from './frontend_menu_config.json';

// Use menus
const menus = menuConfig.menus;
const permissions = menuConfig.permissions;
```

### Kotlin Client Integration
```kotlin
// Copy MenuApiModels.kt to your Kotlin project
// Use the serialization classes for API communication
val userMenusResponse = authClient.getUserMenus(token)
```

## Next Steps

1. 将 frontend_menu_config.json 集成到前端项目
2. 将 MenuApiModels.kt 集成到 Kotlin 客户端
3. 根据验证报告修复任何配置问题
4. 测试不同用户角色的菜单访问权限

Generated by Saturn MHC Menu Initializer
"""

        readme_file = output_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✅ Menu initialization completed successfully!")
        print(f"📋 Check {readme_file} for usage instructions")

        return 0

    except Exception as e:
        print(f"❌ Menu initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)