import tkinter as tk
from tkinter import ttk
from datetime import datetime

from ..utils.config import load_config
from ..utils.theme import apply_theme, COLORS, FONTS
from ..database.db_manager import DatabaseManager

from .dashboard_view import DashboardView
from .product_view import ProductView
from .purchase_view import PurchaseView
from .sales_view import SalesView
from .stock_view import StockView
from .reports_view import ReportsView
from .settings_view import SettingsView


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.config = load_config()
        self.db = DatabaseManager.get_instance()

        self.title("Inventory Management System | CBSE CS/IP & Production Edition")
        self.geometry("1240x760")
        self.minsize(1050, 620)

        # Apply styling
        apply_theme(self)

        self.views = {}
        self.nav_buttons = {}
        self.current_view_name = None

        self._build_layout()
        self.show_view("dashboard")

    def _build_layout(self):
        # 1. Left Sidebar
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand / Header
        brand_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame", padding=(16, 20, 16, 16))
        brand_frame.pack(fill="x")

        ttk.Label(brand_frame, text="📦 INVENTORY", style="SidebarTitle.TLabel").pack(anchor="w")
        ttk.Label(brand_frame, text="CBSE School & Production Edition", style="SidebarSub.TLabel").pack(anchor="w", pady=(2, 0))

        # Divider
        div = tk.Frame(self.sidebar, bg="#1E293B", height=1)
        div.pack(fill="x", padx=14, pady=10)

        # Navigation Buttons
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("product", "📁  Directory & Products"),
            ("purchase", "📥  Purchase Entries"),
            ("sales", "🛒  Sales & Billing"),
            ("stock", "📋  Stock & Alerts"),
            ("reports", "📈  Profit & Reports"),
            ("settings", "⚙️  Database & Settings"),
        ]

        nav_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame", padding=(8, 0))
        nav_frame.pack(fill="x")

        for key, text in nav_items:
            btn = ttk.Button(
                nav_frame,
                text=text,
                style="Sidebar.TButton",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # Bottom System Info in Sidebar
        bot_sidebar = ttk.Frame(self.sidebar, style="Sidebar.TFrame", padding=14)
        bot_sidebar.pack(side="bottom", fill="x")

        ttk.Label(bot_sidebar, text="Active Database:", style="SidebarSub.TLabel").pack(anchor="w")
        self.lbl_sidebar_db = ttk.Label(bot_sidebar, text="Detecting...", font=FONTS["small"],
                                        background=COLORS["bg_sidebar"], foreground="#38BDF8")
        self.lbl_sidebar_db.pack(anchor="w", pady=(2, 6))

        ttk.Label(bot_sidebar, text="CBSE Project: Python + MySQL", font=FONTS["small"],
                  background=COLORS["bg_sidebar"], foreground="#94A3B8").pack(anchor="w")

        # 2. Right Content Area
        self.content_area = ttk.Frame(self, style="Main.TFrame")
        self.content_area.pack(side="right", fill="both", expand=True)

        # Bottom Status Bar
        self.status_bar = tk.Frame(self, bg="#E2E8F0", height=24, padx=12)
        self.status_bar.pack(side="bottom", fill="x")

        self.status_left = tk.Label(self.status_bar, text="Ready", font=FONTS["small"], bg="#E2E8F0", fg="#475569")
        self.status_left.pack(side="left")

        self.status_right = tk.Label(self.status_bar, text="", font=FONTS["small"], bg="#E2E8F0", fg="#475569")
        self.status_right.pack(side="right")

        self.update_status_bar()

        # Initialize View Frames
        self.views["dashboard"] = DashboardView(self.content_area, self)
        self.views["product"] = ProductView(self.content_area, self)
        self.views["purchase"] = PurchaseView(self.content_area, self)
        self.views["sales"] = SalesView(self.content_area, self)
        self.views["stock"] = StockView(self.content_area, self)
        self.views["reports"] = ReportsView(self.content_area, self)
        self.views["settings"] = SettingsView(self.content_area, self)

    def show_view(self, view_name: str):
        """Switch active view and update sidebar button highlights."""
        if view_name not in self.views:
            return

        # Update button styles
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.configure(style="SidebarActive.TButton")
            else:
                btn.configure(style="Sidebar.TButton")

        # Hide current view
        if self.current_view_name and self.current_view_name in self.views:
            self.views[self.current_view_name].pack_forget()

        # Show target view
        target_view = self.views[view_name]
        target_view.pack(fill="both", expand=True)
        self.current_view_name = view_name

        # Trigger refresh if view supports it
        if hasattr(target_view, "refresh"):
            target_view.refresh()

        self.update_status_bar()

    def update_status_bar(self):
        st = self.db.get_status()
        eng = st["engine"]
        msg = st["message"]

        self.status_left.config(text=f"Database: {eng} | {msg}")
        self.status_right.config(text=f"System Date: {datetime.now().strftime('%Y-%m-%d')} | Memory: < 50MB RAM")

        short_db = "MySQL (XAMPP)" if st["is_mysql"] else "SQLite Local"
        self.lbl_sidebar_db.config(
            text=short_db,
            foreground="#34D399" if st["is_mysql"] else "#FBBF24"
        )
