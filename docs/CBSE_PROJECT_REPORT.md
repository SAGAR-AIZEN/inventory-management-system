# CBSE SENIOR SECONDARY SCHOOL PROJECT REPORT
## Subject: Computer Science / Informatics Practices (Code 083 / 065)
### Academic Year: 2026 – 2027

---

# INVENTORY MANAGEMENT SYSTEM
### With Local SQL Database Integration (MySQL / XAMPP & SQLite)

---

## TABLE OF CONTENTS
1. Certificate of Authenticity
2. Acknowledgements
3. Project Synopsis & Objectives
4. System Hardware & Software Specifications
5. Relational Database Architecture & ER Diagram
6. Relational Table Schemas & Data Dictionary
7. SQL DDL & DML Statements Used in the Project
8. Python Source Code Architecture & Design Patterns
9. Core Functional Modules & Business Logic
10. System Testing & Verification Report
11. Viva Voce Questions & Model Answers for CBSE Practical Exam
12. Bibliography & References

---

## 1. CERTIFICATE OF AUTHENTICITY

This is to certify that this project entitled **"INVENTORY MANAGEMENT SYSTEM"** has been successfully designed, developed, and tested under the guidance and supervision of the Computer Science faculty in partial fulfillment of the requirements for the **All India Senior School Certificate Examination (AISSCE) - Class XII** conducted by the **Central Board of Secondary Education (CBSE), New Delhi**.

- **Student Name**: __________________________
- **Roll Number**: ___________________________
- **Class / Section**: Class XII - Science / Commerce
- **School**: ________________________________

```
________________________                      ________________________
Internal Examiner Signature                    External Examiner Signature
```

---

## 2. ACKNOWLEDGEMENTS

I express my heartfelt gratitude to my Computer Science Teacher and the Principal of our school for providing their valuable guidance, constant encouragement, and laboratory facilities to complete this software project. 

I am also thankful to CBSE for introducing Python and Relational Database Systems into the curriculum, which enabled us to solve real-world automation problems using modular programming.

---

## 3. PROJECT SYNOPSIS & OBJECTIVES

### 3.1 Background & Purpose
In traditional retail and school supply stores, inventory tracking, purchase recording, customer billing, and stock reordering are manually maintained on paper ledgers. This manual approach suffers from human errors, misplaced records, lack of real-time stock visibility, unnoticed low-stock situations, and difficult profit/loss calculations.

The **Inventory Management System** is a production-ready desktop application developed in Python with a responsive Tkinter GUI and a local relational SQL database. It was designed to run smoothly on standard school lab systems with minimal hardware requirements while complying with CBSE Class 11 & 12 Computer Science practical guidelines.

### 3.2 Key Objectives
1. **Directory-wise Categorization**: Hierarchical structure with Main Categories (Main Directory) $\rightarrow$ Sub-Categories (Sub Directory) $\rightarrow$ Products.
2. **Product Catalog Management**: Full CRUD operations (Add, Edit, Delete, Search) with SKU/Barcode, unit prices, and reorder limits.
3. **Purchase (Stock Inward) Processing**: Inward invoice generation, stock incrementing, and supplier history.
4. **Sales (Stock Outward) & POS Billing**: Point-of-Sale checkout with real-time stock deduction, inventory validation, and receipt generation.
5. **Real-time Stock Availability**: Instant stock count, valuation at cost price vs. retail price.
6. **Low-Stock Alert Mechanism**: Visual color-coded alerts (red/amber) and automated reorder triggers when stock drops below threshold.
7. **Profit & Performance Analytics**: Automatic calculation of Revenue, Cost of Goods Sold (COGS), Gross Profit, Profit Margins ($\%$) and bestsellers over selectable date ranges.
8. **Dual SQL Engine**: Primary target on **MySQL (via XAMPP)** for evaluator inspection in **phpMyAdmin**, with automatic fail-safe fallback to **SQLite**.

---

## 4. SYSTEM SPECIFICATIONS & HARDWARE COMPATIBILITY

