import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..database.db_manager import DatabaseManager
from ..utils.theme import COLORS, FONTS
from ..utils.export_helper import generate_sales_receipt


class SalesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        # Cart items: list of dicts: {product_id, sku, name, unit, unit_price, unit_cost, quantity, subtotal, profit}
        self.cart_items = []

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header, text="Sales & Billing (Stock Outward)", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="⟳ Refresh", style="Secondary.TButton", command=self.refresh).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: POS Billing / New Sale
        tab_pos = ttk.Frame(notebook, style="Main.TFrame", padding=10)
        notebook.add(tab_pos, text="🛒 POS Billing & Checkout")
        self._build_pos_tab(tab_pos)

        # Tab 2: Sales History & Invoices
        tab_history = ttk.Frame(notebook, style="Main.TFrame", padding=10)
        notebook.add(tab_history, text="📜 Sales Ledger & Invoices")
        self._build_history_tab(tab_history)

    def _build_pos_tab(self, parent):
        # Customer Header Card
        cust_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        cust_card.pack(fill="x", pady=(0, 10))

        ttk.Label(cust_card, text="Customer & Invoice Information", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ttk.Label(cust_card, text="Invoice No:", font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.inv_var = tk.StringVar(value=f"INV-{datetime.now().strftime('%Y%m%d-%H%M')}")
        ttk.Entry(cust_card, textvariable=self.inv_var, width=22).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(cust_card, text="Date (YYYY-MM-DD):", font=FONTS["body_bold"]).grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(cust_card, textvariable=self.date_var, width=16).grid(row=1, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(cust_card, text="Customer Name:", font=FONTS["body_bold"]).grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.cust_name_var = tk.StringVar(value="Walk-in Customer")
        ttk.Entry(cust_card, textvariable=self.cust_name_var, width=28).grid(row=2, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(cust_card, text="Customer Phone:", font=FONTS["body"]).grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.cust_phone_var = tk.StringVar()
        ttk.Entry(cust_card, textvariable=self.cust_phone_var, width=20).grid(row=2, column=3, sticky="w", padx=5, pady=4)

        # Cart Item Entry Card
        item_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        item_card.pack(fill="x", pady=(0, 10))

        ttk.Label(item_card, text="Scan / Add Product to Cart", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        ttk.Label(item_card, text="Select Product:", font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", padx=4)
        self.prod_combo = ttk.Combobox(item_card, width=32, state="readonly")
        self.prod_combo.grid(row=1, column=1, padx=4)
        self.prod_combo.bind("<<ComboboxSelected>>", self._on_product_selected)

        ttk.Label(item_card, text="Available:", font=FONTS["body"]).grid(row=1, column=2, sticky="w", padx=4)
        self.lbl_avail_stock = ttk.Label(item_card, text="0 Pcs", font=FONTS["body_bold"],
                                         background=COLORS["bg_card"], foreground=COLORS["primary"])
        self.lbl_avail_stock.grid(row=1, column=3, sticky="w", padx=4)

        ttk.Label(item_card, text="Selling Price:", font=FONTS["body_bold"]).grid(row=1, column=4, sticky="w", padx=4)
        self.price_var = tk.StringVar()
        ttk.Entry(item_card, textvariable=self.price_var, width=10).grid(row=1, column=5, padx=4)

        ttk.Label(item_card, text="Qty:", font=FONTS["body_bold"]).grid(row=1, column=6, sticky="w", padx=4)
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(item_card, textvariable=self.qty_var, width=6).grid(row=1, column=7, padx=4)

        ttk.Button(item_card, text="+ Add to Cart", style="Primary.TButton",
                   command=self._add_to_cart).grid(row=1, column=8, padx=10)

        # Cart Table
        cart_frame = ttk.Frame(parent, style="Card.TFrame", padding=12)
        cart_frame.pack(fill="both", expand=True)

        cols = ("sku", "name", "unit", "price", "qty", "subtotal", "profit")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cols, show="headings", height=6, style="Treeview")
        self.cart_tree.heading("sku", text="SKU")
        self.cart_tree.heading("name", text="Product Name")
        self.cart_tree.heading("unit", text="Unit")
        self.cart_tree.heading("price", text="Unit Price")
        self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.heading("subtotal", text="Subtotal")
        self.cart_tree.heading("profit", text="Profit Margin")

        self.cart_tree.column("sku", width=95, anchor="center")
        self.cart_tree.column("name", width=220, anchor="w")
        self.cart_tree.column("unit", width=60, anchor="center")
        self.cart_tree.column("price", width=95, anchor="e")
        self.cart_tree.column("qty", width=80, anchor="center")
        self.cart_tree.column("subtotal", width=110, anchor="e")
        self.cart_tree.column("profit", width=110, anchor="e")

        self.cart_tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Checkout Bottom Bar
        bot_bar = ttk.Frame(parent, style="Main.TFrame")
        bot_bar.pack(fill="x", pady=10)

        ttk.Button(bot_bar, text="Remove Selected", style="Danger.TButton",
                   command=self._remove_cart_item).pack(side="left")

        self.lbl_grand_total = ttk.Label(bot_bar, text=f"Total: {self.currency}0.00", font=FONTS["title"],
                                         style="MainBg.TLabel", foreground=COLORS["success"])
        self.lbl_grand_total.pack(side="left", padx=20)

        self.lbl_total_profit = ttk.Label(bot_bar, text=f"Est. Profit: {self.currency}0.00", font=FONTS["body_bold"],
                                          style="MainBg.TLabel", foreground=COLORS["primary"])
        self.lbl_total_profit.pack(side="left", padx=10)

        ttk.Button(bot_bar, text="💳 Complete Sale & Generate Bill", style="Success.TButton",
                   command=self._checkout_sale).pack(side="right")

    def _build_history_tab(self, parent):
        top_bar = ttk.Frame(parent, style="Main.TFrame")
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(top_bar, text="Sales History & Invoices Ledger", font=FONTS["subtitle"],
                  style="MainBg.TLabel").pack(side="left")

        ttk.Button(top_bar, text="View Receipt / Invoice", style="Primary.TButton",
                   command=self._view_sale_receipt).pack(side="right")

        cols = ("id", "inv", "customer", "phone", "date", "amount", "profit")
        self.sales_tree = ttk.Treeview(parent, columns=cols, show="headings", style="Treeview")
        self.sales_tree.heading("id", text="ID")
        self.sales_tree.heading("inv", text="Invoice No")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("phone", text="Phone")
        self.sales_tree.heading("date", text="Sale Date")
        self.sales_tree.heading("amount", text="Total Bill")
        self.sales_tree.heading("profit", text="Net Profit")

        self.sales_tree.column("id", width=40, anchor="center")
        self.sales_tree.column("inv", width=130, anchor="center")
        self.sales_tree.column("customer", width=170, anchor="w")
        self.sales_tree.column("phone", width=110, anchor="center")
        self.sales_tree.column("date", width=100, anchor="center")
        self.sales_tree.column("amount", width=120, anchor="e")
        self.sales_tree.column("profit", width=120, anchor="e")

        self.sales_tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(parent, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def refresh(self):
        self.currency = self.controller.config.get("currency_symbol", "₹")
        products = self.db.get_products()
        self.prod_map = {f"{p['sku']} - {p['name']} (Stock: {p['current_stock']})": p for p in products}
        self.prod_combo["values"] = list(self.prod_map.keys())
        if self.prod_map:
            self.prod_combo.current(0)
            self._on_product_selected(None)

        self._load_sales_history()

    def _on_product_selected(self, event):
        val = self.prod_combo.get()
        p = self.prod_map.get(val)
        if p:
            self.lbl_avail_stock.config(text=f"{p['current_stock']} {p['unit']}")
            self.price_var.set(str(p["selling_price"]))

    def _add_to_cart(self):
        val = self.prod_combo.get()
        p = self.prod_map.get(val)
        if not p:
            messagebox.showwarning("Warning", "Please select a product.")
            return

        try:
            price = float(self.price_var.get().strip())
            qty = int(self.qty_var.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a number and Quantity must be an integer.")
            return

        if price <= 0 or qty <= 0:
            messagebox.showerror("Validation Error", "Price and Quantity must be greater than zero.")
            return

        # Check total requested quantity including items already in cart
        already_in_cart = sum(it["quantity"] for it in self.cart_items if it["product_id"] == p["id"])
        total_requested = already_in_cart + qty

        if total_requested > p["current_stock"]:
            messagebox.showerror(
                "Stock Shortage Error",
                f"Insufficient stock for '{p['name']}'.\n"
                f"Available in Stock: {p['current_stock']} {p['unit']}\n"
                f"Already in Cart: {already_in_cart} {p['unit']}\n"
                f"Attempting to add: {qty} {p['unit']}"
            )
            return

        subtotal = price * qty
        cost = p["cost_price"]
        profit = (price - cost) * qty

        self.cart_items.append({
            "product_id": p["id"],
            "sku": p["sku"],
            "name": p["name"],
            "unit": p["unit"],
            "unit_price": price,
            "unit_cost": cost,
            "quantity": qty,
            "subtotal": subtotal,
            "profit": profit
        })

        self._refresh_cart_table()

    def _remove_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.cart_items[idx]
        self._refresh_cart_table()

    def _refresh_cart_table(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total_bill = 0.0
        total_prof = 0.0

        for i, it in enumerate(self.cart_items):
            total_bill += it["subtotal"]
            total_prof += it["profit"]
            self.cart_tree.insert(
                "", "end", iid=str(i),
                values=(it["sku"], it["name"], it["unit"],
                        f"{self.currency}{it['unit_price']:.2f}",
                        it["quantity"],
                        f"{self.currency}{it['subtotal']:.2f}",
                        f"{self.currency}{it['profit']:.2f}")
            )

        self.lbl_grand_total.config(text=f"Total: {self.currency}{total_bill:.2f}")
        self.lbl_total_profit.config(text=f"Est. Profit: {self.currency}{total_prof:.2f}")

    def _checkout_sale(self):
        if not self.cart_items:
            messagebox.showwarning("Cart Empty", "Please add items to cart before checkout.")
            return

        inv_no = self.inv_var.get().strip()
        cust_name = self.cust_name_var.get().strip() or "Walk-in Customer"
        cust_phone = self.cust_phone_var.get().strip()
        sdate = self.date_var.get().strip()

        if not inv_no:
            messagebox.showerror("Validation Error", "Invoice Number is required.")
            return

        try:
            sid = self.db.record_sale(inv_no, cust_name, cust_phone, sdate, self.cart_items)

            # Generate Receipt text
            receipt_items = [
                (it["name"], it["quantity"], it["unit_price"], it["subtotal"])
                for it in self.cart_items
            ]
            total_amt = sum(it["subtotal"] for it in self.cart_items)
            receipt_text = generate_sales_receipt(
                inv_no, cust_name, cust_phone, receipt_items, total_amt, self.currency
            )

            # Show Receipt Dialog
            self._show_receipt_popup(receipt_text)

            # Reset cart and inputs
            self.cart_items.clear()
            self._refresh_cart_table()
            self.inv_var.set(f"INV-{datetime.now().strftime('%Y%m%d-%H%M')}")
            self.cust_name_var.set("Walk-in Customer")
            self.cust_phone_var.set("")

            # Refresh views
            self.refresh()
            self.controller.views["dashboard"].refresh()
            self.controller.views["product"].refresh()
            self.controller.views["stock"].refresh()
            self.controller.views["reports"].refresh()

        except Exception as e:
            messagebox.showerror("Sale Processing Error", str(e))

    def _show_receipt_popup(self, receipt_text: str):
        dlg = tk.Toplevel(self)
        dlg.title("Sales Receipt Generated")
        dlg.geometry("480x440")
        dlg.transient(self)

        txt = tk.Text(dlg, font=("Courier", 10), padx=10, pady=10)
        txt.insert("1.0", receipt_text)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

        btn_box = ttk.Frame(dlg, padding=6)
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Close", style="Primary.TButton", command=dlg.destroy).pack(side="right", padx=5)

    def _load_sales_history(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        sales = self.db.get_sales()
        for s in sales:
            self.sales_tree.insert(
                "", "end", iid=str(s["id"]),
                values=(s["id"], s["invoice_no"], s["customer_name"] or "Walk-in",
                        s["customer_phone"] or "-", s["sale_date"],
                        f"{self.currency}{s['total_amount']:.2f}",
                        f"{self.currency}{s['total_profit']:.2f}")
            )

    def _view_sale_receipt(self):
        sel = self.sales_tree.selection()
        if not sel:
            messagebox.showwarning("Select Sale", "Please select a sale record to view invoice.")
            return

        sid = int(sel[0])
        sales = self.db.get_sales()
        sale_obj = next((s for s in sales if s["id"] == sid), None)
        if not sale_obj:
            return

        items = self.db.get_sale_items(sid)
        receipt_items = [
            (it["product_name"], it["quantity"], it["unit_price"], it["subtotal"])
            for it in items
        ]
        receipt_text = generate_sales_receipt(
            sale_obj["invoice_no"],
            sale_obj["customer_name"],
            sale_obj["customer_phone"],
            receipt_items,
            sale_obj["total_amount"],
            self.currency
        )
        self._show_receipt_popup(receipt_text)
