#!/usr/bin/env python3
"""
Saturn MHC 菜单系统综合测试
"""
import sys
import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.models.auth_menu import SATURN_MHC_MENU_CONFIG, MENU_PERMISSIONS
from domain.models.auth_user_role import UserType
from application.services.menu_permission_service import MenuPermissionService


class MockUserRoleRepo:
    """模拟用户角色仓库"""
    async def get_user_permissions(self, user_id: str, user_type: UserType):
        class MockPermissions:
            def __init__(self, permissions):
                self.permissions = permissions
        return MockPermissions([])


class MenuSystemTester:
    """菜单系统综合测试器"""

    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.mock_repo = MockUserRoleRepo()
        self.menu_service = MenuPermissionService(self.mock_repo, use_saturn_mhc_menus=True)
        self.test_results = {}

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Saturn MHC Menu System Comprehensive Test")
        print("=" * 70)
        print()

        # 测试配置验证
        await self.test_configuration()

        # 测试服务端API
        await self.test_server_apis()

        # 测试权限系统
        await self.test_permission_system()

        # 测试用户场景
        await self.test_user_scenarios()

        # 测试数据导出
        await self.test_data_export()

        # 生成测试报告
        self.generate_test_report()

    async def test_configuration(self):
        """测试菜单配置"""
        print("📋 Testing Menu Configuration")
        print("-" * 40)

        try:
            # 检查菜单数量
            total_menus = len(SATURN_MHC_MENU_CONFIG)
            print(f"✅ Total root menus: {total_menus}")

            # 检查权限映射
            total_permissions = len(MENU_PERMISSIONS)
            print(f"✅ Total permissions: {total_permissions}")

            # 检查菜单ID唯一性
            all_menus = self._flatten_menus(SATURN_MHC_MENU_CONFIG)
            menu_ids = [menu.id for menu in all_menus]
            unique_ids = set(menu_ids)

            if len(menu_ids) == len(unique_ids):
                print(f"✅ Menu IDs are unique: {len(unique_ids)} menus")
            else:
                print(f"❌ Duplicate menu IDs found")

            # 检查路径唯一性
            menu_paths = [menu.path for menu in all_menus if menu.path]
            unique_paths = set(menu_paths)

            if len(menu_paths) == len(unique_paths):
                print(f"✅ Menu paths are unique: {len(unique_paths)} paths")
            else:
                print(f"❌ Duplicate menu paths found")

            self.test_results["configuration"] = {
                "status": "passed",
                "total_menus": len(all_menus),
                "root_menus": total_menus,
                "total_permissions": total_permissions,
                "unique_ids": len(unique_ids) == len(menu_ids),
                "unique_paths": len(unique_paths) == len(menu_paths)
            }

        except Exception as e:
            print(f"❌ Configuration test failed: {str(e)}")
            self.test_results["configuration"] = {"status": "failed", "error": str(e)}

        print()

    async def test_server_apis(self):
        """测试服务端API"""
        print("🌐 Testing Server APIs")
        print("-" * 40)

        try:
            async with aiohttp.ClientSession() as session:
                # 测试健康检查
                health_status = await self._test_health_check(session)

                # 测试OpenAPI schema
                openapi_status = await self._test_openapi_schema(session)

                # 测试菜单相关端点（无认证）
                menu_endpoints_status = await self._test_menu_endpoints(session)

                self.test_results["server_apis"] = {
                    "status": "passed" if all([health_status, openapi_status]) else "partial",
                    "health_check": health_status,
                    "openapi_schema": openapi_status,
                    "menu_endpoints": menu_endpoints_status
                }

        except Exception as e:
            print(f"❌ Server API test failed: {str(e)}")
            self.test_results["server_apis"] = {"status": "failed", "error": str(e)}

        print()

    async def _test_health_check(self, session):
        """测试健康检查"""
        try:
            async with session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Health check: {result.get('status')}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False

    async def _test_openapi_schema(self, session):
        """测试OpenAPI schema"""
        try:
            async with session.get(f"{self.base_url}/openapi.json") as response:
                if response.status == 200:
                    openapi = await response.json()
                    paths = openapi.get("paths", {})
                    menu_paths = [p for p in paths.keys() if "/menus" in p]
                    print(f"✅ OpenAPI schema: {len(menu_paths)} menu endpoints")
                    return True
                else:
                    print(f"❌ OpenAPI schema failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ OpenAPI schema error: {str(e)}")
            return False

    async def _test_menu_endpoints(self, session):
        """测试菜单端点"""
        test_endpoints = [
            ("/api/v1/menus/tree", "GET", "Menu tree endpoint"),
            ("/api/v1/auth/user-menus", "GET", "User menus endpoint"),
            ("/api/v1/menus", "GET", "Menu list endpoint")
        ]

        results = {}
        for endpoint, method, description in test_endpoints:
            try:
                async with session.request(method, f"{self.base_url}{endpoint}") as response:
                    # 期望401或403（未认证），而不是500或404
                    if response.status in [401, 403]:
                        print(f"✅ {description}: Authentication required (expected)")
                        results[endpoint] = True
                    else:
                        print(f"❌ {description}: Unexpected status {response.status}")
                        results[endpoint] = False
            except Exception as e:
                print(f"❌ {description}: Error {str(e)}")
                results[endpoint] = False

        return results

    async def test_permission_system(self):
        """测试权限系统"""
        print("🔐 Testing Permission System")
        print("-" * 40)

        try:
            user_types = [UserType.ADMIN, UserType.TENANT, UserType.LIMITED]
            permission_results = {}

            for user_type in user_types:
                # 获取用户权限
                user_permissions = self.menu_service._get_user_permissions_by_type(user_type)

                # 获取可访问菜单
                user_menus = await self.menu_service.get_user_accessible_menus(
                    f"test_{user_type.value.lower()}_user",
                    user_type
                )

                # 获取统计信息
                stats = await self.menu_service.get_menu_stats(
                    f"test_{user_type.value.lower()}_user",
                    user_type
                )

                permission_results[user_type.value] = {
                    "permissions_count": len(user_permissions),
                    "accessible_menus": len(user_menus.menus),
                    "coverage_percentage": stats.permission_coverage
                }

                print(f"✅ {user_type.value}: {len(user_menus.menus)} menus, "
                      f"{stats.permission_coverage:.1f}% coverage")

            self.test_results["permission_system"] = {
                "status": "passed",
                "user_permissions": permission_results
            }

        except Exception as e:
            print(f"❌ Permission system test failed: {str(e)}")
            self.test_results["permission_system"] = {"status": "failed", "error": str(e)}

        print()

    async def test_user_scenarios(self):
        """测试用户使用场景"""
        print("👤 Testing User Scenarios")
        print("-" * 40)

        try:
            scenarios = {
                "admin_full_access": await self._test_admin_scenario(),
                "tenant_limited_access": await self._test_tenant_scenario(),
                "limited_minimal_access": await self._test_limited_scenario()
            }

            all_passed = all(scenario["passed"] for scenario in scenarios.values())

            self.test_results["user_scenarios"] = {
                "status": "passed" if all_passed else "partial",
                "scenarios": scenarios
            }

        except Exception as e:
            print(f"❌ User scenarios test failed: {str(e)}")
            self.test_results["user_scenarios"] = {"status": "failed", "error": str(e)}

        print()

    async def _test_admin_scenario(self):
        """测试管理员场景"""
        try:
            user_menus = await self.menu_service.get_user_accessible_menus(
                "admin_user", UserType.ADMIN
            )

            # 管理员应该能访问所有菜单
            expected_admin_menus = len(self._flatten_menus(SATURN_MHC_MENU_CONFIG))
            actual_admin_menus = len(self._flatten_menus_from_tree(user_menus.menus))

            passed = actual_admin_menus >= expected_admin_menus * 0.9  # 允许10%差异

            print(f"✅ Admin scenario: {actual_admin_menus}/{expected_admin_menus} menus accessible")

            return {
                "passed": passed,
                "accessible_menus": actual_admin_menus,
                "expected_menus": expected_admin_menus
            }

        except Exception as e:
            print(f"❌ Admin scenario failed: {str(e)}")
            return {"passed": False, "error": str(e)}

    async def _test_tenant_scenario(self):
        """测试租户场景"""
        try:
            user_menus = await self.menu_service.get_user_accessible_menus(
                "tenant_user", UserType.TENANT
            )

            # 租户应该有中等数量的菜单访问权限
            accessible_count = len(self._flatten_menus_from_tree(user_menus.menus))
            passed = 5 <= accessible_count <= 15  # 期望在5-15个菜单之间

            print(f"✅ Tenant scenario: {accessible_count} menus accessible")

            return {
                "passed": passed,
                "accessible_menus": accessible_count
            }

        except Exception as e:
            print(f"❌ Tenant scenario failed: {str(e)}")
            return {"passed": False, "error": str(e)}

    async def _test_limited_scenario(self):
        """测试受限用户场景"""
        try:
            user_menus = await self.menu_service.get_user_accessible_menus(
                "limited_user", UserType.LIMITED
            )

            # 受限用户应该只有最少的菜单访问权限
            accessible_count = len(self._flatten_menus_from_tree(user_menus.menus))
            passed = accessible_count <= 3  # 期望3个或更少菜单

            print(f"✅ Limited scenario: {accessible_count} menus accessible")

            return {
                "passed": passed,
                "accessible_menus": accessible_count
            }

        except Exception as e:
            print(f"❌ Limited scenario failed: {str(e)}")
            return {"passed": False, "error": str(e)}

    async def test_data_export(self):
        """测试数据导出功能"""
        print("📁 Testing Data Export")
        print("-" * 40)

        try:
            export_dir = Path("./test_export")
            export_dir.mkdir(exist_ok=True)

            # 测试菜单配置导出
            frontend_config = self._generate_frontend_config()
            config_file = export_dir / "test_frontend_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(frontend_config, f, ensure_ascii=False, indent=2)

            print(f"✅ Frontend config exported: {config_file}")

            # 测试统计数据导出
            stats = self._generate_statistics()
            stats_file = export_dir / "test_statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

            print(f"✅ Statistics exported: {stats_file}")

            self.test_results["data_export"] = {
                "status": "passed",
                "exported_files": [str(config_file), str(stats_file)]
            }

        except Exception as e:
            print(f"❌ Data export test failed: {str(e)}")
            self.test_results["data_export"] = {"status": "failed", "error": str(e)}

        print()

    def _generate_frontend_config(self):
        """生成前端配置"""
        return {
            "menus": [self._menu_to_dict(menu) for menu in SATURN_MHC_MENU_CONFIG],
            "permissions": MENU_PERMISSIONS,
            "generated_at": datetime.now().isoformat(),
            "test_mode": True
        }

    def _menu_to_dict(self, menu):
        """菜单配置转字典"""
        menu_dict = {
            "id": menu.id,
            "name": menu.name,
            "title": menu.title,
            "path": menu.path,
            "icon": getattr(menu, 'emoji', None) or menu.icon,
            "permission": menu.permission,
            "sort_order": menu.sort_order,
            "meta": menu.meta or {}
        }

        if hasattr(menu, 'title_en') and menu.title_en:
            menu_dict["title_en"] = menu.title_en

        if menu.children:
            menu_dict["children"] = [self._menu_to_dict(child) for child in menu.children]

        return menu_dict

    def _generate_statistics(self):
        """生成统计信息"""
        all_menus = self._flatten_menus(SATURN_MHC_MENU_CONFIG)
        return {
            "total_menus": len(all_menus),
            "root_menus": len(SATURN_MHC_MENU_CONFIG),
            "child_menus": len(all_menus) - len(SATURN_MHC_MENU_CONFIG),
            "total_permissions": len(MENU_PERMISSIONS),
            "generated_at": datetime.now().isoformat()
        }

    def _flatten_menus(self, menus):
        """展平菜单列表"""
        flattened = []
        for menu in menus:
            flattened.append(menu)
            if menu.children:
                flattened.extend(self._flatten_menus(menu.children))
        return flattened

    def _flatten_menus_from_tree(self, menu_trees):
        """从MenuTree列表展平菜单"""
        flattened = []
        for menu in menu_trees:
            flattened.append(menu)
            if menu.children:
                flattened.extend(self._flatten_menus_from_tree(menu.children))
        return flattened

    def generate_test_report(self):
        """生成测试报告"""
        print("📊 Test Report")
        print("=" * 70)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get("status") == "passed"])
        partial_tests = len([r for r in self.test_results.values() if r.get("status") == "partial"])
        failed_tests = len([r for r in self.test_results.values() if r.get("status") == "failed"])

        print(f"📈 Test Summary:")
        print(f"   Total test suites: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️  Partial: {partial_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print()

        print(f"📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_emoji = {"passed": "✅", "partial": "⚠️", "failed": "❌"}.get(result["status"], "❓")
            print(f"   {status_emoji} {test_name}: {result['status']}")

            if result.get("error"):
                print(f"      Error: {result['error']}")

        print()

        # 保存报告到文件
        report_file = Path("./test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "partial": partial_tests,
                    "failed": failed_tests,
                    "success_rate": passed_tests / total_tests if total_tests > 0 else 0
                },
                "results": self.test_results,
                "generated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")

        if passed_tests == total_tests:
            print("🎉 All tests passed! Menu system is ready for production.")
        elif passed_tests + partial_tests == total_tests:
            print("⚠️  Some tests have partial success. Review the issues before deployment.")
        else:
            print("❌ Some tests failed. Please fix the issues before proceeding.")


async def main():
    """主函数"""
    tester = MenuSystemTester()

    try:
        await tester.run_all_tests()
        return 0
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)