### 4.1 Minimal Hardware Requirements
- **Processor**: Intel Core i5 (3rd Generation or newer) / AMD Athlon / Ryzen / FX series.
- **RAM**: Minimum 512 MB available RAM (Application uses only ~25 MB – 40 MB; MySQL in XAMPP uses ~50 MB).
- **RAM Type**: DDR3 or DDR4 RAM supported.
- **Graphics**: No Dedicated GPU required (100% CPU-rendered native OS widgets).
- **Disk Storage**: Application source < 20 MB; configurable database location.
- **Architecture**: 32-bit (x86), 64-bit (x86_64), and ARM64.

### 4.2 Software Environment
- **Operating System**: Windows 7/8/10/11, macOS (Intel & Apple Silicon), Linux.
- **Programming Language**: Python 3.8+ (Tested on Python 3.15).
- **GUI Toolkit**: Tkinter / TTK (Built-in standard library).
- **Database Server**: XAMPP (Apache + MySQL / MariaDB) running at `localhost:3306`.
- **Database Driver**: `mysql-connector-python` (CBSE curriculum standard).
- **Offline Fallback Engine**: `sqlite3` (Built-in standard library).

---

## 5. RELATIONAL DATABASE ARCHITECTURE & ER DIAGRAM

```
+------------------+         1:N         +----------------------+
|    CATEGORIES    |-------------------->|    SUB_CATEGORIES    |
| (Main Directory) |                     |   (Sub Directory)    |
+------------------+                     +----------------------+
                                                    | 1:N
                                                    v
+------------------+         1:N         +----------------------+
|    PURCHASES     |-------------------->|       PRODUCTS       |
+------------------+                     |    (Catalog Items)   |
        | 1:N                            +----------------------+
        v                                           | 1:N
+------------------+                                v
|  PURCHASE_ITEMS  |                     +----------------------+
+------------------+                     |     SALES_ITEMS      |
                                         +----------------------+
                                                    ^
                                                    | 1:N
                                         +----------------------+
                                         |        SALES         |
                                         |    (Billing Invoices)|
                                         +----------------------+
```

### Key Relationships
- **Categories to Sub-Categories (1:N)**: One Main Directory contains multiple Sub-Directories (`ON DELETE CASCADE`).
- **Sub-Categories to Products (1:N)**: One Sub-Directory contains multiple products (`ON DELETE RESTRICT`).
- **Purchases to Purchase Items (1:N)**: One inward purchase order details multiple item rows.
- **Sales to Sales Items (1:N)**: One customer invoice details multiple sold item rows.
- **Products to Items (1:N)**: Each item row references a specific product by `product_id`.

---

## 6. RELATIONAL TABLE SCHEMAS & DATA DICTIONARY

### Table 1: `categories`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Unique category identifier |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | Main Directory / Category Name |
| `description`| TEXT | NULL | Details about category |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### Table 2: `sub_categories`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Unique subcategory identifier |
| `category_id`| INT | FOREIGN KEY (categories.id) | Parent category directory |
| `name` | VARCHAR(100) | NOT NULL | Sub-Directory Name |
| `description`| TEXT | NULL | Description |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### Table 3: `products`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Unique product ID |
| `sku` | VARCHAR(50) | UNIQUE, NOT NULL | Barcode / SKU Code |
| `name` | VARCHAR(150) | NOT NULL | Product Title / Description |
| `subcategory_id`| INT | FOREIGN KEY (sub_categories.id)| Sub-Directory reference |
| `unit` | VARCHAR(20) | DEFAULT 'Pcs' | Measurement Unit (Pcs, Box, Kg) |
| `cost_price` | DECIMAL(10,2) | NOT NULL, DEFAULT 0.00 | Wholesale / Purchase cost |
| `selling_price`| DECIMAL(10,2)| NOT NULL, DEFAULT 0.00 | Retail selling price |
| `current_stock`| INT | NOT NULL, DEFAULT 0 | Current in-hand inventory |
| `low_stock_threshold`| INT | NOT NULL, DEFAULT 5 | Minimum threshold for alerts |

