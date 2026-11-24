"""
MySQL Database Backend for XAMPP / MariaDB.
Uses mysql.connector to connect to localhost:3306.
Automatically provisions the database and tables if not already present.
"""
from typing import Tuple, List, Dict, Any, Optional
from .schema import MYSQL_TABLES, SEED_CATEGORIES, SEED_SUBCATEGORIES, SEED_PRODUCTS

try:
    import mysql.connector
    from mysql.connector import errorcode
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False


class MySQLBackend:
    def __init__(self, host: str = "localhost", port: int = 3306,
                 user: str = "root", password: str = "", database: str = "inventory_db"):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database = database
        self.conn = None

    def is_available(self) -> bool:
        return HAS_MYSQL

    def test_connection(self) -> Tuple[bool, str]:
        """Test if the MySQL server in XAMPP is reachable."""
        if not HAS_MYSQL:
            return False, "mysql-connector-python is not installed."
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                connection_timeout=3
            )
            server_info = conn.get_server_info()
            conn.close()
            return True, f"Connected to MySQL/MariaDB server ({server_info}) on {self.host}:{self.port}"
        except mysql.connector.Error as err:
            return False, f"MySQL Error [{err.errno}]: {err.msg}"
        except Exception as e:
            return False, f"Connection Failed: {str(e)}"

    def initialize(self) -> Tuple[bool, str]:
        """
        Connect to MySQL, create the database if not exists, and create all required tables.
        """
        if not HAS_MYSQL:
            return False, "mysql-connector-python module missing."

        try:
            # 1. Connect without database to ensure database exists
            server_conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                connection_timeout=4
            )
            cursor = server_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.close()
            server_conn.close()

            # 2. Connect to the specific database
            self.conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            cursor = self.conn.cursor()

            # 3. Create tables
            for ddl in MYSQL_TABLES:
                cursor.execute(ddl)

            self.conn.commit()
            cursor.close()

            # 4. Populate initial seeds if categories are empty
            self._seed_initial_data()

            return True, f"MySQL database '{self.database}' initialized successfully."
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                return False, "Access Denied: Incorrect MySQL username or password."
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                return False, f"Database '{self.database}' does not exist and cannot be created."
            else:
                return False, f"MySQL Error ({err.errno}): {err.msg}"
        except Exception as e:
            return False, f"Database Initialization Error: {str(e)}"

    def get_connection(self):
        """Get or recreate connection if closed."""
        try:
            if self.conn is None or not self.conn.is_connected():
                self.conn = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=False
                )
        except Exception:
            pass
        return self.conn

    def execute(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT, UPDATE, DELETE query and return lastrowid or affected rows."""
        conn = self.get_connection()
        if not conn:
            raise ConnectionError("Not connected to MySQL.")
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return rows as list of dicts."""
        conn = self.get_connection()
        if not conn:
            raise ConnectionError("Not connected to MySQL.")
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return a single row as dict."""
        conn = self.get_connection()
        if not conn:
            raise ConnectionError("Not connected to MySQL.")
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row
        finally:
            cursor.close()

    def _seed_initial_data(self):
        """Insert seed categories, subcategories, and products if database is empty."""
        try:
            existing = self.fetch_all("SELECT COUNT(*) AS cnt FROM categories;")
            if existing and existing[0]["cnt"] > 0:
                return  # Already seeded

            cat_map = {}
            for name, desc in SEED_CATEGORIES:
                cid = self.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (name, desc))
                cat_map[name] = cid

            subcat_map = {}
            for cat_name, sub_name, desc in SEED_SUBCATEGORIES:
                cid = cat_map.get(cat_name)
                if cid:
                    sid = self.execute("INSERT INTO sub_categories (category_id, name, description) VALUES (%s, %s, %s)",
                                       (cid, sub_name, desc))
                    subcat_map[f"{cat_name}::{sub_name}"] = sid

            for sku, name, cat_name, sub_name, unit, cost, sell, stock, limit in SEED_PRODUCTS:
                sid = subcat_map.get(f"{cat_name}::{sub_name}")
                if sid:
                    self.execute(
                        """
                        INSERT INTO products (sku, name, subcategory_id, unit, cost_price, selling_price, current_stock, low_stock_threshold)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (sku, name, sid, unit, cost, sell, stock, limit)
                    )
        except Exception as e:
            print(f"Seed note: {e}")

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            self.conn = None
