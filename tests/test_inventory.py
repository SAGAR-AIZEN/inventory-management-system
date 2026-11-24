import unittest
import os
import shutil
import tempfile
from datetime import datetime

from src.database.sqlite_backend import SQLiteBackend
from src.database.db_manager import DatabaseManager
from src.utils.export_helper import generate_sales_receipt, generate_profit_report_text, export_to_csv


class TestInventoryDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_inventory.db")
        self.backend = SQLiteBackend(file_path=self.test_db_path)
        self.backend.initialize()

    def tearDown(self):
        self.backend.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_schema_and_seed_data(self):
        """Verify tables are created and initial seed categories/products exist."""
        categories = self.backend.fetch_all("SELECT * FROM categories;")
        self.assertGreater(len(categories), 0, "Initial seed categories should be populated.")

        subcategories = self.backend.fetch_all("SELECT * FROM sub_categories;")
        self.assertGreater(len(subcategories), 0, "Initial seed subcategories should be populated.")

        products = self.backend.fetch_all("SELECT * FROM products;")
        self.assertGreater(len(products), 0, "Initial seed products should be populated.")

    def test_category_and_subcategory_hierarchy(self):
        """Test adding Main Directory (Category) and Sub Directory."""
        cat_id = self.backend.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?);",
            ("Laboratory Supplies", "Physics, Chemistry and Biology Lab equipment")
        )
        self.assertIsNotNone(cat_id)

        sub_id = self.backend.execute(
            "INSERT INTO sub_categories (category_id, name, description) VALUES (?, ?, ?);",
            (cat_id, "Glassware", "Beakers, test tubes, flasks")
        )
        self.assertIsNotNone(sub_id)

        res = self.backend.fetch_all(
            """
            SELECT s.name AS sub_name, c.name AS cat_name 
            FROM sub_categories s 
            JOIN categories c ON s.category_id = c.id 
            WHERE s.id = ?;
            """,
            (sub_id,)
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["sub_name"], "Glassware")
        self.assertEqual(res[0]["cat_name"], "Laboratory Supplies")

    def test_product_crud_and_low_stock(self):
        """Test adding, querying, updating, and detecting low stock for a product."""
        sub = self.backend.fetch_one("SELECT id FROM sub_categories LIMIT 1;")
        self.assertIsNotNone(sub)
        sub_id = sub["id"]

        sku = "TEST-SKU-999"
        prod_id = self.backend.execute(
            """
            INSERT INTO products (sku, name, subcategory_id, unit, cost_price, selling_price, current_stock, low_stock_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (sku, "Test Low-Stock Microscope", sub_id, "Pcs", 2500.0, 3999.0, 3, 5)
        )
        self.assertIsNotNone(prod_id)

        prod = self.backend.fetch_one("SELECT * FROM products WHERE id = ?;", (prod_id,))
        self.assertEqual(prod["sku"], sku)
        self.assertEqual(prod["current_stock"], 3)
        self.assertEqual(prod["low_stock_threshold"], 5)
        self.assertTrue(prod["current_stock"] <= prod["low_stock_threshold"])

        self.backend.execute("UPDATE products SET current_stock = 15 WHERE id = ?;", (prod_id,))
        updated_prod = self.backend.fetch_one("SELECT * FROM products WHERE id = ?;", (prod_id,))
        self.assertEqual(updated_prod["current_stock"], 15)
        self.assertFalse(updated_prod["current_stock"] <= updated_prod["low_stock_threshold"])

    def test_purchase_stock_increment(self):
        """Test recording an inward purchase increases stock."""
        prod = self.backend.fetch_one("SELECT id, current_stock FROM products LIMIT 1;")
        initial_stock = prod["current_stock"]
        p_id = prod["id"]

        qty_purchased = 20
        unit_cost = 55.0
        tot = qty_purchased * unit_cost

        pur_id = self.backend.execute(
            "INSERT INTO purchases (invoice_no, supplier_name, purchase_date, total_amount) VALUES (?, ?, ?, ?);",
            ("PUR-TEST-001", "Apex School Supplies", "2026-11-24", tot)
        )
        self.backend.execute(
            "INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost, subtotal) VALUES (?, ?, ?, ?, ?);",
            (pur_id, p_id, qty_purchased, unit_cost, tot)
        )
        self.backend.execute(
            "UPDATE products SET current_stock = current_stock + ?, cost_price = ? WHERE id = ?;",
            (qty_purchased, unit_cost, p_id)
        )

        updated_prod = self.backend.fetch_one("SELECT current_stock, cost_price FROM products WHERE id = ?;", (p_id,))
        self.assertEqual(updated_prod["current_stock"], initial_stock + qty_purchased)
        self.assertEqual(updated_prod["cost_price"], unit_cost)

    def test_sales_and_profit_calculation(self):
        """Test sales entry reduces stock and accurately computes profit."""
        prod = self.backend.fetch_one("SELECT id, name, cost_price, selling_price, current_stock FROM products WHERE current_stock >= 5 LIMIT 1;")
        if not prod:
            self.backend.execute("UPDATE products SET current_stock = 20 WHERE id = 1;")
            prod = self.backend.fetch_one("SELECT id, name, cost_price, selling_price, current_stock FROM products WHERE id = 1;")

        p_id = prod["id"]
        initial_stock = prod["current_stock"]
        cost = prod["cost_price"]
        sell = prod["selling_price"]
        qty = 3
        subtotal = qty * sell
        profit = (sell - cost) * qty

        sale_id = self.backend.execute(
            "INSERT INTO sales (invoice_no, customer_name, sale_date, total_amount, total_profit) VALUES (?, ?, ?, ?, ?);",
            ("INV-TEST-001", "Rohan Sharma", "2026-11-24", subtotal, profit)
        )

        self.backend.execute(
            "INSERT INTO sales_items (sale_id, product_id, quantity, unit_price, unit_cost, profit, subtotal) VALUES (?, ?, ?, ?, ?, ?, ?);",
            (sale_id, p_id, qty, sell, cost, profit, subtotal)
        )

        self.backend.execute(
            "UPDATE products SET current_stock = current_stock - ? WHERE id = ?;",
            (qty, p_id)
        )

        updated = self.backend.fetch_one("SELECT current_stock FROM products WHERE id = ?;", (p_id,))
        self.assertEqual(updated["current_stock"], initial_stock - qty)

        sale_rec = self.backend.fetch_one("SELECT * FROM sales WHERE id = ?;", (sale_id,))
        self.assertAlmostEqual(sale_rec["total_amount"], subtotal)
        self.assertAlmostEqual(sale_rec["total_profit"], profit)


class TestDatabaseManagerHighLevel(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager.get_instance()
        # Force SQLite for test environment
        self.db.switch_engine("sqlite")

    def test_high_level_purchase_and_sale_flow(self):
        """Test the end-to-end business logic in DatabaseManager."""
        # Get a product
        products = self.db.get_products()
        self.assertGreater(len(products), 0)
        p = products[0]
        p_id = p["id"]
        start_stock = p["current_stock"]

        # Record purchase
        pur_inv = f"TEST-PUR-{datetime.now().strftime('%f')}"
        pur_items = [{"product_id": p_id, "quantity": 10, "unit_cost": 50.0}]
        self.db.record_purchase(pur_inv, "Test Supplier", "2026-11-24", pur_items)

        # Check stock incremented
        p_after_pur = self.db.get_product_by_id(p_id)
        self.assertEqual(p_after_pur["current_stock"], start_stock + 10)

        # Record sale
        sale_inv = f"TEST-SALE-{datetime.now().strftime('%f')}"
        sale_items = [{
            "product_id": p_id,
            "quantity": 4,
            "unit_price": 90.0,
            "unit_cost": 50.0
        }]
        self.db.record_sale(sale_inv, "Test Customer", "9999999999", "2026-11-24", sale_items)

        # Check stock decremented
        p_after_sale = self.db.get_product_by_id(p_id)
        self.assertEqual(p_after_sale["current_stock"], start_stock + 10 - 4)

        # Verify profit report captures this sale
        report = self.db.get_profit_report("2026-11-24", "2026-11-24")
        self.assertGreater(report["total_revenue"], 0)
        self.assertGreater(report["total_profit"], 0)

    def test_sale_validation_prevents_oversell(self):
        """Test that record_sale raises ValueError when stock is insufficient."""
        products = self.db.get_products()
        p = products[0]
        p_id = p["id"]
        stock = p["current_stock"]

        excessive_qty = stock + 1000
        sale_items = [{
            "product_id": p_id,
            "quantity": excessive_qty,
            "unit_price": 100.0,
            "unit_cost": 50.0
        }]

        with self.assertRaises(ValueError):
            self.db.record_sale("INV-OVERSELL", "Oversell Customer", "", "2026-11-24", sale_items)


class TestExportHelpers(unittest.TestCase):
    def test_receipt_generation(self):
        items = [
            ("A4 Notebook 200 Pgs", 2, 95.0, 190.0),
            ("Gel Pen Blue", 1, 120.0, 120.0)
        ]
        receipt = generate_sales_receipt("INV-001", "Aarav Patel", "9876543210", items, 310.0, "₹")
        self.assertIn("INVENTORY SALES INVOICE", receipt)
        self.assertIn("INV-001", receipt)
        self.assertIn("A4 Notebook", receipt)
        self.assertIn("₹310.00", receipt)

    def test_profit_report_generation(self):
        rep_data = {
            "total_revenue": 5000.0,
            "total_cost": 3200.0,
            "total_profit": 1800.0,
            "margin_percentage": 36.0,
            "total_transactions": 10,
            "total_items_sold": 45,
            "top_products": [{"name": "A4 Notebook", "qty": 20, "profit": 700.0}]
        }
        text_rep = generate_profit_report_text(rep_data, "2026-11-01", "2026-11-24", "₹")
        self.assertIn("INVENTORY PROFIT & LOSS PERFORMANCE REPORT", text_rep)
        self.assertIn("₹5000.00", text_rep)
        self.assertIn("36.00%", text_rep)

    def test_csv_export(self):
        temp_dir = tempfile.mkdtemp()
        try:
            csv_path = os.path.join(temp_dir, "test_export.csv")
            headers = ["SKU", "Name", "Stock"]
            rows = [["SKU-1", "Prod A", 10], ["SKU-2", "Prod B", 5]]
            ok = export_to_csv(csv_path, headers, rows)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(csv_path))
            with open(csv_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("SKU,Name,Stock", content)
                self.assertIn("Prod A", content)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
