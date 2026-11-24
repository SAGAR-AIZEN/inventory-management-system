import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from ..database.db_manager import DatabaseManager
from ..utils.theme import COLORS, FONTS
from ..utils.export_helper import export_to_csv, generate_profit_report_text


class ReportsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        self.start_date_str = None
        self.end_date_str = None

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header, text="Profit, Valuation & Sales Performance Reports", style="Title.TLabel").pack(side="left")

        btn_box = ttk.Frame(header, style="Main.TFrame")
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="📄 Summary Statement", style="Primary.TButton",
                   command=self._generate_text_summary).pack(side="left", padx=4)
        ttk.Button(btn_box, text="📥 Export CSV", style="Secondary.TButton",
                   command=self._export_csv).pack(side="left", padx=4)
        ttk.Button(btn_box, text="⟳ Refresh", style="Secondary.TButton",
                   command=self.refresh).pack(side="left", padx=4)

        # Date Range Filter Toolbar Card
        filter_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        filter_card.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(filter_card, text="Quick Period Filter:", font=FONTS["body_bold"],
                  background=COLORS["bg_card"]).pack(side="left", padx=(5, 8))

        ttk.Button(filter_card, text="Today", style="Secondary.TButton",
                   command=lambda: self._set_quick_date("today")).pack(side="left", padx=3)
        ttk.Button(filter_card, text="Last 7 Days", style="Secondary.TButton",
                   command=lambda: self._set_quick_date("7days")).pack(side="left", padx=3)
        ttk.Button(filter_card, text="This Month", style="Secondary.TButton",
                   command=lambda: self._set_quick_date("month")).pack(side="left", padx=3)
        ttk.Button(filter_card, text="All Time", style="Secondary.TButton",
                   command=lambda: self._set_quick_date("all")).pack(side="left", padx=3)

        ttk.Label(filter_card, text="Custom Range (YYYY-MM-DD):", font=FONTS["body_bold"],
                  background=COLORS["bg_card"]).pack(side="left", padx=(20, 5))

        self.start_var = tk.StringVar()
        ttk.Entry(filter_card, textvariable=self.start_var, width=12).pack(side="left", padx=2)

        ttk.Label(filter_card, text="to", background=COLORS["bg_card"]).pack(side="left", padx=4)

        self.end_var = tk.StringVar()
        ttk.Entry(filter_card, textvariable=self.end_var, width=12).pack(side="left", padx=2)

        ttk.Button(filter_card, text="Apply Filter", style="Primary.TButton",
                   command=self._apply_custom_range).pack(side="left", padx=8)

        # KPI Financial Metrics Grid
        kpi_frame = ttk.Frame(self, style="Main.TFrame")
        kpi_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.kpis = {}
        self._create_card(kpi_frame, "Total Revenue", "revenue", f"{self.currency}0.00", 0, 0, COLORS["primary"])
        self._create_card(kpi_frame, "Cost of Goods Sold (COGS)", "cogs", f"{self.currency}0.00", 0, 1, "#64748B")
        self._create_card(kpi_frame, "Net Gross Profit", "profit", f"{self.currency}0.00", 0, 2, COLORS["success"])
        self._create_card(kpi_frame, "Overall Profit Margin", "margin", "0.00%", 0, 3, "#059669")

        # Split content: Top Selling Products (Left) & Sales Transactions Ledger (Right)
        split_pane = ttk.PanedWindow(self, orient="horizontal")
        split_pane.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Left: Top Products
        top_prod_card = ttk.Frame(split_pane, style="Card.TFrame", padding=12)
        split_pane.add(top_prod_card, weight=2)

        ttk.Label(top_prod_card, text="🏆 Top Selling Products (By Volume)", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        cols_top = ("name", "qty", "profit")
        self.top_tree = ttk.Treeview(top_prod_card, columns=cols_top, show="headings", height=8, style="Treeview")
        self.top_tree.heading("name", text="Product Name")
        self.top_tree.heading("qty", text="Total Sold")
        self.top_tree.heading("profit", text="Profit Generated")

        self.top_tree.column("name", width=180, anchor="w")
        self.top_tree.column("qty", width=90, anchor="center")
        self.top_tree.column("profit", width=110, anchor="e")

        self.top_tree.pack(fill="both", expand=True)

        # Right: Sales Transactions for the Period
        sales_card = ttk.Frame(split_pane, style="Card.TFrame", padding=12)
        split_pane.add(sales_card, weight=3)

        ttk.Label(sales_card, text="📋 Sales Transactions for Period", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        cols_sales = ("inv", "customer", "date", "revenue", "profit")
        self.sales_tree = ttk.Treeview(sales_card, columns=cols_sales, show="headings", style="Treeview")
        self.sales_tree.heading("inv", text="Invoice No")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("date", text="Date")
        self.sales_tree.heading("revenue", text="Bill Amount")
        self.sales_tree.heading("profit", text="Profit")

        self.sales_tree.column("inv", width=110, anchor="center")
        self.sales_tree.column("customer", width=140, anchor="w")
        self.sales_tree.column("date", width=90, anchor="center")
        self.sales_tree.column("revenue", width=100, anchor="e")
        self.sales_tree.column("profit", width=100, anchor="e")

        self.sales_tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(sales_card, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def _create_card(self, parent, title: str, key: str, default_val: str,
                     row: int, col: int, color_accent: str):
        card = tk.Frame(parent, bg=COLORS["bg_card"], bd=0, highlightbackground=COLORS["border"],
                        highlightthickness=1, padx=16, pady=12)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        parent.columnconfigure(col, weight=1)

        bar = tk.Frame(card, bg=color_accent, height=3)
        bar.pack(fill="x", side="top", pady=(0, 8))

        tk.Label(card, text=title.upper(), font=FONTS["kpi_label"],
                 fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w")

        lbl_val = tk.Label(card, text=default_val, font=FONTS["kpi_value"],
                           fg=color_accent, bg=COLORS["bg_card"])
        lbl_val.pack(anchor="w", pady=(4, 0))

        self.kpis[key] = lbl_val

    def refresh(self):
        self.currency = self.controller.config.get("currency_symbol", "₹")
        self._load_reports_data()

    def _set_quick_date(self, period: str):
        today = datetime.now().date()
        if period == "today":
            self.start_date_str = today.strftime("%Y-%m-%d")
            self.end_date_str = today.strftime("%Y-%m-%d")
        elif period == "7days":
            self.start_date_str = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            self.end_date_str = today.strftime("%Y-%m-%d")
        elif period == "month":
            self.start_date_str = today.replace(day=1).strftime("%Y-%m-%d")
            self.end_date_str = today.strftime("%Y-%m-%d")
        else:  # "all"
            self.start_date_str = None
            self.end_date_str = None

        self.start_var.set(self.start_date_str or "")
        self.end_var.set(self.end_date_str or "")
        self._load_reports_data()

    def _apply_custom_range(self):
        s = self.start_var.get().strip()
        e = self.end_var.get().strip()
        self.start_date_str = s if s else None
        self.end_date_str = e if e else None
        self._load_reports_data()

    def _load_reports_data(self):
        report = self.db.get_profit_report(self.start_date_str, self.end_date_str)
        self.last_report = report

        # Update KPI Cards
        rev = report["total_revenue"]
        cogs = report["total_cost"]
        prof = report["total_profit"]
        margin = report["margin_percentage"]

        self.kpis["revenue"].config(text=f"{self.currency}{rev:,.2f}")
        self.kpis["cogs"].config(text=f"{self.currency}{cogs:,.2f}")
        self.kpis["profit"].config(text=f"{self.currency}{prof:,.2f}")
        self.kpis["margin"].config(text=f"{margin:.2f}%")

        # Top products
        for row in self.top_tree.get_children():
            self.top_tree.delete(row)

        for p in report["top_products"]:
            self.top_tree.insert(
                "", "end",
                values=(p["name"], p["qty"], f"{self.currency}{float(p['profit']):.2f}")
            )

        # Sales ledger for period
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        sales = self.db.get_sales()
        for s in sales:
            s_date = str(s["sale_date"])
            if self.start_date_str and s_date < self.start_date_str:
                continue
            if self.end_date_str and s_date > self.end_date_str:
                continue

            self.sales_tree.insert(
                "", "end",
                values=(s["invoice_no"], s["customer_name"] or "Walk-in", s["sale_date"],
                        f"{self.currency}{s['total_amount']:.2f}",
                        f"{self.currency}{s['total_profit']:.2f}")
            )

    def _generate_text_summary(self):
        start = self.start_date_str or "Earliest"
        end = self.end_date_str or "Latest"
        summary_text = generate_profit_report_text(self.last_report, start, end, self.currency)

        dlg = tk.Toplevel(self)
        dlg.title("Profit Performance Statement")
        dlg.geometry("520x450")
        dlg.transient(self)

        txt = tk.Text(dlg, font=("Courier", 10), padx=10, pady=10)
        txt.insert("1.0", summary_text)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

        btn_box = ttk.Frame(dlg, padding=6)
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Close", style="Primary.TButton", command=dlg.destroy).pack(side="right")

    def _export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Profit & Sales Report"
        )
        if not filepath:
            return

        headers = ["Invoice No", "Customer", "Sale Date", "Bill Amount", "Profit"]
        rows = []
        for iid in self.sales_tree.get_children():
            rows.append(list(self.sales_tree.item(iid, "values")))

        if export_to_csv(filepath, headers, rows):
            messagebox.showinfo("Export Successful", f"Report saved to:\n{filepath}")
        else:
            messagebox.showerror("Export Failed", "Could not export report.")
