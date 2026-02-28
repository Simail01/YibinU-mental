import logging
import traceback
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

from config import settings

logger = logging.getLogger(__name__)


class DBManager:
    def __init__(self):
        self._pool: Optional[PooledDB] = None
        self._initialized = False
        self._available = False

    def _init_pool(self) -> None:
        if self._initialized and self._pool:
            return
            
        try:
            db_config = settings.db
            self._pool = PooledDB(
                creator=pymysql,
                maxconnections=db_config.max_connections,
                mincached=db_config.min_cached,
                maxcached=db_config.max_cached,
                maxshared=3,
                blocking=True,
                setsession=[],
                ping=1,
                **db_config.config_dict
            )
            self._initialized = True
            self._available = True
            logger.info("数据库连接池初始化成功")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            self._available = False
            self._initialized = True

    def get_connection(self):
        if not self._initialized:
            self._init_pool()
        if not self._available:
            raise ConnectionError("数据库不可用，请检查数据库配置和连接")
        try:
            return self._pool.connection()
        except Exception as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise

    @contextmanager
    def get_cursor(self, cursor_class=DictCursor):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_class)
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}\n{traceback.format_exc()}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def execute_query(
        self, 
        sql: str, 
        params: Optional[tuple] = None,
        fetch_all: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        if not self._available:
            logger.warning("数据库不可用，无法执行查询")
            return None
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            if fetch_all:
                return cursor.fetchall()
            return cursor.fetchone()

    def execute_update(
        self, 
        sql: str, 
        params: Optional[tuple] = None
    ) -> Optional[int]:
        if not self._available:
            logger.warning("数据库不可用，无法执行更新")
            return None
        with self.get_cursor(cursor_class=pymysql.cursors.Cursor) as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_batch(
        self, 
        sql: str, 
        params_list: List[tuple]
    ) -> int:
        if not self._available:
            logger.warning("数据库不可用，无法执行批量操作")
            return 0
        with self.get_cursor(cursor_class=pymysql.cursors.Cursor) as cursor:
            cursor.executemany(sql, params_list)
            return cursor.rowcount

    def init_db(self) -> None:
        if not self._available:
            logger.warning("数据库不可用，跳过表结构初始化")
            return
            
        tables = [
            """
            CREATE TABLE IF NOT EXISTS scl90_record (
                id INT AUTO_INCREMENT PRIMARY KEY,
                uuid VARCHAR(64) NOT NULL,
                scores JSON NOT NULL COMMENT '各因子得分',
                total_score FLOAT NOT NULL,
                average_score FLOAT DEFAULT 0,
                positive_items_count INT DEFAULT 0,
                abnormal_items JSON COMMENT '异常项',
                answers JSON COMMENT '原始答案',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_uuid (uuid),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS text_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                uuid VARCHAR(64) NOT NULL,
                content TEXT,
                emotion_result JSON,
                scl90_ref_id INT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_uuid (uuid),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS dialogue (
                id INT AUTO_INCREMENT PRIMARY KEY,
                uuid VARCHAR(64) NOT NULL,
                session_id VARCHAR(64) NOT NULL,
                user_query TEXT,
                system_reply TEXT,
                emotion VARCHAR(32),
                risk_level VARCHAR(32),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_uuid (uuid),
                INDEX idx_session_id (session_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS dialogue_session (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(64) NOT NULL UNIQUE,
                uuid VARCHAR(64) NOT NULL,
                title VARCHAR(255),
                message_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_uuid (uuid),
                INDEX idx_session_id (session_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type ENUM('public', 'private') DEFAULT 'private',
                uuid VARCHAR(64),
                title VARCHAR(255),
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_uuid (uuid),
                INDEX idx_type (type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ]
        
        for sql in tables:
            try:
                self.execute_update(sql)
            except Exception as e:
                logger.error(f"创建表失败: {e}")
                raise
        
        logger.info("数据库表结构初始化完成")

    def health_check(self) -> bool:
        if not self._available:
            return False
        try:
            result = self.execute_query("SELECT 1 as test")
            return result is not None
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

    def close(self) -> None:
        if self._pool:
            self._pool = None
            self._initialized = False
            self._available = False
            logger.info("数据库连接池已关闭")


db_manager = DBManager()
