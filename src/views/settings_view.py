import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from ..database.db_manager import DatabaseManager
from ..utils.config import load_config, save_config
from ..utils.theme import COLORS, FONTS


class SettingsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.db = DatabaseManager.get_instance()
        self.config = load_config()

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Main.TFrame")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header, text="System & Database Settings (XAMPP / MySQL)", style="Title.TLabel").pack(side="left")

        # Scrollable container
        canvas = tk.Canvas(self, bg=COLORS["bg_main"], bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Main.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 15))
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=(0, 15))

        # ---------------------------------------------------------------------
        # 1. Active Database Status Card
        # ---------------------------------------------------------------------
        status_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        status_card.pack(fill="x", pady=(0, 15))

        ttk.Label(status_card, text="Current Active Database Connection", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        self.lbl_active_db = ttk.Label(status_card, text="Status: Loading...", font=FONTS["body_bold"],
                                       background=COLORS["bg_card"], foreground=COLORS["primary"])
        self.lbl_active_db.pack(anchor="w", pady=(0, 4))

        # Engine selector
        eng_frame = ttk.Frame(status_card, style="Card.TFrame")
        eng_frame.pack(fill="x", pady=6)

        ttk.Label(eng_frame, text="Select Active Backend Engine:", font=FONTS["body_bold"],
                  background=COLORS["bg_card"]).pack(side="left", padx=(0, 10))

        self.engine_var = tk.StringVar(value=self.config.get("db_type", "mysql"))
        ttk.Radiobutton(eng_frame, text="MySQL / XAMPP (CBSE Evaluator Requirement)",
                        value="mysql", variable=self.engine_var).pack(side="left", padx=10)
        ttk.Radiobutton(eng_frame, text="SQLite (Local File / Offline)",
                        value="sqlite", variable=self.engine_var).pack(side="left", padx=10)

        # ---------------------------------------------------------------------
        # 2. MySQL / XAMPP Configuration Card
        # ---------------------------------------------------------------------
        mysql_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        mysql_card.pack(fill="x", pady=(0, 15))

        ttk.Label(mysql_card, text="MySQL Server Settings (XAMPP localhost:3306)", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        mysql_conf = self.config.get("mysql", {})

        ttk.Label(mysql_card, text="Host Name:", font=FONTS["body"]).grid(row=1, column=0, sticky="w", pady=4)
        self.host_var = tk.StringVar(value=mysql_conf.get("host", "localhost"))
        ttk.Entry(mysql_card, textvariable=self.host_var, width=22).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(mysql_card, text="Port (Default 3306):", font=FONTS["body"]).grid(row=1, column=2, sticky="w", padx=(20, 5), pady=4)
        self.port_var = tk.StringVar(value=str(mysql_conf.get("port", 3306)))
        ttk.Entry(mysql_card, textvariable=self.port_var, width=12).grid(row=1, column=3, sticky="w", pady=4)

        ttk.Label(mysql_card, text="Username (Default 'root'):", font=FONTS["body"]).grid(row=2, column=0, sticky="w", pady=4)
        self.user_var = tk.StringVar(value=mysql_conf.get("user", "root"))
        ttk.Entry(mysql_card, textvariable=self.user_var, width=22).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(mysql_card, text="Password (Default blank):", font=FONTS["body"]).grid(row=2, column=2, sticky="w", padx=(20, 5), pady=4)
        self.pass_var = tk.StringVar(value=mysql_conf.get("password", ""))
        ttk.Entry(mysql_card, textvariable=self.pass_var, width=22, show="*").grid(row=2, column=3, sticky="w", pady=4)

        ttk.Label(mysql_card, text="Database Name:", font=FONTS["body"]).grid(row=3, column=0, sticky="w", pady=4)
        self.dbname_var = tk.StringVar(value=mysql_conf.get("database", "inventory_db"))
        ttk.Entry(mysql_card, textvariable=self.dbname_var, width=22).grid(row=3, column=1, sticky="w", pady=4)

        btn_box = ttk.Frame(mysql_card, style="Card.TFrame")
        btn_box.grid(row=4, column=0, columnspan=4, sticky="w", pady=(14, 0))

        ttk.Button(btn_box, text="🔌 Test MySQL Connection", style="Secondary.TButton",
                   command=self._test_mysql_conn).pack(side="left", padx=(0, 10))
        ttk.Button(btn_box, text="💾 Save & Reconnect", style="Primary.TButton",
                   command=self._save_settings).pack(side="left")

        # ---------------------------------------------------------------------
        # 3. SQLite Storage Path Card (User Configurable Storage)
        # ---------------------------------------------------------------------
        sqlite_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        sqlite_card.pack(fill="x", pady=(0, 15))

        ttk.Label(sqlite_card, text="Local SQLite Database File Location", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        ttk.Label(sqlite_card, text="You can select custom drive or directory for data storage:", font=FONTS["small"],
                  background=COLORS["bg_card"], foreground=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        path_box = ttk.Frame(sqlite_card, style="Card.TFrame")
        path_box.pack(fill="x", pady=4)

        sq_conf = self.config.get("sqlite", {})
        self.sqlite_path_var = tk.StringVar(value=sq_conf.get("file_path", "data/inventory.db"))
        ttk.Entry(path_box, textvariable=self.sqlite_path_var, width=50).pack(side="left", padx=(0, 10))

        ttk.Button(path_box, text="Browse Location...", style="Secondary.TButton",
                   command=self._browse_sqlite_path).pack(side="left")

        # ---------------------------------------------------------------------
        # 4. Database Backup & Maintenance Card
        # ---------------------------------------------------------------------
        backup_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        backup_card.pack(fill="x", pady=(0, 15))

        ttk.Label(backup_card, text="Database Backup & Archival", font=FONTS["subtitle"],
                  background=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        ttk.Button(backup_card, text="💾 Create Timestamped Backup Now", style="Success.TButton",
                   command=self._create_backup).pack(anchor="w", pady=4)

        # ---------------------------------------------------------------------
        # 5. CBSE Evaluator Viva Notes
        # ---------------------------------------------------------------------
        viva_card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=14)
        viva_card.pack(fill="x", pady=(0, 15))

        ttk.Label(viva_card, text="💡 CBSE Evaluator & Teacher Demonstration Guide", font=FONTS["subtitle"],
                  background=COLORS["bg_card"], foreground=COLORS["primary"]).pack(anchor="w", pady=(0, 6))

        guide_text = (
            "1. Start XAMPP Control Panel and click 'Start' next to MySQL and Apache.\n"
            "2. Open your web browser at: http://localhost/phpmyadmin\n"
            "3. Click on the database 'inventory_db' on the left sidebar to show all 6 tables:\n"
            "   - categories, sub_categories, products, purchases, purchase_items, sales, sales_items\n"
            "4. Show the external examiner live CRUD operations in this Python application\n"
            "   and refresh phpMyAdmin to verify records are synced in real-time!"
        )
        ttk.Label(viva_card, text=guide_text, font=FONTS["body"], background=COLORS["bg_card"], justify="left").pack(anchor="w")

    def refresh(self):
        st = self.db.get_status()
        self.lbl_active_db.config(
            text=f"Engine: {st['engine']} | {st['message']}",
            foreground=COLORS["success"] if st["is_mysql"] else COLORS["warning"]
        )

    def _test_mysql_conn(self):
        from ..database.mysql_backend import MySQLBackend
        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showerror("Validation", "Port must be a valid integer (default 3306).")
            return

        tester = MySQLBackend(
            host=self.host_var.get().strip(),
            port=port,
            user=self.user_var.get().strip(),
            password=self.pass_var.get().strip(),
            database=self.dbname_var.get().strip()
        )
        ok, msg = tester.test_connection()
        if ok:
            messagebox.showinfo("MySQL Connection Test", f"✓ SUCCESS:\n{msg}")
        else:
            messagebox.showerror("MySQL Connection Test", f"✗ FAILED:\n{msg}\n\nMake sure XAMPP is started and MySQL service is running.")

    def _save_settings(self):
        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showerror("Validation", "Port must be a valid integer.")
            return

        cfg = load_config()
        cfg["db_type"] = self.engine_var.get()
        cfg["mysql"] = {
            "host": self.host_var.get().strip(),
            "port": port,
            "user": self.user_var.get().strip(),
            "password": self.pass_var.get().strip(),
            "database": self.dbname_var.get().strip()
        }
        cfg["sqlite"] = {
            "file_path": self.sqlite_path_var.get().strip()
        }

        save_config(cfg)
        self.controller.config = cfg

        # Re-initialize DatabaseManager
        self.db.setup_backend(force_engine=cfg["db_type"])
        self.refresh()
        self.controller.update_status_bar()
        self.controller.views["dashboard"].refresh()
        messagebox.showinfo("Settings Saved", f"Settings updated!\nStatus: {self.db.status_message}")

    def _browse_sqlite_path(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Select SQLite Database Storage File Location"
        )
        if path:
            self.sqlite_path_var.set(path)

    def _create_backup(self):
        folder = filedialog.askdirectory(title="Select Destination Folder for Backup")
        if not folder:
            return
        ok, msg = self.db.backup_database(folder)
        if ok:
            messagebox.showinfo("Backup Completed", msg)
        else:
            messagebox.showerror("Backup Failed", msg)
