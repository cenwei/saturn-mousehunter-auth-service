"""
认证服务 - 菜单数据库存储库
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.auth_menu import MenuConfig, MenuType

log = get_logger(__name__)


class MenuRepo:
    """菜单数据库存储库"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    async def initialize_tables(self):
        """初始化菜单相关表"""
        create_menu_table_sql = """
        CREATE TABLE IF NOT EXISTS auth_menus (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            title VARCHAR(200) NOT NULL,
            title_en VARCHAR(200),
            path VARCHAR(500),
            component VARCHAR(200),
            icon VARCHAR(50),
            emoji VARCHAR(10),
            parent_id VARCHAR(50),
            permission VARCHAR(100),
            menu_type VARCHAR(20) DEFAULT 'menu',
            sort_order INTEGER DEFAULT 0,
            is_hidden BOOLEAN DEFAULT FALSE,
            is_external BOOLEAN DEFAULT FALSE,
            status VARCHAR(20) DEFAULT 'active',
            meta JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by VARCHAR(50),
            updated_by VARCHAR(50),
            FOREIGN KEY (parent_id) REFERENCES auth_menus(id) ON DELETE CASCADE
        );
        """

        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_auth_menus_parent_id ON auth_menus(parent_id);",
            "CREATE INDEX IF NOT EXISTS idx_auth_menus_status ON auth_menus(status);",
            "CREATE INDEX IF NOT EXISTS idx_auth_menus_sort_order ON auth_menus(sort_order);",
            "CREATE INDEX IF NOT EXISTS idx_auth_menus_permission ON auth_menus(permission);",
        ]

        try:
            async with self.dao.acquire() as conn:
                await conn.execute(create_menu_table_sql)
                for index_sql in create_indexes_sql:
                    await conn.execute(index_sql)

                log.info("Menu tables and indexes created successfully")
        except Exception as e:
            log.error(f"Failed to create menu tables: {e}")
            raise

    async def create_menu(self, menu_data: MenuConfig, created_by: str) -> str:
        """创建新菜单"""
        insert_sql = """
        INSERT INTO auth_menus (
            id, name, title, title_en, path, component, icon, emoji,
            parent_id, permission, menu_type, sort_order, is_hidden,
            is_external, status, meta, created_by, updated_by
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8,
            $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
        )
        """

        try:
            async with self.dao.acquire() as conn:
                await conn.execute(
                    insert_sql,
                    menu_data.id, menu_data.name, menu_data.title, menu_data.title_en,
                    menu_data.path, menu_data.component, menu_data.icon, menu_data.emoji,
                    menu_data.parent_id, menu_data.permission, menu_data.menu_type.value,
                    menu_data.sort_order, menu_data.is_hidden, menu_data.is_external,
                    menu_data.status, json.dumps(menu_data.meta or {}),
                    created_by, created_by
                )

                log.info(f"Created menu: {menu_data.id} by user: {created_by}")
                return menu_data.id

        except Exception as e:
            log.error(f"Failed to create menu {menu_data.id}: {e}")
            raise

    async def get_menu_by_id(self, menu_id: str) -> Optional[MenuConfig]:
        """根据ID获取菜单"""
        query_sql = """
        SELECT id, name, title, title_en, path, component, icon, emoji,
               parent_id, permission, menu_type, sort_order, is_hidden,
               is_external, status, meta, created_at, updated_at
        FROM auth_menus
        WHERE id = $1
        """

        try:
            async with self.dao.acquire() as conn:
                row = await conn.fetchrow(query_sql, menu_id)

                if not row:
                    return None

                return self._row_to_menu_config(row)

        except Exception as e:
            log.error(f"Failed to get menu {menu_id}: {e}")
            raise

    async def get_all_menus(self, status: Optional[str] = None) -> List[MenuConfig]:
        """获取所有菜单"""
        query_sql = """
        SELECT id, name, title, title_en, path, component, icon, emoji,
               parent_id, permission, menu_type, sort_order, is_hidden,
               is_external, status, meta, created_at, updated_at
        FROM auth_menus
        """

        params = []
        if status:
            query_sql += " WHERE status = $1"
            params.append(status)

        query_sql += " ORDER BY sort_order ASC, created_at ASC"

        try:
            async with self.dao.acquire() as conn:
                rows = await conn.fetch(query_sql, *params)

                menus = []
                for row in rows:
                    menu = self._row_to_menu_config(row)
                    menus.append(menu)

                log.info(f"Retrieved {len(menus)} menus from database")
                return menus

        except Exception as e:
            log.error(f"Failed to get all menus: {e}")
            raise

    async def update_menu(self, menu_id: str, update_data: Dict[str, Any], updated_by: str) -> bool:
        """更新菜单"""
        # 构建动态更新SQL
        set_clauses = []
        params = []
        param_counter = 1

        for field, value in update_data.items():
            if field == 'meta' and isinstance(value, dict):
                set_clauses.append(f"{field} = ${param_counter}")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{field} = ${param_counter}")
                params.append(value)
            param_counter += 1

        set_clauses.append(f"updated_by = ${param_counter}")
        params.append(updated_by)
        param_counter += 1

        set_clauses.append(f"updated_at = ${param_counter}")
        params.append(datetime.now())
        param_counter += 1

        params.append(menu_id)

        update_sql = f"""
        UPDATE auth_menus
        SET {', '.join(set_clauses)}
        WHERE id = ${param_counter}
        """

        try:
            async with self.dao.acquire() as conn:
                result = await conn.execute(update_sql, *params)

                rows_affected = int(result.split()[-1]) if result else 0
                success = rows_affected > 0

                if success:
                    log.info(f"Updated menu: {menu_id} by user: {updated_by}")
                else:
                    log.warning(f"No rows affected when updating menu: {menu_id}")

                return success

        except Exception as e:
            log.error(f"Failed to update menu {menu_id}: {e}")
            raise

    async def delete_menu(self, menu_id: str, deleted_by: str) -> bool:
        """删除菜单（软删除）"""
        update_sql = """
        UPDATE auth_menus
        SET status = 'deleted', updated_by = $1, updated_at = $2
        WHERE id = $3 AND status != 'deleted'
        """

        try:
            async with self.dao.acquire() as conn:
                result = await conn.execute(update_sql, deleted_by, datetime.now(), menu_id)

                rows_affected = int(result.split()[-1]) if result else 0
                success = rows_affected > 0

                if success:
                    log.info(f"Deleted menu: {menu_id} by user: {deleted_by}")
                else:
                    log.warning(f"No rows affected when deleting menu: {menu_id}")

                return success

        except Exception as e:
            log.error(f"Failed to delete menu {menu_id}: {e}")
            raise

    async def batch_create_menus(self, menus: List[MenuConfig], created_by: str) -> int:
        """批量创建菜单"""
        insert_sql = """
        INSERT INTO auth_menus (
            id, name, title, title_en, path, component, icon, emoji,
            parent_id, permission, menu_type, sort_order, is_hidden,
            is_external, status, meta, created_by, updated_by
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8,
            $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
        )
        """

        created_count = 0
        try:
            async with self.dao.acquire() as conn:
                async with conn.transaction():
                    for menu in menus:
                        try:
                            await conn.execute(
                                insert_sql,
                                menu.id, menu.name, menu.title, menu.title_en,
                                menu.path, menu.component, menu.icon, menu.emoji,
                                menu.parent_id, menu.permission, menu.menu_type.value,
                                menu.sort_order, menu.is_hidden, menu.is_external,
                                menu.status, json.dumps(menu.meta or {}),
                                created_by, created_by
                            )
                            created_count += 1
                        except Exception as e:
                            log.warning(f"Failed to create menu {menu.id} in batch: {e}")
                            # 继续处理其他菜单

                log.info(f"Batch created {created_count}/{len(menus)} menus by user: {created_by}")
                return created_count

        except Exception as e:
            log.error(f"Failed to batch create menus: {e}")
            raise

    async def clear_all_menus(self, deleted_by: str) -> int:
        """清空所有菜单（软删除）"""
        update_sql = """
        UPDATE auth_menus
        SET status = 'deleted', updated_by = $1, updated_at = $2
        WHERE status != 'deleted'
        """

        try:
            async with self.dao.acquire() as conn:
                result = await conn.execute(update_sql, deleted_by, datetime.now())

                rows_affected = int(result.split()[-1]) if result else 0

                log.info(f"Cleared {rows_affected} menus by user: {deleted_by}")
                return rows_affected

        except Exception as e:
            log.error(f"Failed to clear all menus: {e}")
            raise

    def _row_to_menu_config(self, row) -> MenuConfig:
        """将数据库行转换为MenuConfig对象"""
        meta = {}
        if row['meta']:
            try:
                meta = json.loads(row['meta']) if isinstance(row['meta'], str) else row['meta']
            except (json.JSONDecodeError, TypeError):
                meta = {}

        return MenuConfig(
            id=row['id'],
            name=row['name'],
            title=row['title'],
            title_en=row['title_en'],
            path=row['path'],
            component=row['component'],
            icon=row['icon'],
            emoji=row['emoji'],
            parent_id=row['parent_id'],
            permission=row['permission'],
            menu_type=MenuType(row['menu_type']),
            sort_order=row['sort_order'],
            is_hidden=row['is_hidden'],
            is_external=row['is_external'],
            status=row['status'],
            meta=meta,
            children=None  # 子菜单需要单独查询构建
        )