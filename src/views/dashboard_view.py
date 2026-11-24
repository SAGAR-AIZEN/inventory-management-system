import tkinter as tk
from tkinter import ttk
from ..database.db_manager import DatabaseManager
from ..utils.theme import COLORS, FONTS


class DashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        self.kpi_labels = {}
        self._build_ui()

    def _build_ui(self):
        # Header banner
        header_frame = ttk.Frame(self, style="Main.TFrame")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = ttk.Label(header_frame, text="Dashboard Overview", style="Title.TLabel")
        title_lbl.pack(side="left")

        refresh_btn = ttk.Button(header_frame, text="⟳ Refresh Data", style="Secondary.TButton", command=self.refresh)
        refresh_btn.pack(side="right")

        # KPI Cards Grid
        kpi_container = ttk.Frame(self, style="Main.TFrame")
        kpi_container.pack(fill="x", padx=20, pady=10)

        # 4 top KPI cards
        self._create_card(kpi_container, "Total Products", "total_products", "0", 0, 0, COLORS["primary"])
        self._create_card(kpi_container, "Total Stock Units", "total_units", "0 Units", 0, 1, "#4F46E5")
        self._create_card(kpi_container, "Stock Cost Value", "cost_val", f"{self.currency}0.00", 0, 2, "#0D9488")
        self._create_card(kpi_container, "Stock Retail Value", "retail_val", f"{self.currency}0.00", 0, 3, COLORS["success"])

        # Row 2 cards: Potential Margin and Low Stock Alert
        self._create_card(kpi_container, "Potential Profit", "potential_profit", f"{self.currency}0.00", 1, 0, "#059669")
        self._create_card(kpi_container, "⚠️ Low-Stock Alerts", "low_stock", "0 Items", 1, 1, COLORS["danger"], is_alert=True)

        # Content split: Low Stock Warning Box & Quick Action Shortcuts
        content_frame = ttk.Frame(self, style="Main.TFrame")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Left: Low Stock Items Table
        alert_box = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        alert_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        alert_header = ttk.Frame(alert_box, style="Card.TFrame")
        alert_header.pack(fill="x", pady=(0, 10))

        ttk.Label(alert_header, text="⚠️ Low Stock Alert Items (Action Needed)", font=FONTS["subtitle"],
                  background=COLORS["bg_card"], foreground=COLORS["danger"]).pack(side="left")

        view_stock_btn = ttk.Button(alert_header, text="View All in Stock Manager →", style="Primary.TButton",
                                    command=lambda: self.controller.show_view("stock"))
        view_stock_btn.pack(side="right")

        # Treeview for low stock
        cols = ("sku", "name", "category", "stock", "threshold", "action")
        self.alert_tree = ttk.Treeview(alert_box, columns=cols, show="headings", height=8, style="Treeview")
        self.alert_tree.heading("sku", text="SKU")
        self.alert_tree.heading("name", text="Product Name")
        self.alert_tree.heading("category", text="Category")
        self.alert_tree.heading("stock", text="Current Stock")
        self.alert_tree.heading("threshold", text="Reorder Limit")
        self.alert_tree.heading("action", text="Status")

        self.alert_tree.column("sku", width=90, anchor="center")
        self.alert_tree.column("name", width=180, anchor="w")
        self.alert_tree.column("category", width=110, anchor="w")
        self.alert_tree.column("stock", width=90, anchor="center")
        self.alert_tree.column("threshold", width=90, anchor="center")
        self.alert_tree.column("action", width=100, anchor="center")

        self.alert_tree.tag_configure("low_tag", foreground=COLORS["danger"], font=FONTS["body_bold"])

        scroll = ttk.Scrollbar(alert_box, orient="vertical", command=self.alert_tree.yview)
        self.alert_tree.configure(yscrollcommand=scroll.set)
        self.alert_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Right: Quick Shortcuts Card
        actions_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15, width=280)
        actions_card.pack(side="right", fill="y")
        actions_card.pack_propagate(False)

        ttk.Label(actions_card, text="Quick Shortcuts", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 15))

        btn_new_sale = ttk.Button(actions_card, text="🛒 New Sales Entry", style="Success.TButton",
                                  command=lambda: self.controller.show_view("sales"))
        btn_new_sale.pack(fill="x", pady=6)

        btn_new_purchase = ttk.Button(actions_card, text="📥 Inward Purchase", style="Primary.TButton",
                                      command=lambda: self.controller.show_view("purchase"))
        btn_new_purchase.pack(fill="x", pady=6)

        btn_add_prod = ttk.Button(actions_card, text="📦 Manage Catalog", style="Secondary.TButton",
                                  command=lambda: self.controller.show_view("product"))
        btn_add_prod.pack(fill="x", pady=6)

        btn_reports = ttk.Button(actions_card, text="📈 Profit & Reports", style="Secondary.TButton",
                                 command=lambda: self.controller.show_view("reports"))
        btn_reports.pack(fill="x", pady=6)

        # Database Engine Info Card
        db_info_box = ttk.Frame(actions_card, style="Card.TFrame", padding=10)
        db_info_box.pack(fill="x", side="bottom", pady=(10, 0))

        ttk.Label(db_info_box, text="Database Status:", font=FONTS["small"],
                  background=COLORS["bg_card"], foreground=COLORS["text_muted"]).pack(anchor="w")

        self.lbl_db_status = ttk.Label(db_info_box, text="Checking...", font=FONTS["body_bold"],
                                       background=COLORS["bg_card"], foreground=COLORS["primary"])
        self.lbl_db_status.pack(anchor="w", pady=(2, 0))

    def _create_card(self, parent, title: str, key: str, default_val: str,
                     row: int, col: int, color_accent: str, is_alert: bool = False):
        card = tk.Frame(parent, bg=COLORS["bg_card"], bd=0, highlightbackground=COLORS["border"],
                        highlightthickness=1, padx=16, pady=12)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        parent.columnconfigure(col, weight=1)

        # Accent top bar
        bar = tk.Frame(card, bg=color_accent, height=3)
        bar.pack(fill="x", side="top", pady=(0, 8))

        lbl_title = tk.Label(card, text=title.upper(), font=FONTS["kpi_label"],
                             fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(card, text=default_val, font=FONTS["kpi_value"],
                           fg=color_accent if is_alert else COLORS["text_dark"], bg=COLORS["bg_card"])
        lbl_val.pack(anchor="w", pady=(4, 0))

        self.kpi_labels[key] = lbl_val

    def refresh(self):
        """Reload summary statistics and low stock items from database."""
        summary = self.db.get_stock_summary()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        self.kpi_labels["total_products"].config(text=f"{summary['total_products']:,}")
        self.kpi_labels["total_units"].config(text=f"{summary['total_units']:,} Units")
        self.kpi_labels["cost_val"].config(text=f"{self.currency}{summary['total_cost_value']:,.2f}")
        self.kpi_labels["retail_val"].config(text=f"{self.currency}{summary['total_retail_value']:,.2f}")
        self.kpi_labels["potential_profit"].config(text=f"{self.currency}{summary['potential_profit']:,.2f}")

        low_cnt = summary["low_stock_count"]
        self.kpi_labels["low_stock"].config(
            text=f"{low_cnt} Items" if low_cnt > 0 else "0 (All Good)",
            fg=COLORS["danger"] if low_cnt > 0 else COLORS["success"]
        )

        # Update DB status label
        st = self.db.get_status()
        self.lbl_db_status.config(
            text=f"{st['engine']}: {st['message'].split('(')[0].strip()}",
            foreground=COLORS["success"] if st["is_mysql"] else COLORS["warning"]
        )

        # Reload low stock tree
        for row in self.alert_tree.get_children():
            self.alert_tree.delete(row)

        low_products = self.db.get_products(only_low_stock=True)
        for p in low_products:
            self.alert_tree.insert(
                "", "end",
                values=(p["sku"], p["name"], p["category_name"], f"{p['current_stock']} {p['unit']}",
                        f"{p['low_stock_threshold']} {p['unit']}", "REORDER NOW"),
                tags=("low_tag",)
            )
