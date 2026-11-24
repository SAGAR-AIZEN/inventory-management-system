import tkinter as tk
from tkinter import ttk
import sys

# Professional Color Palette
COLORS = {
    "bg_main": "#F1F5F9",          # Light grayish blue background
    "bg_card": "#FFFFFF",          # Pure white cards
    "bg_sidebar": "#0F172A",       # Deep slate navy sidebar
    "bg_sidebar_hover": "#1E293B", # Hover state for sidebar
    "bg_sidebar_active": "#2563EB",# Selected sidebar item
    "text_dark": "#0F172A",        # Main text
    "text_muted": "#64748B",       # Secondary text
    "text_light": "#FFFFFF",       # Light text for dark backgrounds
    "primary": "#2563EB",          # Primary blue accent
    "primary_hover": "#1D4ED8",    # Hover blue
    "success": "#10B981",          # Emerald green (sales, profits, in-stock)
    "warning": "#F59E0B",          # Amber warning
    "danger": "#EF4444",           # Red (low stock, delete)
    "danger_light": "#FEE2E2",     # Soft light red for alerts
    "warning_light": "#FEF3C7",    # Soft light yellow for low-stock warning
    "border": "#CBD5E1",          # Light borders
    "table_alt": "#F8FAFC",        # Alternating table row
}

# Typography
def get_font_family():
    if sys.platform == "darwin":
        return "SF Pro Text"
    elif sys.platform.startswith("win"):
        return "Segoe UI"
    else:
        return "Ubuntu"

FONT_FAMILY = get_font_family()

FONTS = {
    "title": (FONT_FAMILY, 16, "bold"),
    "subtitle": (FONT_FAMILY, 12, "bold"),
    "heading": (FONT_FAMILY, 11, "bold"),
    "body": (FONT_FAMILY, 10),
    "body_bold": (FONT_FAMILY, 10, "bold"),
    "small": (FONT_FAMILY, 9),
    "kpi_value": (FONT_FAMILY, 18, "bold"),
    "kpi_label": (FONT_FAMILY, 9, "bold"),
}


def apply_theme(root: tk.Tk):
    """Apply modern TTK styles to the entire application."""
    style = ttk.Style(root)
    
    # Try using clam or default
    try:
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=COLORS["bg_main"])

    # General Frames
    style.configure("Main.TFrame", background=COLORS["bg_main"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")
    style.configure("Sidebar.TFrame", background=COLORS["bg_sidebar"])

    # Labels
    style.configure("TLabel", background=COLORS["bg_card"], foreground=COLORS["text_dark"], font=FONTS["body"])
    style.configure("MainBg.TLabel", background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["body"])
    style.configure("Title.TLabel", background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["title"])
    style.configure("Subtitle.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_dark"], font=FONTS["subtitle"])
    style.configure("Muted.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_muted"], font=FONTS["small"])
    
    # Sidebar Labels
    style.configure("SidebarTitle.TLabel", background=COLORS["bg_sidebar"], foreground=COLORS["text_light"], font=FONTS["title"])
    style.configure("SidebarSub.TLabel", background=COLORS["bg_sidebar"], foreground="#94A3B8", font=FONTS["small"])

    # Buttons
    style.configure("Primary.TButton",
                    font=FONTS["body_bold"],
                    background=COLORS["primary"],
                    foreground=COLORS["text_light"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(12, 6))
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_hover"])],
              foreground=[("active", COLORS["text_light"])])

    style.configure("Success.TButton",
                    font=FONTS["body_bold"],
                    background=COLORS["success"],
                    foreground=COLORS["text_light"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(12, 6))
    style.map("Success.TButton",
              background=[("active", "#059669")])

    style.configure("Danger.TButton",
                    font=FONTS["body_bold"],
                    background=COLORS["danger"],
                    foreground=COLORS["text_light"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(12, 6))
    style.map("Danger.TButton",
              background=[("active", "#DC2626")])

    style.configure("Secondary.TButton",
                    font=FONTS["body"],
                    background=COLORS["bg_main"],
                    foreground=COLORS["text_dark"],
                    borderwidth=1,
                    padding=(10, 5))

    # Sidebar Navigation Buttons
    style.configure("Sidebar.TButton",
                    font=FONTS["body_bold"],
                    background=COLORS["bg_sidebar"],
                    foreground="#E2E8F0",
                    borderwidth=0,
                    anchor="w",
                    padding=(16, 10))
    style.map("Sidebar.TButton",
              background=[("active", COLORS["bg_sidebar_hover"])],
              foreground=[("active", "#FFFFFF")])

    style.configure("SidebarActive.TButton",
                    font=FONTS["body_bold"],
                    background=COLORS["bg_sidebar_active"],
                    foreground="#FFFFFF",
                    borderwidth=0,
                    anchor="w",
                    padding=(16, 10))

    # Treeview (Data Tables)
    style.configure("Treeview",
                    font=FONTS["body"],
                    rowheight=26,
                    background=COLORS["bg_card"],
                    fieldbackground=COLORS["bg_card"],
                    foreground=COLORS["text_dark"],
                    borderwidth=0)
    style.configure("Treeview.Heading",
                    font=FONTS["heading"],
                    background="#E2E8F0",
                    foreground=COLORS["text_dark"],
                    relief="flat",
                    padding=(6, 4))
    style.map("Treeview",
              background=[("selected", COLORS["primary"])],
              foreground=[("selected", "#FFFFFF")])

    # Entry and Combobox
    style.configure("TEntry", padding=5, font=FONTS["body"])
    style.configure("TCombobox", padding=4, font=FONTS["body"])

    # Scrollbars
    style.configure("Vertical.TScrollbar", gripcount=0, background=COLORS["border"])
