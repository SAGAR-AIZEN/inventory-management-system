"""
Database Manager - Unified interface handling queries, transactions, and fallback.
Coordinates between MySQL (primary XAMPP target) and SQLite (resilient fallback).
"""
import os
import shutil
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from .mysql_backend import MySQLBackend
from .sqlite_backend import SQLiteBackend
from ..utils.config import load_config, save_config


class DatabaseManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.config = load_config()
        self.active_engine = "mysql"
        self.status_message = "Not initialized"
        self.mysql = None
        self.sqlite = None
        self.backend = None
        self.setup_backend()

    def setup_backend(self, force_engine: Optional[str] = None):
        """Configure and connect to the selected database backend."""
        self.config = load_config()
        target = force_engine or self.config.get("db_type", "mysql").lower()

        mysql_conf = self.config.get("mysql", {})
        self.mysql = MySQLBackend(
            host=mysql_conf.get("host", "localhost"),
            port=mysql_conf.get("port", 3306),
            user=mysql_conf.get("user", "root"),
            password=mysql_conf.get("password", ""),
            database=mysql_conf.get("database", "inventory_db")
        )

        sqlite_conf = self.config.get("sqlite", {})
        self.sqlite = SQLiteBackend(
            file_path=sqlite_conf.get("file_path", "data/inventory.db")
        )

        if target == "mysql":
            success, msg = self.mysql.initialize()
            if success:
                self.backend = self.mysql
                self.active_engine = "mysql"
                self.status_message = f"Connected to MySQL (XAMPP: {self.mysql.host}:{self.mysql.port}/{self.mysql.database})"
            else:
                # Automatic graceful fallback to SQLite
                print(f"[DatabaseManager] MySQL not reachable: {msg}. Falling back to SQLite.")
                sq_ok, sq_msg = self.sqlite.initialize()
                self.backend = self.sqlite
                self.active_engine = "sqlite"
                self.status_message = f"XAMPP Offline -> Switched to SQLite ({self.sqlite.file_path})"
        else:
            sq_ok, sq_msg = self.sqlite.initialize()
            self.backend = self.sqlite
            self.active_engine = "sqlite"
            self.status_message = f"Connected to SQLite ({self.sqlite.file_path})"

    def switch_engine(self, engine_name: str) -> Tuple[bool, str]:
        """Manually switch between 'mysql' and 'sqlite'."""
        engine_name = engine_name.lower()
        if engine_name not in ["mysql", "sqlite"]:
            return False, "Invalid engine name. Choose 'mysql' or 'sqlite'."

        self.setup_backend(force_engine=engine_name)
        if self.active_engine == engine_name:
            self.config["db_type"] = engine_name
            save_config(self.config)
            return True, self.status_message
        else:
            return False, f"Could not switch to {engine_name}. Current status: {self.status_message}"

    def get_status(self) -> Dict[str, Any]:
        """Return status information for display in the UI bar."""
        return {
            "engine": self.active_engine.upper(),
            "message": self.status_message,
            "is_mysql": self.active_engine == "mysql"
        }

    # =========================================================================
    # CATEGORIES & SUB-CATEGORIES (Directory Hierarchy)
    # =========================================================================
    def get_categories(self) -> List[Dict[str, Any]]:
        """Fetch all main categories."""
        return self.backend.fetch_all("SELECT * FROM categories ORDER BY name ASC;")

    def add_category(self, name: str, description: str = "") -> int:
        """Add a new main category directory."""
        return self.backend.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s);",
            (name.strip(), description.strip())
        )

    def delete_category(self, category_id: int) -> bool:
        """Delete a main category and cascade to subcategories."""
        self.backend.execute("DELETE FROM categories WHERE id = %s;", (category_id,))
        return True

    def get_subcategories(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch subcategories, optionally filtered by parent category ID."""
        if category_id:
            return self.backend.fetch_all(
                """
                SELECT s.*, c.name AS category_name 
                FROM sub_categories s 
                JOIN categories c ON s.category_id = c.id 
                WHERE s.category_id = %s 
                ORDER BY s.name ASC;
                """,
                (category_id,)
            )
        return self.backend.fetch_all(
            """
            SELECT s.*, c.name AS category_name 
            FROM sub_categories s 
            JOIN categories c ON s.category_id = c.id 
            ORDER BY c.name ASC, s.name ASC;
            """
        )

    def add_subcategory(self, category_id: int, name: str, description: str = "") -> int:
        """Add a new subcategory under a main category directory."""
        return self.backend.execute(
            "INSERT INTO sub_categories (category_id, name, description) VALUES (%s, %s, %s);",
            (category_id, name.strip(), description.strip())
        )

    def delete_subcategory(self, subcategory_id: int) -> bool:
        """Delete a subcategory."""
        self.backend.execute("DELETE FROM sub_categories WHERE id = %s;", (subcategory_id,))
        return True

    # =========================================================================
    # PRODUCT MANAGEMENT
    # =========================================================================
    def get_products(self, search: str = "", category_id: Optional[int] = None,
                     subcategory_id: Optional[int] = None, only_low_stock: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch products with joined category/subcategory names, search, and low-stock filter.
        """
        query = """
            SELECT p.id, p.sku, p.name, p.unit, p.cost_price, p.selling_price, 
                   p.current_stock, p.low_stock_threshold, p.created_at,
                   s.id AS subcategory_id, s.name AS subcategory_name,
                   c.id AS category_id, c.name AS category_name
            FROM products p
            JOIN sub_categories s ON p.subcategory_id = s.id
            JOIN categories c ON s.category_id = c.id
            WHERE 1=1
        """
        params = []

        if search:
            like_val = f"%{search.strip()}%"
            query += " AND (p.sku LIKE %s OR p.name LIKE %s OR c.name LIKE %s OR s.name LIKE %s)"
            params.extend([like_val, like_val, like_val, like_val])

        if subcategory_id:
            query += " AND s.id = %s"
            params.append(subcategory_id)
        elif category_id:
            query += " AND c.id = %s"
            params.append(category_id)

        if only_low_stock:
            query += " AND p.current_stock <= p.low_stock_threshold"

        query += " ORDER BY c.name ASC, s.name ASC, p.name ASC;"
        return self.backend.fetch_all(query, tuple(params))

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT p.*, s.name AS subcategory_name, c.id AS category_id, c.name AS category_name
            FROM products p
            JOIN sub_categories s ON p.subcategory_id = s.id
            JOIN categories c ON s.category_id = c.id
            WHERE p.id = %s;
        """
        return self.backend.fetch_one(query, (product_id,))

    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM products WHERE sku = %s;"
        return self.backend.fetch_one(query, (sku.strip(),))

    def add_product(self, sku: str, name: str, subcategory_id: int, unit: str,
                    cost_price: float, selling_price: float, current_stock: int,
                    low_stock_threshold: int) -> int:
        """Add a new product with unique SKU."""
        query = """
            INSERT INTO products 
            (sku, name, subcategory_id, unit, cost_price, selling_price, current_stock, low_stock_threshold)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        return self.backend.execute(
            query,
            (sku.strip(), name.strip(), subcategory_id, unit.strip(),
             float(cost_price), float(selling_price), int(current_stock), int(low_stock_threshold))
        )

    def update_product(self, product_id: int, sku: str, name: str, subcategory_id: int,
                       unit: str, cost_price: float, selling_price: float,
                       current_stock: int, low_stock_threshold: int) -> bool:
        """Update product details."""
        query = """
            UPDATE products 
            SET sku = %s, name = %s, subcategory_id = %s, unit = %s,
                cost_price = %s, selling_price = %s, current_stock = %s, low_stock_threshold = %s
            WHERE id = %s;
        """
        self.backend.execute(
            query,
            (sku.strip(), name.strip(), subcategory_id, unit.strip(),
             float(cost_price), float(selling_price), int(current_stock), int(low_stock_threshold),
             product_id)
        )
        return True

    def delete_product(self, product_id: int) -> bool:
        """Delete product by ID."""
        self.backend.execute("DELETE FROM products WHERE id = %s;", (product_id,))
        return True

    # =========================================================================
    # PURCHASES (STOCK INWARD)
    # =========================================================================
    def record_purchase(self, invoice_no: str, supplier_name: str, purchase_date: str,
                        items: List[Dict[str, Any]], notes: str = "") -> int:
        """
        Record a purchase transaction:
        - Insert into `purchases`
        - Insert each into `purchase_items`
        - Atomically INCREMENT `current_stock` for each product
        - Update `cost_price` to the latest purchase unit cost
        """
        total_amount = sum(item["quantity"] * item["unit_cost"] for item in items)
        
        # 1. Insert Purchase Header
        purchase_id = self.backend.execute(
            """
            INSERT INTO purchases (invoice_no, supplier_name, purchase_date, total_amount, notes)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (invoice_no.strip(), supplier_name.strip(), purchase_date, total_amount, notes.strip())
        )

        # 2. Insert Items and update product stock
        for it in items:
            p_id = it["product_id"]
            qty = int(it["quantity"])
            cost = float(it["unit_cost"])
            subtotal = qty * cost

            self.backend.execute(
                """
                INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost, subtotal)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (purchase_id, p_id, qty, cost, subtotal)
            )

            # Update product stock & cost price
            self.backend.execute(
                """
                UPDATE products 
                SET current_stock = current_stock + %s, cost_price = %s 
                WHERE id = %s;
                """,
                (qty, cost, p_id)
            )

        return purchase_id

    def get_purchases(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent purchases."""
        return self.backend.fetch_all(
            "SELECT * FROM purchases ORDER BY purchase_date DESC, id DESC LIMIT %s;",
            (limit,)
        )

    def get_purchase_items(self, purchase_id: int) -> List[Dict[str, Any]]:
        """Fetch items for a specific purchase."""
        query = """
            SELECT pi.*, p.name AS product_name, p.sku, p.unit
            FROM purchase_items pi
            JOIN products p ON pi.product_id = p.id
            WHERE pi.purchase_id = %s;
        """
        return self.backend.fetch_all(query, (purchase_id,))

    # =========================================================================
    # SALES (BILLING & STOCK OUTWARD)
    # =========================================================================
    def record_sale(self, invoice_no: str, customer_name: str, customer_phone: str,
                    sale_date: str, items: List[Dict[str, Any]], notes: str = "") -> int:
        """
        Record a sales transaction:
        - Check stock availability first (prevent out-of-stock sale)
        - Insert into `sales`
        - Insert each into `sales_items` with calculated profit
        - Atomically DECREMENT `current_stock` for each product
        """
        # Validate stock for all items first
        for it in items:
            prod = self.get_product_by_id(it["product_id"])
            if not prod:
                raise ValueError(f"Product ID {it['product_id']} not found.")
            if prod["current_stock"] < it["quantity"]:
                raise ValueError(
                    f"Insufficient stock for '{prod['name']}'. "
                    f"Available: {prod['current_stock']} {prod['unit']}, Requested: {it['quantity']}"
                )

        total_amount = 0.0
        total_profit = 0.0

        for it in items:
            qty = int(it["quantity"])
            sell_price = float(it["unit_price"])
            cost_price = float(it["unit_cost"])
            subtotal = qty * sell_price
            profit = (sell_price - cost_price) * qty
            total_amount += subtotal
            total_profit += profit

        # 1. Insert Sales Header
        sale_id = self.backend.execute(
            """
            INSERT INTO sales (invoice_no, customer_name, customer_phone, sale_date, total_amount, total_profit, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (invoice_no.strip(), customer_name.strip(), customer_phone.strip(), sale_date, total_amount, total_profit, notes.strip())
        )

        # 2. Insert items and decrement stock
        for it in items:
            p_id = it["product_id"]
            qty = int(it["quantity"])
            sell_price = float(it["unit_price"])
            cost_price = float(it["unit_cost"])
            subtotal = qty * sell_price
            profit = (sell_price - cost_price) * qty

            self.backend.execute(
                """
                INSERT INTO sales_items (sale_id, product_id, quantity, unit_price, unit_cost, profit, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (sale_id, p_id, qty, sell_price, cost_price, profit, subtotal)
            )

            # Decrement stock
            self.backend.execute(
                "UPDATE products SET current_stock = current_stock - %s WHERE id = %s;",
                (qty, p_id)
            )

        return sale_id

    def get_sales(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent sales invoices."""
        return self.backend.fetch_all(
            "SELECT * FROM sales ORDER BY sale_date DESC, id DESC LIMIT %s;",
            (limit,)
        )

    def get_sale_items(self, sale_id: int) -> List[Dict[str, Any]]:
        """Fetch items for a specific sale."""
        query = """
            SELECT si.*, p.name AS product_name, p.sku, p.unit
            FROM sales_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = %s;
        """
        return self.backend.fetch_all(query, (sale_id,))

    # =========================================================================
    # STOCK & LOW-STOCK DASHBOARD KPI
    # =========================================================================
    def get_stock_summary(self) -> Dict[str, Any]:
        """Calculate overall stock valuation and counts."""
        products = self.backend.fetch_all("SELECT cost_price, selling_price, current_stock, low_stock_threshold FROM products;")
        total_items = len(products)
        total_units = sum(p["current_stock"] for p in products)
        total_cost_val = sum(p["current_stock"] * p["cost_price"] for p in products)
        total_retail_val = sum(p["current_stock"] * p["selling_price"] for p in products)
        low_stock_count = sum(1 for p in products if p["current_stock"] <= p["low_stock_threshold"])

        return {
            "total_products": total_items,
            "total_units": total_units,
            "total_cost_value": total_cost_val,
            "total_retail_value": total_retail_val,
            "potential_profit": total_retail_val - total_cost_val,
            "low_stock_count": low_stock_count
        }

    # =========================================================================
    # PROFIT & PERFORMANCE REPORTS
    # =========================================================================
    def get_profit_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate total revenue, COGS, gross profit, margin %, and bestsellers.
        """
        query = "SELECT * FROM sales WHERE 1=1"
        params = []
        if start_date:
            query += " AND sale_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND sale_date <= %s"
            params.append(end_date)

        sales = self.backend.fetch_all(query, tuple(params))

        total_revenue = sum(float(s["total_amount"]) for s in sales)
        total_profit = sum(float(s["total_profit"]) for s in sales)
        total_cost = total_revenue - total_profit
        margin = (total_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

        # Top selling products in this period
        item_query = """
            SELECT p.name, SUM(si.quantity) AS qty, SUM(si.profit) AS profit
            FROM sales_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE 1=1
        """
        item_params = []
        if start_date:
            item_query += " AND s.sale_date >= %s"
            item_params.append(start_date)
        if end_date:
            item_query += " AND s.sale_date <= %s"
            item_params.append(end_date)

        item_query += " GROUP BY p.id, p.name ORDER BY qty DESC LIMIT 5;"
        top_products = self.backend.fetch_all(item_query, tuple(item_params))

        total_items_sold = sum(p["qty"] for p in top_products) if top_products else 0

        return {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "margin_percentage": margin,
            "total_transactions": len(sales),
            "total_items_sold": total_items_sold,
            "top_products": top_products
        }

    # =========================================================================
    # BACKUP UTILITY
    # =========================================================================
    def backup_database(self, dest_dir: str) -> Tuple[bool, str]:
        """Create a backup of the current database."""
        try:
            os.makedirs(dest_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if self.active_engine == "sqlite":
                source = self.sqlite.file_path
                dest = os.path.join(dest_dir, f"inventory_backup_{timestamp}.db")
                shutil.copy2(source, dest)
                return True, f"SQLite backup saved: {dest}"
            else:
                # Export metadata / CSV summary as MySQL backup bundle
                summary = self.get_stock_summary()
                dest = os.path.join(dest_dir, f"mysql_inventory_snapshot_{timestamp}.txt")
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(f"MySQL Inventory Snapshot: {datetime.now()}\n")
                    f.write(f"Database: {self.mysql.database}\n")
                    f.write(f"Total Products: {summary['total_products']}\n")
                    f.write(f"Total Stock Value: {summary['total_retail_value']}\n")
                return True, f"MySQL snapshot summary saved: {dest}"
        except Exception as e:
            return False, f"Backup error: {str(e)}"