### Table 4: `purchases`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Purchase transaction ID |
| `invoice_no` | VARCHAR(50) | UNIQUE, NOT NULL | Supplier bill / Invoice number |
| `supplier_name`| VARCHAR(150)| NOT NULL | Supplier / Vendor name |
| `purchase_date`| DATE | NOT NULL | Date of inward purchase |
| `total_amount`| DECIMAL(10,2)| DEFAULT 0.00 | Total invoice amount |
| `notes` | TEXT | NULL | Inward remarks |

### Table 5: `purchase_items`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Line item ID |
| `purchase_id`| INT | FOREIGN KEY (purchases.id) | Parent purchase reference |
| `product_id` | INT | FOREIGN KEY (products.id) | Product reference |
| `quantity` | INT | NOT NULL | Quantity inwarded |
| `unit_cost` | DECIMAL(10,2) | NOT NULL | Unit purchase price |
| `subtotal` | DECIMAL(10,2) | NOT NULL | `quantity * unit_cost` |

### Table 6: `sales`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Sale transaction ID |
| `invoice_no` | VARCHAR(50) | UNIQUE, NOT NULL | Customer receipt number |
| `customer_name`| VARCHAR(150)| DEFAULT 'Walk-in' | Customer name |
| `customer_phone`| VARCHAR(20) | NULL | Customer contact number |
| `sale_date` | DATE | NOT NULL | Date of sale |
| `total_amount`| DECIMAL(10,2)| DEFAULT 0.00 | Total bill amount |
| `total_profit`| DECIMAL(10,2)| DEFAULT 0.00 | Net profit earned |

### Table 7: `sales_items`
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT / INTEGER | PRIMARY KEY AUTO_INCREMENT | Sold line item ID |
| `sale_id` | INT | FOREIGN KEY (sales.id) | Parent sales invoice reference |
| `product_id` | INT | FOREIGN KEY (products.id) | Product reference |
| `quantity` | INT | NOT NULL | Units sold |
| `unit_price` | DECIMAL(10,2) | NOT NULL | Selling price per unit |
| `unit_cost` | DECIMAL(10,2) | NOT NULL | Cost price per unit |
| `profit` | DECIMAL(10,2) | NOT NULL | `(unit_price - unit_cost) * quantity` |
| `subtotal` | DECIMAL(10,2) | NOT NULL | `quantity * unit_price` |

---

## 7. SQL DDL & DML STATEMENTS USED

### 7.1 Database & Table Creation (DDL)
```sql
CREATE DATABASE IF NOT EXISTS inventory_db CHARACTER SET utf8mb4;
USE inventory_db;

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE sub_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    subcategory_id INT NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'Pcs',
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    selling_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    current_stock INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 5,
    FOREIGN KEY (subcategory_id) REFERENCES sub_categories(id)
) ENGINE=InnoDB;
```

### 7.2 Core DML Queries Used in Application
```sql
-- 1. Querying Products with Directory Hierarchy & Search
SELECT p.id, p.sku, p.name, p.current_stock, p.low_stock_threshold,
       c.name AS category_name, s.name AS subcategory_name
FROM products p
JOIN sub_categories s ON p.subcategory_id = s.id
JOIN categories c ON s.category_id = c.id
WHERE p.name LIKE '%Notebook%' OR p.sku LIKE '%Notebook%';

-- 2. Low-Stock Query
SELECT name, current_stock, low_stock_threshold
FROM products
WHERE current_stock <= low_stock_threshold;

-- 3. Stock Inward Increment (Atomic Purchase)
UPDATE products 
SET current_stock = current_stock + 10, cost_price = 55.00 
WHERE id = 1;

-- 4. Stock Outward Decrement (Atomic Sale)
UPDATE products 
SET current_stock = current_stock - 2 
WHERE id = 1;

-- 5. Profit Calculation Query for Selected Date Range
SELECT 
    SUM(total_amount) AS total_revenue,
    SUM(total_profit) AS total_profit,
    (SUM(total_amount) - SUM(total_profit)) AS total_cost,
    (SUM(total_profit) / SUM(total_amount) * 100) AS margin_percentage
FROM sales
WHERE sale_date BETWEEN '2026-11-01' AND '2026-11-30';
```

