"""
SQLite Database Backend for local fallback or offline execution.
Uses built-in Python sqlite3 module.
Adapts '%s' parameter placeholders to '?' automatically for seamless cross-engine compatibility.
"""
import sqlite3
import os
from typing import Tuple, List, Dict, Any, Optional
from .schema import SQLITE_TABLES, SEED_CATEGORIES, SEED_SUBCATEGORIES, SEED_PRODUCTS


class SQLiteBackend:
    def __init__(self, file_path: str = "data/inventory.db"):
        self.file_path = file_path
        self.conn = None

    def is_available(self) -> bool:
        return True

    def test_connection(self) -> Tuple[bool, str]:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            conn = sqlite3.connect(self.file_path, timeout=3)
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            conn.close()
            return True, f"SQLite connected successfully to {self.file_path}"
        except Exception as e:
            return False, f"SQLite Connection Failed: {str(e)}"

    def initialize(self) -> Tuple[bool, str]:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            self.conn = sqlite3.connect(self.file_path, timeout=5, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

            # Enable foreign keys and WAL mode for high performance
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA journal_mode = WAL;")

            # Create tables
            for ddl in SQLITE_TABLES:
                cursor.execute(ddl)

            self.conn.commit()
            cursor.close()

            # Seed initial data
            self._seed_initial_data()

            return True, f"SQLite database initialized at {self.file_path}"
        except Exception as e:
            return False, f"SQLite Initialization Error: {str(e)}"

    def get_connection(self):
        if self.conn is None:
            self.initialize()
        return self.conn

    def _convert_query(self, query: str) -> str:
        """Convert MySQL %s placeholder to SQLite ? placeholder."""
        return query.replace("%s", "?")

    def execute(self, query: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        converted_q = self._convert_query(query)
        cursor = conn.cursor()
        try:
            cursor.execute(converted_q, params)
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        converted_q = self._convert_query(query)
        cursor = conn.cursor()
        try:
            cursor.execute(converted_q, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            cursor.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        converted_q = self._convert_query(query)
        cursor = conn.cursor()
        try:
            cursor.execute(converted_q, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()

    def _seed_initial_data(self):
        try:
            existing = self.fetch_all("SELECT COUNT(*) AS cnt FROM categories;")
            if existing and existing[0]["cnt"] > 0:
                return

            cat_map = {}
            for name, desc in SEED_CATEGORIES:
                cid = self.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, desc))
                cat_map[name] = cid

            subcat_map = {}
            for cat_name, sub_name, desc in SEED_SUBCATEGORIES:
                cid = cat_map.get(cat_name)
                if cid:
                    sid = self.execute(
                        "INSERT INTO sub_categories (category_id, name, description) VALUES (?, ?, ?)",
                        (cid, sub_name, desc)
                    )
                    subcat_map[f"{cat_name}::{sub_name}"] = sid

            for sku, name, cat_name, sub_name, unit, cost, sell, stock, limit in SEED_PRODUCTS:
                sid = subcat_map.get(f"{cat_name}::{sub_name}")
                if sid:
                    self.execute(
                        """
                        INSERT INTO products (sku, name, subcategory_id, unit, cost_price, selling_price, current_stock, low_stock_threshold)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (sku, name, sid, unit, cost, sell, stock, limit)
                    )
        except Exception as e:
            print(f"Seed note (sqlite): {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
