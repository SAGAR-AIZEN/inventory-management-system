# User & Administrator Guide
## Inventory Management System (MySQL / XAMPP Edition)

---

## 1. Quick Start Guide

### Step 1: Start XAMPP Server (Recommended for CBSE Evaluation)
1. Open the **XAMPP Control Panel** on your computer.
2. Click the **Start** button next to **Apache**.
3. Click the **Start** button next to **MySQL**.
4. Both modules should now show a green background, indicating port `80/443` (Apache) and `3306` (MySQL) are active.

> **Note**: If XAMPP is not installed or running, the application will automatically start in **SQLite mode** using local file storage without crashing.

### Step 2: Launch the Application
- On **Windows**: Double-click the `run.bat` file in the project folder, or run:
  ```powershell
  python src\main.py
  ```
- On **macOS / Linux**: Open Terminal and run:
  ```bash
  python3 src/main.py
  ```

---

## 2. Verifying Tables in phpMyAdmin
CBSE teachers and examiners often check the database backend in phpMyAdmin:
1. Open your web browser and navigate to: `http://localhost/phpmyadmin`
2. In the left navigation list, click on `inventory_db`.
3. You will see all 6 relational tables:
   - `categories`: Main Directory categories.
   - `sub_categories`: Sub Directory items.
   - `products`: Catalog items, prices, and stock numbers.
   - `purchases`: Supplier purchase orders.
   - `purchase_items`: Individual items inwarded.
   - `sales`: Customer billing transactions.
   - `sales_items`: Individual items sold with unit profit.

---

## 3. Application Feature Walkthrough

### 3.1 Dashboard Overview
- Shows real-time financial KPI cards:
  - **Total Products**: Count of unique SKUs.
  - **Total Stock Units**: Total physical items in inventory.
  - **Stock Cost Value**: Total valuation at wholesale cost.
  - **Stock Retail Value**: Total valuation at retail selling price.
  - **Potential Profit**: Difference between retail value and cost value.
  - **Low-Stock Alert Count**: Items at or below reorder threshold.
- Quick alert list displaying items that need immediate reordering.

### 3.2 Product & Directory Management
- **Directory Hierarchy**: The left panel displays your categories and subcategories in a treeview structure (`Main Directory` $\rightarrow$ `Sub Directory`).
- Click any directory to filter the products table immediately.
- Use **+ Add Main Category** or **+ Add Sub-Category** to expand your organization.
- Click **➕ Add New Product** to insert a new catalog item with SKU, unit price, stock, and reorder limit.
- Click **✏️ Edit Selected** or **🗑️ Delete Selected** to maintain records.

### 3.3 Purchase Entries (Stock Inward)
1. Go to the **Purchase Entries** tab.
2. Enter the Supplier Name and Bill / Invoice number.
3. Select an item from the product dropdown, enter the inward cost and quantity, and click **+ Add to Slip**.
4. You can add multiple items to the same purchase order.
5. Click **✓ Confirm & Inward Stock**.
   - The application automatically adds the inward quantity to the product's current stock and updates the latest cost price.

### 3.4 Sales & Billing (Stock Outward)
1. Go to the **Sales & Billing** tab.
2. Enter Customer Name and Phone number.
3. Select a product: the system displays current available stock in real time.
4. Enter selling price and quantity, then click **+ Add to Cart**.
   - *Stock Safety Check*: If the quantity exceeds available stock, the system refuses to add it, preventing negative inventory!
5. When all items are added, click **💳 Complete Sale & Generate Bill**.
   - Current stock is atomically decremented.
   - A formatted, printable invoice receipt popup appears.

### 3.5 Stock Availability & Low-Stock Alerts
- View all inventory items, their current quantities, and total cost/retail values.
- Check the **⚠️ Show Low-Stock Alerts Only** box to isolate items that have fallen below their reorder threshold.
- Highlighted in bold red/amber for rapid visual identification.
- Click **📥 Export Stock CSV** to export a complete spreadsheet for ordering.

### 3.6 Profit & Performance Reports
- Select date periods: **Today**, **Last 7 Days**, **This Month**, **All Time**, or enter a custom date range.
- Real-time financial calculations:
  - Total Revenue (Sales)
  - Cost of Goods Sold (COGS)
  - Gross Profit
  - Profit Margin ($\%$)
- Top 5 best-selling products by quantity and profit.
- Complete sales ledger with 1-click **Export CSV** and **Generate Summary Statement**.

### 3.7 Database Settings & Storage Selection
- Switch between **MySQL (XAMPP)** and **SQLite (Local File)** on the fly.
- Configure Host (`localhost`), Port (`3306`), User (`root`), Password, and Database (`inventory_db`).
- Test MySQL connection with 1-click feedback.
- Change the file location of the SQLite database to any partition or external drive.
- Create timestamped database backups with 1 click.

---

## 4. Troubleshooting Common Issues

### Issue 1: "MySQL Not Reachable / Fallback to SQLite"
- **Reason**: The MySQL service in XAMPP is not started.
- **Solution**: Open the XAMPP Control Panel and click **Start** next to MySQL.

### Issue 2: "Port 3306 is in use by another program"
- **Reason**: Another instance of MySQL Server or MariaDB is already running.
- **Solution**: In XAMPP, click **Config** on MySQL, change the port to `3307`, and update port `3307` in this application's **Settings** tab.

### Issue 3: "Access Denied for user 'root'@'localhost'"
- **Reason**: Your local MySQL server has a root password set.
- **Solution**: Open the **Settings** tab in the application, enter your MySQL root password, and click **Save & Reconnect**.
