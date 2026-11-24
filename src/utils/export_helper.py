import csv
import os
from datetime import datetime


def export_to_csv(filepath: str, headers: list, rows: list) -> bool:
    """Export tabular headers and rows to a CSV file."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return True
    except Exception as e:
        print(f"CSV Export Error: {e}")
        return False


def generate_sales_receipt(invoice_no: str, customer_name: str, customer_phone: str,
                           items: list, total_amount: float, currency: str = "₹") -> str:
    """Generate a clean formatted plain-text sales invoice / receipt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    divider = "=" * 48
    sub_divider = "-" * 48

    total_formatted = f"{currency}{total_amount:.2f}"

    lines = [
        divider,
        "             INVENTORY SALES INVOICE",
        divider,
        f"Invoice No : {invoice_no}",
        f"Date/Time  : {now}",
        f"Customer   : {customer_name or 'Walk-in Customer'}",
        f"Phone      : {customer_phone or 'N/A'}",
        sub_divider,
        f"{'Item':<22} {'Qty':>5} {'Price':>8} {'Total':>9}",
        sub_divider,
    ]

    for item in items:
        # item: (name, qty, unit_price, subtotal)
        name = str(item[0])[:20]
        qty = item[1]
        price = f"{currency}{item[2]:.2f}"
        sub = f"{currency}{item[3]:.2f}"
        lines.append(f"{name:<22} {qty:>5} {price:>8} {sub:>9}")

    lines.extend([
        sub_divider,
        f"{'TOTAL PAYABLE:':<28} {total_formatted:>18}",
        divider,
        "         Thank you for your business!",
        divider
    ])

    return "\n".join(lines)


def generate_profit_report_text(report_data: dict, start_date: str, end_date: str, currency: str = "₹") -> str:
    """Generate a structured text summary for profit analysis."""
    divider = "=" * 54
    sub_divider = "-" * 54

    rev_str = f"{currency}{report_data.get('total_revenue', 0.0):.2f}"
    cogs_str = f"{currency}{report_data.get('total_cost', 0.0):.2f}"
    profit_str = f"{currency}{report_data.get('total_profit', 0.0):.2f}"
    margin_str = f"{report_data.get('margin_percentage', 0.0):.2f}%"
    tx_str = str(report_data.get('total_transactions', 0))
    items_str = str(report_data.get('total_items_sold', 0))

    lines = [
        divider,
        "         INVENTORY PROFIT & LOSS PERFORMANCE REPORT",
        divider,
        f"Period        : {start_date} to {end_date}",
        f"Generated At  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        sub_divider,
        f"{'Total Revenue (Sales)':<34}: {rev_str:>16}",
        f"{'Total Cost of Goods Sold (COGS)':<34}: {cogs_str:>16}",
        f"{'Gross Profit':<34}: {profit_str:>16}",
        f"{'Profit Margin':<34}: {margin_str:>16}",
        f"{'Total Sales Transactions':<34}: {tx_str:>16}",
        f"{'Total Items Sold':<34}: {items_str:>16}",
        divider,
        "TOP SELLING PRODUCTS IN THIS PERIOD:",
        sub_divider,
        f"{'Product Name':<28} {'Qty Sold':>10} {'Profit':>12}",
        sub_divider,
    ]

    for prod in report_data.get("top_products", []):
        name = str(prod.get("name", "Unknown"))[:26]
        qty = prod.get("qty", 0)
        prof = f"{currency}{prod.get('profit', 0.0):.2f}"
        lines.append(f"{name:<28} {qty:>10} {prof:>12}")

    lines.append(divider)
    return "\n".join(lines)
