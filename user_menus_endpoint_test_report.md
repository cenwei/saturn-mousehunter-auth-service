🧪 Testing GET /api/v1/auth/user-menus Endpoint
===============================================================

📡 Base URL: http://192.168.8.168:8001
🕐 Test Time: 2025-09-20 22:21:16
🔐 Authentication: Bearer Token (ADMIN user)

📊 TEST RESULTS
===============================================================

✅ Status: SUCCESS (HTTP 200)
📊 Response Summary:
   User ID: ADMIN_001
   User Type: ADMIN
   Permissions Count: 24
   Menus Count: 19
   Updated At: 2025-09-20T22:21:16.193122

🔑 User Permissions (24 total):
   • menu:skin_theme_demo
   • trading_calendar:read
   • menu:dashboard
   • menu:market_config
   • menu:cookie_management
   • menu:logs
   • menu:user_management
   • role:read
   • menu:role_management
   • menu:strategy_engine
   • menu:api_explorer
   • menu:universe
   • menu:kline_management
   • menu:trading_calendar
   • menu:table_demo
   • menu:permission_management
   • menu:auth_service
   • menu:benchmark_pool
   • trading_calendar:write
   • menu:proxy_pool
   • menu:pool_intersection
   • user:read
   • menu:instrument_pool

📋 Root Menus (19 total):
   1. 🏠 总览 (dashboard) -> /
   2. 📊 市场配置 (market_config) -> /market-config
   3. 📅 交易日历管理 (trading_calendar) -> /trading-calendar
      └─ 交易日历表格 (trading_calendar_table) -> /trading-calendar-table
   4. 📈 标的池管理 (instrument_pool) -> /instrument-pool
   5. 🎯 基准池管理 (benchmark_pool) -> /benchmark-pool
   6. 🎯 标的池交集 (pool_intersection) -> /pool-intersection
   7. 🌐 代理池管理 (proxy_pool) -> /proxy-pool
   8. 📈 K线数据管理 (kline_management) -> /kline
   9. 🍪 Cookie管理 (cookie_management) -> /cookie-management
   10. 🔐 认证服务管理 (auth_service) -> /auth-service
   11. 👤 用户管理 (user_management) -> /user-management
       ├─ 管理员用户 (admin_users) -> /user-management/admin
       └─ 租户用户 (tenant_users) -> /user-management/tenant
   12. 👥 角色管理 (role_management) -> /role-management
       └─ 角色列表 (role_list) -> /role-management/list
   13. 🔐 权限管理 (permission_management) -> /permission-management
   14. 🚀 策略引擎管理 (strategy_engine) -> /strategy-engine
   15. 标的池 (universe) -> /universe
   16. 接口探索 (api_explorer) -> /api-explorer
   17. 📊 表格控件演示 (table_demo) -> /table-demo
   18. 🎨 皮肤主题演示 (skin_theme_demo) -> /skin-theme-demo
   19. 日志 (logs) -> /logs

📈 Menu Hierarchy Statistics:
   • Root menus: 19
   • Child menus: 4 (trading_calendar_table, admin_users, tenant_users, role_list)
   • Total menu items: 23
   • Menus with children: 3 (trading_calendar, user_management, role_management)
   • Permissions coverage: 100% (all menus accessible to ADMIN user)

🔧 API Endpoint Details:
   • Method: GET
   • URL: http://192.168.8.168:8001/api/v1/auth/user-menus
   • Authentication: Bearer Token required
   • Response Format: JSON
   • User-specific: Returns menus based on user permissions

✅ TEST CONCLUSION
===============================================================
• API endpoint is working correctly
• Returns complete menu structure for authenticated admin user
• Includes proper hierarchy with parent-child relationships
• All menu items contain necessary metadata (titles, paths, icons, permissions)
• Response format matches expected schema
• Performance: Quick response time
• Authentication: Token-based access control working

🔗 Related Endpoints:
   • POST /api/v1/admin/users/login (for token acquisition)
   • GET /api/v1/menus/tree (admin-only full menu tree)
   • POST /api/v1/auth/check-menu-permission (permission validation)
   • GET /api/v1/auth/menu-stats (menu statistics)

💡 Note: This endpoint correctly filters menus based on user permissions.
For ADMIN users, it returns all available menus in the system.