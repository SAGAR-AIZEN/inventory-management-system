#!/usr/bin/env python3
"""
Inventory Management System - Main Entry Point
CBSE Class 11/12 Computer Science / IP & Production-Ready Project.
"""
import sys
import os

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.views.main_window import MainWindow


def main():
    print("=" * 60)
    print("  CBSE Inventory Management System (MySQL / XAMPP Edition)")
    print(f"  Python Version: {sys.version.split()[0]} on {sys.platform}")
    print("=" * 60)

    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
    except Exception as e:
        print(f"\nFatal Error during application startup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
