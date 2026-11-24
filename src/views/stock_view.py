import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from ..database.db_manager import DatabaseManager
from ..utils.theme import COLORS, FONTS
from ..utils.export_helper import export_to_csv


class StockView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        self.selected_category_id: Optional[int] = None
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header, text="Stock Availability & Low-Stock Alerts", style="Title.TLabel").pack(side="left")

        actions_box = ttk.Frame(header, style="Main.TFrame")
        actions_box.pack(side="right")

        ttk.Button(actions_box, text="📥 Export Stock CSV", style="Secondary.TButton",
                   command=self._export_csv).pack(side="left", padx=4)
        ttk.Button(actions_box, text="⟳ Refresh", style="Secondary.TButton",
                   command=self.refresh).pack(side="left", padx=4)

        # Valuation Metric Banner Card
        banner = ttk.Frame(self, style="Card.TFrame", padding=12)
        banner.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_units = ttk.Label(banner, text="Total Units: 0", font=FONTS["body_bold"],
                                   background=COLORS["bg_card"], foreground="#4F46E5")
        self.lbl_units.pack(side="left", padx=15)

        self.lbl_cost = ttk.Label(banner, text=f"Cost Valuation: {self.currency}0.00", font=FONTS["body_bold"],
                                  background=COLORS["bg_card"], foreground="#0D9488")
        self.lbl_cost.pack(side="left", padx=15)

        self.lbl_retail = ttk.Label(banner, text=f"Retail Valuation: {self.currency}0.00", font=FONTS["body_bold"],
                                    background=COLORS["bg_card"], foreground=COLORS["success"])
        self.lbl_retail.pack(side="left", padx=15)

        self.lbl_low_count = ttk.Label(banner, text="Low-Stock Items: 0", font=FONTS["body_bold"],
                                       background=COLORS["bg_card"], foreground=COLORS["danger"])
        self.lbl_low_count.pack(side="right", padx=15)

        # Filters Toolbar Card
        filter_card = ttk.Frame(self, style="Card.TFrame", padding=10)
        filter_card.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(filter_card, text="Search Item:", font=FONTS["body_bold"],
                  background=COLORS["bg_card"]).pack(side="left", padx=(5, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_stock_table())
        ttk.Entry(filter_card, textvariable=self.search_var, width=22).pack(side="left", padx=(0, 15))

        ttk.Label(filter_card, text="Main Directory:", font=FONTS["body_bold"],
                  background=COLORS["bg_card"]).pack(side="left", padx=(5, 4))
        self.cat_combo = ttk.Combobox(filter_card, state="readonly", width=18)
        self.cat_combo.pack(side="left", padx=(0, 15))
        self.cat_combo.bind("<<ComboboxSelected>>", self._on_category_filter)

        self.only_low_var = tk.BooleanVar(value=False)
        chk_low = ttk.Checkbutton(filter_card, text="⚠️ Show Low-Stock Alerts Only",
                                  variable=self.only_low_var, command=self.load_stock_table)
        chk_low.pack(side="left", padx=10)

        btn_reset = ttk.Button(filter_card, text="Reset Filters", style="Secondary.TButton",
                               command=self._reset_filters)
        btn_reset.pack(side="right", padx=5)

        # Stock Table Card
        table_card = ttk.Frame(self, style="Card.TFrame", padding=10)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        cols = ("sku", "name", "category", "subcategory", "unit", "cost", "sell", "stock", "threshold", "status", "cost_val", "retail_val")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", style="Treeview")

        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("subcategory", text="Sub-Category")
        self.tree.heading("unit", text="Unit")
        self.tree.heading("cost", text="Cost Price")
        self.tree.heading("sell", text="Selling Price")
        self.tree.heading("stock", text="Current Stock")
        self.tree.heading("threshold", text="Reorder Limit")
        self.tree.heading("status", text="Stock Status")
        self.tree.heading("cost_val", text="Total Cost Value")
        self.tree.heading("retail_val", text="Total Retail Value")

        self.tree.column("sku", width=95, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("category", width=105, anchor="w")
        self.tree.column("subcategory", width=115, anchor="w")
        self.tree.column("unit", width=50, anchor="center")
        self.tree.column("cost", width=80, anchor="e")
        self.tree.column("sell", width=80, anchor="e")
        self.tree.column("stock", width=85, anchor="center")
        self.tree.column("threshold", width=85, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("cost_val", width=100, anchor="e")
        self.tree.column("retail_val", width=100, anchor="e")

        # Color tags
        self.tree.tag_configure("low_tag", foreground=COLORS["danger"], font=FONTS["body_bold"])
        self.tree.tag_configure("ok_tag", foreground=COLORS["text_dark"])

        self.tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def refresh(self):
        self.currency = self.controller.config.get("currency_symbol", "₹")

        # Refresh categories combobox
        categories = self.db.get_categories()
        self.cat_map = {"All Directories": None}
        for c in categories:
            self.cat_map[c["name"]] = c["id"]
        self.cat_combo["values"] = list(self.cat_map.keys())
        self.cat_combo.current(0)
        self.selected_category_id = None

        self.load_stock_table()

    def _on_category_filter(self, event):
        val = self.cat_combo.get()
        self.selected_category_id = self.cat_map.get(val)
        self.load_stock_table()

    def _reset_filters(self):
        self.search_var.set("")
        self.cat_combo.current(0)
        self.selected_category_id = None
        self.only_low_var.set(False)
        self.load_stock_table()

    def load_stock_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_var.get().strip()
        only_low = self.only_low_var.get()

        products = self.db.get_products(
            search=search,
            category_id=self.selected_category_id,
            only_low_stock=only_low
        )

        total_units = 0
        total_cost_val = 0.0
        total_retail_val = 0.0
        low_count = 0

        for p in products:
            stock = p["current_stock"]
            threshold = p["low_stock_threshold"]
            cost = p["cost_price"]
            sell = p["selling_price"]
            c_val = stock * cost
            r_val = stock * sell

            total_units += stock
            total_cost_val += c_val
            total_retail_val += r_val

            is_low = stock <= threshold
            if is_low:
                low_count += 1
                tag = "low_tag"
                status = "⚠️ REORDER NOW"
            else:
                tag = "ok_tag"
                status = "✓ Sufficient"

            self.tree.insert(
                "", "end", iid=str(p["id"]),
                values=(
                    p["sku"],
                    p["name"],
                    p["category_name"],
                    p["subcategory_name"],
                    p["unit"],
                    f"{self.currency}{cost:.2f}",
                    f"{self.currency}{sell:.2f}",
                    f"{stock} {p['unit']}",
                    f"{threshold} {p['unit']}",
                    status,
                    f"{self.currency}{c_val:.2f}",
                    f"{self.currency}{r_val:.2f}"
                ),
                tags=(tag,)
            )

        # Update banner
        self.lbl_units.config(text=f"Total Units: {total_units:,}")
        self.lbl_cost.config(text=f"Cost Valuation: {self.currency}{total_cost_val:,.2f}")
        self.lbl_retail.config(text=f"Retail Valuation: {self.currency}{total_retail_val:,.2f}")
        self.lbl_low_count.config(text=f"Low-Stock Items: {low_count}")

    def _export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Stock Availability Report"
        )
        if not filepath:
            return

        headers = ["SKU", "Product Name", "Category", "Subcategory", "Unit", "Cost Price", "Selling Price",
                   "Current Stock", "Reorder Threshold", "Status", "Total Cost Value", "Total Retail Value"]
        rows = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            rows.append(list(vals))

        if export_to_csv(filepath, headers, rows):
            messagebox.showinfo("Export Successful", f"Stock report exported successfully to:\n{filepath}")
        else:
            messagebox.showerror("Export Failed", "Could not export stock report.")
