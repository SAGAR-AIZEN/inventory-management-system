import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..database.db_manager import DatabaseManager
from ..utils.theme import COLORS, FONTS


class PurchaseView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        # Cart/staging items: list of dicts: {product_id, sku, name, unit, unit_cost, quantity, subtotal}
        self.staged_items = []

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header, text="Purchase & Stock Inward Entry", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="⟳ Refresh", style="Secondary.TButton", command=self.refresh).pack(side="right")

        # PanedWindow: Top/Left Inward Entry Form | Bottom/Right History
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: New Purchase Entry
        tab_new = ttk.Frame(notebook, style="Main.TFrame", padding=10)
        notebook.add(tab_new, text="📥 New Inward Purchase")
        self._build_entry_tab(tab_new)

        # Tab 2: Purchase History
        tab_history = ttk.Frame(notebook, style="Main.TFrame", padding=10)
        notebook.add(tab_history, text="📜 Purchase History & Records")
        self._build_history_tab(tab_history)

    def _build_entry_tab(self, parent):
        # Supplier & Invoice Header Card
        hdr_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        hdr_card.pack(fill="x", pady=(0, 10))

        ttk.Label(hdr_card, text="Supplier & Invoice Details", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ttk.Label(hdr_card, text="Invoice / Bill No:", font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.inv_var = tk.StringVar(value=f"PUR-{datetime.now().strftime('%Y%m%d-%H%M')}")
        ttk.Entry(hdr_card, textvariable=self.inv_var, width=22).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(hdr_card, text="Purchase Date (YYYY-MM-DD):", font=FONTS["body_bold"]).grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(hdr_card, textvariable=self.date_var, width=16).grid(row=1, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(hdr_card, text="Supplier Name:", font=FONTS["body_bold"]).grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.supplier_var = tk.StringVar()
        ttk.Entry(hdr_card, textvariable=self.supplier_var, width=28).grid(row=2, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(hdr_card, text="Notes / Remarks:", font=FONTS["body"]).grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.notes_var = tk.StringVar()
        ttk.Entry(hdr_card, textvariable=self.notes_var, width=30).grid(row=2, column=3, sticky="w", padx=5, pady=4)

        # Add Item Section Card
        item_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        item_card.pack(fill="x", pady=(0, 10))

        ttk.Label(item_card, text="Add Inward Stock Item", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))

        ttk.Label(item_card, text="Select Product:", font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", padx=4)
        self.prod_combo = ttk.Combobox(item_card, width=32, state="readonly")
        self.prod_combo.grid(row=1, column=1, padx=4)
        self.prod_combo.bind("<<ComboboxSelected>>", self._on_product_selected)

        ttk.Label(item_card, text="Unit Cost:", font=FONTS["body_bold"]).grid(row=1, column=2, sticky="w", padx=4)
        self.cost_var = tk.StringVar()
        ttk.Entry(item_card, textvariable=self.cost_var, width=12).grid(row=1, column=3, padx=4)

        ttk.Label(item_card, text="Quantity:", font=FONTS["body_bold"]).grid(row=1, column=4, sticky="w", padx=4)
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(item_card, textvariable=self.qty_var, width=10).grid(row=1, column=5, padx=4)

        ttk.Button(item_card, text="+ Add to Slip", style="Primary.TButton",
                   command=self._add_item_to_staged).grid(row=1, column=6, padx=10)

        # Staged Items Table
        staged_frame = ttk.Frame(parent, style="Card.TFrame", padding=12)
        staged_frame.pack(fill="both", expand=True)

        ttk.Label(staged_frame, text="Inward Stock Items Slip", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        cols = ("sku", "name", "unit", "cost", "qty", "subtotal")
        self.staged_tree = ttk.Treeview(staged_frame, columns=cols, show="headings", height=6, style="Treeview")
        self.staged_tree.heading("sku", text="SKU")
        self.staged_tree.heading("name", text="Product Name")
        self.staged_tree.heading("unit", text="Unit")
        self.staged_tree.heading("cost", text="Inward Unit Cost")
        self.staged_tree.heading("qty", text="Quantity Inward")
        self.staged_tree.heading("subtotal", text="Subtotal")

        self.staged_tree.column("sku", width=100, anchor="center")
        self.staged_tree.column("name", width=220, anchor="w")
        self.staged_tree.column("unit", width=60, anchor="center")
        self.staged_tree.column("cost", width=100, anchor="e")
        self.staged_tree.column("qty", width=100, anchor="center")
        self.staged_tree.column("subtotal", width=120, anchor="e")

        self.staged_tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(staged_frame, orient="vertical", command=self.staged_tree.yview)
        self.staged_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Bottom Bar: Total & Submit Button
        bot_bar = ttk.Frame(parent, style="Main.TFrame")
        bot_bar.pack(fill="x", pady=10)

        ttk.Button(bot_bar, text="Remove Selected Item", style="Danger.TButton",
                   command=self._remove_staged_item).pack(side="left")

        self.lbl_total = ttk.Label(bot_bar, text=f"Total Amount: {self.currency}0.00", font=FONTS["title"],
                                   style="MainBg.TLabel", foreground=COLORS["primary"])
        self.lbl_total.pack(side="left", padx=30)

        ttk.Button(bot_bar, text="✓ Confirm & Inward Stock", style="Success.TButton",
                   command=self._submit_purchase).pack(side="right")

    def _build_history_tab(self, parent):
        top_bar = ttk.Frame(parent, style="Main.TFrame")
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(top_bar, text="Recent Supplier Purchases", font=FONTS["subtitle"],
                  style="MainBg.TLabel").pack(side="left")

        ttk.Button(top_bar, text="View Items Breakdown", style="Primary.TButton",
                   command=self._view_purchase_breakdown).pack(side="right")

        cols = ("id", "inv", "supplier", "date", "amount", "notes")
        self.hist_tree = ttk.Treeview(parent, columns=cols, show="headings", style="Treeview")
        self.hist_tree.heading("id", text="ID")
        self.hist_tree.heading("inv", text="Invoice No")
        self.hist_tree.heading("supplier", text="Supplier")
        self.hist_tree.heading("date", text="Date")
        self.hist_tree.heading("amount", text="Total Inward Amount")
        self.hist_tree.heading("notes", text="Notes")

        self.hist_tree.column("id", width=40, anchor="center")
        self.hist_tree.column("inv", width=130, anchor="center")
        self.hist_tree.column("supplier", width=180, anchor="w")
        self.hist_tree.column("date", width=100, anchor="center")
        self.hist_tree.column("amount", width=130, anchor="e")
        self.hist_tree.column("notes", width=200, anchor="w")

        self.hist_tree.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(parent, orient="vertical", command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def refresh(self):
        self.currency = self.controller.config.get("currency_symbol", "₹")
        # Load products into combobox
        products = self.db.get_products()
        self.prod_map = {f"{p['sku']} - {p['name']} (Cur Stock: {p['current_stock']})": p for p in products}
        self.prod_combo["values"] = list(self.prod_map.keys())
        if self.prod_map:
            self.prod_combo.current(0)
            self._on_product_selected(None)

        self._load_purchase_history()

    def _on_product_selected(self, event):
        val = self.prod_combo.get()
        p = self.prod_map.get(val)
        if p:
            self.cost_var.set(str(p["cost_price"]))

    def _add_item_to_staged(self):
        val = self.prod_combo.get()
        p = self.prod_map.get(val)
        if not p:
            messagebox.showwarning("Warning", "Please select a valid product.")
            return

        try:
            cost = float(self.cost_var.get().strip())
            qty = int(self.qty_var.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Cost must be a number and Quantity must be an integer.")
            return

        if cost <= 0 or qty <= 0:
            messagebox.showerror("Validation Error", "Cost and Quantity must be greater than zero.")
            return

        subtotal = cost * qty
        self.staged_items.append({
            "product_id": p["id"],
            "sku": p["sku"],
            "name": p["name"],
            "unit": p["unit"],
            "unit_cost": cost,
            "quantity": qty,
            "subtotal": subtotal
        })

        self._refresh_staged_table()

    def _remove_staged_item(self):
        sel = self.staged_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.staged_items[idx]
        self._refresh_staged_table()

    def _refresh_staged_table(self):
        for item in self.staged_tree.get_children():
            self.staged_tree.delete(item)

        total = 0.0
        for i, item in enumerate(self.staged_items):
            total += item["subtotal"]
            self.staged_tree.insert(
                "", "end", iid=str(i),
                values=(item["sku"], item["name"], item["unit"],
                        f"{self.currency}{item['unit_cost']:.2f}",
                        item["quantity"],
                        f"{self.currency}{item['subtotal']:.2f}")
            )

        self.lbl_total.config(text=f"Total Amount: {self.currency}{total:.2f}")

    def _submit_purchase(self):
        if not self.staged_items:
            messagebox.showwarning("Notice", "Please add at least one item to the inward slip.")
            return

        inv_no = self.inv_var.get().strip()
        supplier = self.supplier_var.get().strip()
        pdate = self.date_var.get().strip()
        notes = self.notes_var.get().strip()

        if not inv_no or not supplier:
            messagebox.showerror("Validation Error", "Invoice Number and Supplier Name are required.")
            return

        try:
            pid = self.db.record_purchase(inv_no, supplier, pdate, self.staged_items, notes)
            messagebox.showinfo("Success", f"Purchase '{inv_no}' recorded! Stock successfully updated.")

            # Clear inputs and reset
            self.staged_items.clear()
            self._refresh_staged_table()
            self.inv_var.set(f"PUR-{datetime.now().strftime('%Y%m%d-%H%M')}")
            self.supplier_var.set("")
            self.notes_var.set("")

            # Refresh views
            self.refresh()
            self.controller.views["dashboard"].refresh()
            self.controller.views["product"].refresh()
            self.controller.views["stock"].refresh()
        except Exception as e:
            messagebox.showerror("Purchase Error", str(e))

    def _load_purchase_history(self):
        for row in self.hist_tree.get_children():
            self.hist_tree.delete(row)

        purchases = self.db.get_purchases()
        for p in purchases:
            self.hist_tree.insert(
                "", "end", iid=str(p["id"]),
                values=(p["id"], p["invoice_no"], p["supplier_name"],
                        p["purchase_date"], f"{self.currency}{p['total_amount']:.2f}", p.get("notes", ""))
            )

    def _view_purchase_breakdown(self):
        sel = self.hist_tree.selection()
        if not sel:
            messagebox.showwarning("Select Purchase", "Please select a purchase from the history table.")
            return

        pid = int(sel[0])
        items = self.db.get_purchase_items(pid)
        if not items:
            messagebox.showinfo("Details", "No items recorded for this purchase.")
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Purchase Items Breakdown (ID #{pid})")
        dlg.geometry("520x300")
        dlg.transient(self)

        tree = ttk.Treeview(dlg, columns=("sku", "name", "qty", "cost", "subtotal"), show="headings", style="Treeview")
        tree.heading("sku", text="SKU")
        tree.heading("name", text="Product")
        tree.heading("qty", text="Quantity")
        tree.heading("cost", text="Unit Cost")
        tree.heading("subtotal", text="Subtotal")

        for it in items:
            tree.insert("", "end", values=(it["sku"], it["product_name"], f"{it['quantity']} {it['unit']}",
                                           f"{self.currency}{it['unit_cost']:.2f}",
                                           f"{self.currency}{it['subtotal']:.2f}"))
        tree.pack(fill="both", expand=True, padx=10, pady=10)
