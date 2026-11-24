"""
Database Schema Definitions for MySQL and SQLite.
Contains table creation DDL and initial sample seeds for CBSE project demonstrations.
"""

# MySQL DDL (for XAMPP MariaDB/MySQL)
MYSQL_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS sub_categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
        UNIQUE KEY uq_cat_subcat (category_id, name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sku VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(150) NOT NULL,
        subcategory_id INT NOT NULL,
        unit VARCHAR(20) NOT NULL DEFAULT 'Pcs',
        cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        selling_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        current_stock INT NOT NULL DEFAULT 0,
        low_stock_threshold INT NOT NULL DEFAULT 5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (subcategory_id) REFERENCES sub_categories(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS purchases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        invoice_no VARCHAR(50) NOT NULL UNIQUE,
        supplier_name VARCHAR(150) NOT NULL,
        purchase_date DATE NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS purchase_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        purchase_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_cost DECIMAL(10, 2) NOT NULL,
        subtotal DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        invoice_no VARCHAR(50) NOT NULL UNIQUE,
        customer_name VARCHAR(150),
        customer_phone VARCHAR(20),
        sale_date DATE NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        total_profit DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS sales_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sale_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        unit_cost DECIMAL(10, 2) NOT NULL,
        profit DECIMAL(10, 2) NOT NULL,
        subtotal DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]

# SQLite DDL (for local standalone fallback)
SQLITE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sub_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
        UNIQUE(category_id, name)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        subcategory_id INTEGER NOT NULL,
        unit TEXT NOT NULL DEFAULT 'Pcs',
        cost_price REAL NOT NULL DEFAULT 0.00,
        selling_price REAL NOT NULL DEFAULT 0.00,
        current_stock INTEGER NOT NULL DEFAULT 0,
        low_stock_threshold INTEGER NOT NULL DEFAULT 5,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subcategory_id) REFERENCES sub_categories(id) ON DELETE RESTRICT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT NOT NULL UNIQUE,
        supplier_name TEXT NOT NULL,
        purchase_date TEXT NOT NULL,
        total_amount REAL NOT NULL DEFAULT 0.00,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS purchase_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_cost REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT NOT NULL UNIQUE,
        customer_name TEXT,
        customer_phone TEXT,
        sale_date TEXT NOT NULL,
        total_amount REAL NOT NULL DEFAULT 0.00,
        total_profit REAL NOT NULL DEFAULT 0.00,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sales_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        unit_cost REAL NOT NULL,
        profit REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    );
    """
]

# Initial Seed Data for immediate test & CBSE demonstration
SEED_CATEGORIES = [
    ("Stationery", "School and office writing and paper supplies"),
    ("Electronics", "Computer peripherals, devices, and accessories"),
    ("Books & Guides", "Textbooks, reference materials, and workbooks"),
    ("Uniform & Sports", "School uniforms, sports gear, and equipment")
]

SEED_SUBCATEGORIES = [
    # (Category Name, SubCategory Name, Description)
    ("Stationery", "Notebooks & Registers", "Ruled and plain notebooks"),
    ("Stationery", "Writing Instruments", "Pens, pencils, markers, and highlighters"),
    ("Electronics", "Peripherals", "Keyboards, mice, USB drives"),
    ("Electronics", "Cables & Adapters", "HDMI, USB-C, power cables"),
    ("Books & Guides", "Class 12 Materials", "Computer Science, Math, Physics"),
    ("Uniform & Sports", "Games Equipment", "Footballs, cricket kits, badminton rackets")
]

SEED_PRODUCTS = [
    # (SKU, Name, CategoryName, SubcategoryName, Unit, CostPrice, SellingPrice, Stock, LowStockLimit)
    ("STA-NB-001", "A4 Spiral Notebook 200 Pgs", "Stationery", "Notebooks & Registers", "Pcs", 60.00, 95.00, 25, 10),
    ("STA-PEN-002", "Gel Pen 0.5mm Blue (Pack of 10)", "Stationery", "Writing Instruments", "Pack", 80.00, 120.00, 4, 8),  # Low Stock!
    ("ELE-KB-101", "USB Wired Multimedia Keyboard", "Electronics", "Peripherals", "Pcs", 350.00, 599.00, 12, 5),
    ("ELE-MOU-102", "Optical USB Mouse", "Electronics", "Peripherals", "Pcs", 180.00, 320.00, 3, 5),  # Low Stock!
    ("ELE-USB-103", "32GB High Speed Flash Drive", "Electronics", "Peripherals", "Pcs", 240.00, 450.00, 15, 6),
    ("BOK-CS-120", "CBSE Class 12 CS Guide", "Books & Guides", "Class 12 Materials", "Book", 400.00, 650.00, 8, 4),
    ("SPT-FB-301", "Size 5 Football Pro League", "Uniform & Sports", "Games Equipment", "Pcs", 450.00, 750.00, 2, 5)   # Low Stock!
]
