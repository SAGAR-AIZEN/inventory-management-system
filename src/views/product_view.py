import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from ..database.db_manager import DatabaseManager
from ..utils.theme import COLORS, FONTS


class ProductView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.currency = self.controller.config.get("currency_symbol", "₹")

        self.selected_category_id: Optional[int] = None
        self.selected_subcategory_id: Optional[int] = None

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header, text="Product & Directory Management", style="Title.TLabel").pack(side="left")

        btn_box = ttk.Frame(header, style="Main.TFrame")
        btn_box.pack(side="right")

        ttk.Button(btn_box, text="+ Add Main Category", style="Secondary.TButton",
                   command=self._dialog_add_category).pack(side="left", padx=4)
        ttk.Button(btn_box, text="+ Add Sub-Category", style="Secondary.TButton",
                   command=self._dialog_add_subcategory).pack(side="left", padx=4)
        ttk.Button(btn_box, text="➕ Add New Product", style="Primary.TButton",
                   command=self._dialog_add_product).pack(side="left", padx=4)

        # Main Split Content: Left Directory Treeview | Right Products Table
        split_pane = ttk.PanedWindow(self, orient="horizontal")
        split_pane.pack(fill="both", expand=True, padx=20, pady=10)

        # ---------------------------------------------------------------------
        # LEFT PANE: Directory Hierarchy Treeview (Main -> Sub Directory)
        # ---------------------------------------------------------------------
        left_frame = ttk.Frame(split_pane, style="Card.TFrame", padding=10)
        split_pane.add(left_frame, weight=1)

        ttk.Label(left_frame, text="📁 Directory Hierarchy", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        ttk.Label(left_frame, text="Click to filter products:", font=FONTS["small"],
                  background=COLORS["bg_card"], foreground=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        self.dir_tree = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.dir_tree.pack(fill="both", expand=True, side="left")
        self.dir_tree.bind("<<TreeviewSelect>>", self._on_dir_selected)

        dir_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.dir_tree.yview)
        self.dir_tree.configure(yscrollcommand=dir_scroll.set)
        dir_scroll.pack(side="right", fill="y")

        # ---------------------------------------------------------------------
        # RIGHT PANE: Search Bar & Product List
        # ---------------------------------------------------------------------
        right_frame = ttk.Frame(split_pane, style="Card.TFrame", padding=12)
        split_pane.add(right_frame, weight=3)

        # Search Bar & Filter info
        top_filter = ttk.Frame(right_frame, style="Card.TFrame")
        top_filter.pack(fill="x", pady=(0, 10))

        ttk.Label(top_filter, text="Search:", font=FONTS["body_bold"],
                  background=COLORS["bg_card"]).pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_products())
        search_entry = ttk.Entry(top_filter, textvariable=self.search_var, width=28)
        search_entry.pack(side="left", padx=(0, 10))

        self.lbl_active_filter = ttk.Label(top_filter, text="Filter: All Directories", font=FONTS["small"],
                                           background=COLORS["bg_card"], foreground=COLORS["primary"])
        self.lbl_active_filter.pack(side="left", padx=10)

        btn_clear_filter = ttk.Button(top_filter, text="Reset Filter", style="Secondary.TButton",
                                      command=self._reset_directory_filter)
        btn_clear_filter.pack(side="right")

        # Products Table
        table_frame = ttk.Frame(right_frame, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True)

        cols = ("id", "sku", "name", "category", "subcategory", "unit", "cost", "sell", "stock", "limit", "status")
        self.prod_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse", style="Treeview")

        self.prod_tree.heading("id", text="ID")
        self.prod_tree.heading("sku", text="SKU / Barcode")
        self.prod_tree.heading("name", text="Product Name")
        self.prod_tree.heading("category", text="Main Directory")
        self.prod_tree.heading("subcategory", text="Sub Directory")
        self.prod_tree.heading("unit", text="Unit")
        self.prod_tree.heading("cost", text="Cost Price")
        self.prod_tree.heading("sell", text="Selling Price")
        self.prod_tree.heading("stock", text="In Stock")
        self.prod_tree.heading("limit", text="Reorder Limit")
        self.prod_tree.heading("status", text="Stock Status")

        self.prod_tree.column("id", width=35, anchor="center")
        self.prod_tree.column("sku", width=95, anchor="center")
        self.prod_tree.column("name", width=170, anchor="w")
        self.prod_tree.column("category", width=110, anchor="w")
        self.prod_tree.column("subcategory", width=120, anchor="w")
        self.prod_tree.column("unit", width=55, anchor="center")
        self.prod_tree.column("cost", width=80, anchor="e")
        self.prod_tree.column("sell", width=80, anchor="e")
        self.prod_tree.column("stock", width=75, anchor="center")
        self.prod_tree.column("limit", width=85, anchor="center")
        self.prod_tree.column("status", width=95, anchor="center")

        # Color tags
        self.prod_tree.tag_configure("low_stock_tag", foreground=COLORS["danger"], font=FONTS["body_bold"])
        self.prod_tree.tag_configure("ok_stock_tag", foreground=COLORS["text_dark"])

        p_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.prod_tree.yview)
        self.prod_tree.configure(yscrollcommand=p_scroll.set)
        self.prod_tree.pack(side="left", fill="both", expand=True)
        p_scroll.pack(side="right", fill="y")

        # Table Action Buttons
        actions_bar = ttk.Frame(right_frame, style="Card.TFrame")
        actions_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(actions_bar, text="✏️ Edit Selected", style="Secondary.TButton",
                   command=self._dialog_edit_product).pack(side="left", padx=(0, 6))
        ttk.Button(actions_bar, text="🗑️ Delete Selected", style="Danger.TButton",
                   command=self._delete_selected_product).pack(side="left", padx=6)
        ttk.Button(actions_bar, text="⟳ Refresh", style="Secondary.TButton",
                   command=self.refresh).pack(side="right")

    def refresh(self):
        """Reload categories, directory hierarchy, and product list."""
        self.currency = self.controller.config.get("currency_symbol", "₹")
        self.load_directory_tree()
        self.load_products()

    def load_directory_tree(self):
        """Build hierarchical directory view: Root -> Main Category -> Subcategory."""
        for item in self.dir_tree.get_children():
            self.dir_tree.delete(item)

        root_id = self.dir_tree.insert("", "end", iid="root", text="📁 [All Directories]", open=True)

        categories = self.db.get_categories()
        for cat in categories:
            cat_node = self.dir_tree.insert(
                root_id, "end",
                iid=f"cat_{cat['id']}",
                text=f"📂 {cat['name']}",
                open=True
            )
            subcategories = self.db.get_subcategories(category_id=cat["id"])
            for sub in subcategories:
                self.dir_tree.insert(
                    cat_node, "end",
                    iid=f"sub_{sub['id']}",
                    text=f"  └ 📄 {sub['name']}"
                )

    def _on_dir_selected(self, event):
        selected = self.dir_tree.selection()
        if not selected:
            return
        node_id = selected[0]
        if node_id == "root":
            self.selected_category_id = None
            self.selected_subcategory_id = None
            self.lbl_active_filter.config(text="Filter: All Directories")
        elif node_id.startswith("cat_"):
            cat_id = int(node_id.replace("cat_", ""))
            self.selected_category_id = cat_id
            self.selected_subcategory_id = None
            cat_name = self.dir_tree.item(node_id, "text").replace("📂", "").strip()
            self.lbl_active_filter.config(text=f"Filter: Main Directory [{cat_name}]")
        elif node_id.startswith("sub_"):
            sub_id = int(node_id.replace("sub_", ""))
            self.selected_category_id = None
            self.selected_subcategory_id = sub_id
            sub_name = self.dir_tree.item(node_id, "text").replace("└ 📄", "").strip()
            self.lbl_active_filter.config(text=f"Filter: Sub Directory [{sub_name}]")

        self.load_products()

    def _reset_directory_filter(self):
        self.selected_category_id = None
        self.selected_subcategory_id = None
        self.search_var.set("")
        self.lbl_active_filter.config(text="Filter: All Directories")
        self.dir_tree.selection_set("root")
        self.load_products()

    def load_products(self):
        """Fetch products filtered by directory selection and search term."""
        for row in self.prod_tree.get_children():
            self.prod_tree.delete(row)

        search_term = self.search_var.get().strip()
        products = self.db.get_products(
            search=search_term,
            category_id=self.selected_category_id,
            subcategory_id=self.selected_subcategory_id
        )

        for p in products:
            is_low = p["current_stock"] <= p["low_stock_threshold"]
            tag = "low_stock_tag" if is_low else "ok_stock_tag"
            status = "⚠️ LOW STOCK" if is_low else "✓ In Stock"

            self.prod_tree.insert(
                "", "end",
                iid=str(p["id"]),
                values=(
                    p["id"],
                    p["sku"],
                    p["name"],
                    p["category_name"],
                    p["subcategory_name"],
                    p["unit"],
                    f"{self.currency}{p['cost_price']:.2f}",
                    f"{self.currency}{p['selling_price']:.2f}",
                    p["current_stock"],
                    p["low_stock_threshold"],
                    status
                ),
                tags=(tag,)
            )

    # -------------------------------------------------------------------------
    # DIALOGUES
    # -------------------------------------------------------------------------
    def _dialog_add_category(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Main Directory / Category")
        dlg.geometry("380x200")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Category Name:", font=FONTS["body_bold"]).grid(row=0, column=0, sticky="w", pady=4)
        name_entry = ttk.Entry(frm, width=30)
        name_entry.grid(row=0, column=1, pady=4)
        name_entry.focus()

        ttk.Label(frm, text="Description:", font=FONTS["body"]).grid(row=1, column=0, sticky="w", pady=4)
        desc_entry = ttk.Entry(frm, width=30)
        desc_entry.grid(row=1, column=1, pady=4)

        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Validation Error", "Category Name cannot be empty.", parent=dlg)
                return
            try:
                self.db.add_category(name, desc_entry.get().strip())
                dlg.destroy()
                self.refresh()
                messagebox.showinfo("Success", f"Category '{name}' created successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        btn_box = ttk.Frame(frm)
        btn_box.grid(row=2, column=0, columnspan=2, pady=16)
        ttk.Button(btn_box, text="Save Category", style="Primary.TButton", command=save).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dlg.destroy).pack(side="left")

    def _dialog_add_subcategory(self):
        categories = self.db.get_categories()
        if not categories:
            messagebox.showwarning("Notice", "Please create at least one Main Category first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add Sub-Directory / Sub-Category")
        dlg.geometry("420x240")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Main Directory:", font=FONTS["body_bold"]).grid(row=0, column=0, sticky="w", pady=6)
        cat_map = {c["name"]: c["id"] for c in categories}
        cat_combo = ttk.Combobox(frm, values=list(cat_map.keys()), state="readonly", width=26)
        cat_combo.grid(row=0, column=1, pady=6)
        cat_combo.current(0)

        ttk.Label(frm, text="Sub-Category Name:", font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(frm, width=28)
        name_entry.grid(row=1, column=1, pady=6)
        name_entry.focus()

        ttk.Label(frm, text="Description:", font=FONTS["body"]).grid(row=2, column=0, sticky="w", pady=6)
        desc_entry = ttk.Entry(frm, width=28)
        desc_entry.grid(row=2, column=1, pady=6)

        def save():
            sub_name = name_entry.get().strip()
            cat_name = cat_combo.get()
            if not sub_name:
                messagebox.showerror("Validation Error", "Subcategory Name cannot be empty.", parent=dlg)
                return
            cid = cat_map.get(cat_name)
            try:
                self.db.add_subcategory(cid, sub_name, desc_entry.get().strip())
                dlg.destroy()
                self.refresh()
                messagebox.showinfo("Success", f"Subcategory '{sub_name}' added under '{cat_name}'.")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        btn_box = ttk.Frame(frm)
        btn_box.grid(row=3, column=0, columnspan=2, pady=16)
        ttk.Button(btn_box, text="Save Sub-Category", style="Primary.TButton", command=save).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dlg.destroy).pack(side="left")

    def _dialog_add_product(self):
        subcategories = self.db.get_subcategories()
        if not subcategories:
            messagebox.showwarning("Notice", "Please create at least one Sub-Category directory first.")
            return

        self._product_form_dialog(title="Add New Product", is_edit=False)

    def _dialog_edit_product(self):
        selected = self.prod_tree.selection()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product from the table to edit.")
            return
        prod_id = int(selected[0])
        prod = self.db.get_product_by_id(prod_id)
        if not prod:
            messagebox.showerror("Error", "Product details not found.")
            return

        self._product_form_dialog(title="Edit Product", is_edit=True, prod=prod)

    def _product_form_dialog(self, title: str, is_edit: bool = False, prod: dict = None):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("460x420")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill="both", expand=True)

        # SKU
        ttk.Label(frm, text="SKU / Barcode:", font=FONTS["body_bold"]).grid(row=0, column=0, sticky="w", pady=4)
        sku_entry = ttk.Entry(frm, width=28)
        sku_entry.grid(row=0, column=1, pady=4)
        if prod:
            sku_entry.insert(0, prod["sku"])

        # Name
        ttk.Label(frm, text="Product Name:", font=FONTS["body_bold"]).grid(row=1, column=0, sticky="w", pady=4)
        name_entry = ttk.Entry(frm, width=28)
        name_entry.grid(row=1, column=1, pady=4)
        if prod:
            name_entry.insert(0, prod["name"])

        # Subcategory mapping
        subcategories = self.db.get_subcategories()
        subcat_map = {f"{s['category_name']} -> {s['name']}": s["id"] for s in subcategories}
        ttk.Label(frm, text="Directory / Subcategory:", font=FONTS["body_bold"]).grid(row=2, column=0, sticky="w", pady=4)
        sub_combo = ttk.Combobox(frm, values=list(subcat_map.keys()), state="readonly", width=26)
        sub_combo.grid(row=2, column=1, pady=4)

        current_sub_text = None
        if prod:
            for k, sid in subcat_map.items():
                if sid == prod["subcategory_id"]:
                    current_sub_text = k
                    break
        if current_sub_text:
            sub_combo.set(current_sub_text)
        elif subcat_map:
            sub_combo.current(0)

        # Unit
        ttk.Label(frm, text="Measurement Unit:", font=FONTS["body"]).grid(row=3, column=0, sticky="w", pady=4)
        unit_combo = ttk.Combobox(frm, values=["Pcs", "Pack", "Box", "Kg", "Ltr", "Meter", "Roll", "Set"], width=26)
        unit_combo.grid(row=3, column=1, pady=4)
        unit_combo.set(prod["unit"] if prod else "Pcs")

        # Cost Price
        ttk.Label(frm, text=f"Cost Price ({self.currency}):", font=FONTS["body_bold"]).grid(row=4, column=0, sticky="w", pady=4)
        cost_entry = ttk.Entry(frm, width=28)
        cost_entry.grid(row=4, column=1, pady=4)
        cost_entry.insert(0, str(prod["cost_price"]) if prod else "0.00")

        # Selling Price
        ttk.Label(frm, text=f"Selling Price ({self.currency}):", font=FONTS["body_bold"]).grid(row=5, column=0, sticky="w", pady=4)
        sell_entry = ttk.Entry(frm, width=28)
        sell_entry.grid(row=5, column=1, pady=4)
        sell_entry.insert(0, str(prod["selling_price"]) if prod else "0.00")

        # Current Stock
        ttk.Label(frm, text="Current Stock:", font=FONTS["body"]).grid(row=6, column=0, sticky="w", pady=4)
        stock_entry = ttk.Entry(frm, width=28)
        stock_entry.grid(row=6, column=1, pady=4)
        stock_entry.insert(0, str(prod["current_stock"]) if prod else "0")

        # Low Stock Threshold
        ttk.Label(frm, text="Reorder Limit (Threshold):", font=FONTS["body"]).grid(row=7, column=0, sticky="w", pady=4)
        limit_entry = ttk.Entry(frm, width=28)
        limit_entry.grid(row=7, column=1, pady=4)
        limit_entry.insert(0, str(prod["low_stock_threshold"]) if prod else "5")

        def submit():
            sku = sku_entry.get().strip()
            name = name_entry.get().strip()
            sub_key = sub_combo.get()
            sub_id = subcat_map.get(sub_key)
            unit = unit_combo.get().strip() or "Pcs"

            if not sku or not name:
                messagebox.showerror("Validation Error", "SKU and Product Name are required.", parent=dlg)
                return
            if not sub_id:
                messagebox.showerror("Validation Error", "Please select a valid subcategory directory.", parent=dlg)
                return

            try:
                cost = float(cost_entry.get().strip())
                sell = float(sell_entry.get().strip())
                stock = int(stock_entry.get().strip())
                limit = int(limit_entry.get().strip())
            except ValueError:
                messagebox.showerror("Validation Error", "Prices must be decimal numbers and stock/limit must be integers.", parent=dlg)
                return

            if cost < 0 or sell < 0 or stock < 0 or limit < 0:
                messagebox.showerror("Validation Error", "Values cannot be negative.", parent=dlg)
                return

            try:
                if is_edit:
                    self.db.update_product(prod["id"], sku, name, sub_id, unit, cost, sell, stock, limit)
                    messagebox.showinfo("Success", f"Product '{name}' updated successfully.")
                else:
                    self.db.add_product(sku, name, sub_id, unit, cost, sell, stock, limit)
                    messagebox.showinfo("Success", f"Product '{name}' added successfully.")

                dlg.destroy()
                self.refresh()
                self.controller.views["dashboard"].refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=18)
        ttk.Button(btn_frame, text="Save Product", style="Primary.TButton", command=submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", style="Secondary.TButton", command=dlg.destroy).pack(side="left")

    def _delete_selected_product(self):
        selected = self.prod_tree.selection()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product to delete.")
            return

        prod_id = int(selected[0])
        prod = self.db.get_product_by_id(prod_id)
        if not prod:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete product '{prod['name']}' (SKU: {prod['sku']})?\n"
            "This action cannot be undone."
        )
        if confirm:
            try:
                self.db.delete_product(prod_id)
                self.refresh()
                self.controller.views["dashboard"].refresh()
                messagebox.showinfo("Deleted", f"Product '{prod['name']}' has been removed.")
            except Exception as e:
                messagebox.showerror("Cannot Delete", f"Product cannot be deleted (may have active purchase/sales entries): {e}")