---

## 8. PYTHON SOURCE CODE ARCHITECTURE

The application follows the **Model-View-Controller (MVC)** architectural pattern:
- **`src/database/`**: Contains database drivers (`mysql_backend.py`, `sqlite_backend.py`), database manager (`db_manager.py`), and schemas (`schema.py`).
- **`src/models/`**: Domain entity dataclasses (`Product`, `Category`, `Purchase`, `Sale`).
- **`src/views/`**: Tkinter UI presentation modules:
  - `dashboard_view.py`: Summary KPI cards and quick alert list.
  - `product_view.py`: Directory tree and product catalog CRUD.
  - `purchase_view.py`: Inward stock slips and supplier ledger.
  - `sales_view.py`: POS billing and stock decrementing checkout.
  - `stock_view.py`: Stock valuation and low-stock highlighting.
  - `reports_view.py`: Profit/loss analytics and CSV exporter.
  - `settings_view.py`: MySQL/XAMPP connection manager.
- **`src/utils/`**: Theme configuration (`theme.py`), JSON settings (`config.py`), and report formatters (`export_helper.py`).

---

## 9. VIVA VOCE QUESTIONS & MODEL ANSWERS (CBSE EXAM PREPARATION)

### Q1: What is the purpose of this project?
> **Answer**: To automate inventory tracking in a retail or school environment by recording stock purchases, sales transactions, calculating real-time profit and stock valuation, highlighting low-stock items for reordering, and maintaining records in a relational SQL database.

### Q2: Why did you choose MySQL and XAMPP?
> **Answer**: MySQL is an enterprise-grade, ACID-compliant Relational Database Management System (RDBMS). XAMPP provides an integrated local server environment bundled with phpMyAdmin, allowing teachers and evaluators to inspect database tables, primary keys, foreign keys, and live records in a browser.

### Q3: How do you connect Python to MySQL?
> **Answer**: Using the official Oracle driver `mysql-connector-python`. We establish a connection via `mysql.connector.connect(host='localhost', user='root', password='', database='inventory_db')` and execute parameterized queries using a database cursor.

### Q4: How is stock integrity maintained during sales?
> **Answer**: Before recording a sale, the system checks whether `current_stock >= requested_quantity`. If stock is insufficient, it raises a validation error preventing overselling. Upon confirmation, it executes an atomic transaction that decrements stock and inserts the line item.

### Q5: How is profit calculated in the reports module?
> **Answer**:
> - For each sold line item: $\text{Item Profit} = (\text{Selling Price} - \text{Cost Price}) \times \text{Quantity Sold}$.
> - Total Revenue $= \sum \text{Subtotals}$.
> - Net Profit $= \sum \text{Item Profits}$.
> - Profit Margin $(\%) = \left(\frac{\text{Net Profit}}{\text{Total Revenue}}\right) \times 100$.

### Q6: What happens if XAMPP is turned off or not installed on a system?
> **Answer**: The application includes an intelligent fallback mechanism. If the MySQL server actively refuses connection, it catches the error and switches to the built-in Python `sqlite3` engine using a local database file (`data/inventory.db`). This ensures the software never crashes during examination.

### Q7: Why is Tkinter preferred over frameworks like Electron or PyQt for this project?
> **Answer**: Tkinter is built directly into Python and uses native operating system graphics APIs. It consumes only ~25 MB to 40 MB of RAM, requires no GPU acceleration, and runs smoothly on legacy hardware (e.g. 512 MB RAM, Intel Core i5 3rd Gen) across Windows, macOS, and Linux.

---

## 10. BIBLIOGRAPHY & REFERENCES
1. CBSE Computer Science Class XII Textbook (Sumita Arora / Preeti Arora).
2. Python Official Documentation: https://docs.python.org/3/library/tkinter.html
3. MySQL Connector/Python Developer Guide: https://dev.mysql.com/doc/connector-python/en/
4. SQLite Official Documentation: https://www.sqlite.org/
