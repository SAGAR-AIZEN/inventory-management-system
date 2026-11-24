"""
Transaction models for Purchases and Sales.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PurchaseItem:
    product_id: int
    product_name: str
    quantity: int
    unit_cost: float
    subtotal: float = 0.0

    def __post_init__(self):
        if not self.subtotal:
            self.subtotal = self.quantity * self.unit_cost


@dataclass
class Purchase:
    id: Optional[int]
    invoice_no: str
    supplier_name: str
    purchase_date: str
    total_amount: float
    notes: str = ""
    items: List[PurchaseItem] = field(default_factory=list)


@dataclass
class SaleItem:
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    unit_cost: float
    subtotal: float = 0.0
    profit: float = 0.0

    def __post_init__(self):
        if not self.subtotal:
            self.subtotal = self.quantity * self.unit_price
        if not self.profit:
            self.profit = (self.unit_price - self.unit_cost) * self.quantity


@dataclass
class Sale:
    id: Optional[int]
    invoice_no: str
    customer_name: str
    customer_phone: str
    sale_date: str
    total_amount: float
    total_profit: float
    notes: str = ""
    items: List[SaleItem] = field(default_factory=list)
