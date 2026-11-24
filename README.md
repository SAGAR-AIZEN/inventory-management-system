# High-Performance Inventory Management System
### CBSE Computer Science / IP Class 12 & Open-Source Production Edition

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Database-MySQL](https://img.shields.io/badge/Database-MySQL%20%2F%20XAMPP-orange.svg)](https://www.apachefriends.org/)
[![Database-SQLite](https://img.shields.io/badge/Fallback-SQLite3-brightgreen.svg)](https://www.sqlite.org/)
[![UI-Tkinter](https://img.shields.io/badge/UI-Tkinter%20%2F%20TTK-teal.svg)](https://docs.python.org/3/library/tkinter.html)
[![RAM Usage](https://img.shields.io/badge/RAM%20Footprint-%3C%2050MB-success.svg)](#hardware-footprint)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An ultra-lightweight, cross-platform Inventory Management System engineered in pure Python with a responsive Tkinter GUI and dual local SQL database support (**MySQL via XAMPP** as primary for CBSE evaluation, and **SQLite** as resilient offline fallback).

---

## 🌟 Key Features

1. **Directory-wise Organization**:
   - Hierarchical structure: **Main Directory (Category)** $\rightarrow$ **Sub Directory (Sub-Category)** $\rightarrow$ **Products**.
   - Interactive navigation tree for instantaneous catalog filtering.

2. **Five Core Functional Pillars**:
   - **Product Management**: Full CRUD with SKU, auto-validation, unit prices, stock, and reorder limits.
   - **Purchase Entries (Stock Inward)**: Inward supplier billing with automatic stock increments.
   - **Sales Entries (Stock Outward)**: POS billing with real-time stock safety validation (prevents overselling) and automatic profit calculation.
   - **Stock Availability & Low-Stock Alerts**: Real-time inventory table with dynamic search, valuation metrics, and visual color-coded warnings (amber/red) for items below reorder thresholds.
   - **Profit & Performance Reports**: Financial metrics (Revenue, COGS, Gross Profit, Profit Margin $\%$), top-selling products, and 1-click CSV/text summary exports.

3. **Database Architecture**:
   - **MySQL / XAMPP (Primary Target)**: Connects to `localhost:3306`, automatically provisions `inventory_db` and tables viewable in **phpMyAdmin**.
   - **SQLite (Fallback Engine)**: Seamless offline operation with zero setup if XAMPP is offline.
   - **User Configurable Storage**: Users can change database file paths and external drive targets in Settings.

---

## 💻 Hardware & System Footprint

Designed specifically to run smoothly on budget and legacy computer lab systems:
- **RAM Consumption**: $< 50\text{ MB}$ for Python, $< 60\text{ MB}$ for MySQL/MariaDB in XAMPP (Total $< 110\text{ MB}$, easily fitting a $512\text{ MB}$ RAM environment).
- **CPU**: Efficient event-driven architecture running smoothly on Intel Core i5 3rd Gen or AMD DDR3 machines.
- **GPU**: 0% GPU usage (100% native CPU OS widget rendering).
- **Disk Footprint**: $< 20\text{ MB}$ for the software source.
- **Supported Architectures**: Windows, macOS, and Linux across ARM64, x86_64, and 32-bit x86.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.8 or higher.
- (Optional, recommended for CBSE evaluation): [XAMPP](https://www.apachefriends.org/) running Apache & MySQL on port 3306.

### 2. Installation
Clone or extract the repository, then install the MySQL connector:
```bash
pip install -r requirements.txt
```

### 3. Launching
- **Windows**: Double-click `run.bat` or run:
  ```powershell
  python src\main.py
  ```
- **macOS / Linux**:
  ```bash
  python3 src/main.py
  ```

---

## 🧪 Running Automated Tests
Run the comprehensive test suite verifying database transactions, stock integrity, and export helpers:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📂 Project Structure
```
├── src/
│   ├── main.py                     # Application entry point
│   ├── database/
│   │   ├── db_manager.py           # Unified database interface & fallback
│   │   ├── mysql_backend.py        # MySQL / XAMPP connector (mysql.connector)
│   │   ├── sqlite_backend.py       # SQLite engine (local fallback)
│   │   └── schema.py               # Relational DDL schemas and seed data
│   ├── models/
│   │   ├── product.py              # Product and Category domain models
│   │   └── transaction.py          # Purchase and Sales transaction models
│   ├── views/
│   │   ├── main_window.py          # Master window with responsive sidebar
│   │   ├── dashboard_view.py       # KPI metrics & quick alert cards
│   │   ├── product_view.py         # Directory tree & product CRUD
│   │   ├── purchase_view.py        # Stock inward purchases
│   │   ├── sales_view.py           # POS billing & stock outward
│   │   ├── stock_view.py           # Stock availability & low-stock alerts
│   │   ├── reports_view.py         # Profit analytics & date filtering
│   │   └── settings_view.py        # Database engine switch & XAMPP config
│   └── utils/
│       ├── theme.py                # Modern TTK styling & color palette
│       ├── config.py               # JSON configuration manager
│       └── export_helper.py        # CSV & plain-text report formatters
├── docs/
│   ├── CBSE_PROJECT_REPORT.md      # Full CBSE-format project report with viva Q&A
│   └── USER_GUIDE.md               # User & XAMPP guide for school labs
├── tests/
│   └── test_inventory.py          # Automated verification test suite
├── requirements.txt                # Python package requirements
├── run.bat                         # 1-click Windows launcher
└── README.md                       # Open-source documentation
```

---

## 📄 Documentation for CBSE Submissions
- **[CBSE Project Report](docs/CBSE_PROJECT_REPORT.md)**: Ready-to-print project documentation with Certificate, Acknowledgement, ER diagrams, DDL/DML queries, and Viva Voce preparation.
- **[User Guide](docs/USER_GUIDE.md)**: Administrator setup and phpMyAdmin verification instructions.
