"""
Data models representing Domain Entities in the Inventory System.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: Optional[int]
    name: str
    description: str = ""


@dataclass
class SubCategory:
    id: Optional[int]
    category_id: int
    name: str
    description: str = ""
    category_name: str = ""


@dataclass
class Product:
    id: Optional[int]
    sku: str
    name: str
    subcategory_id: int
    unit: str = "Pcs"
    cost_price: float = 0.0
    selling_price: float = 0.0
    current_stock: int = 0
    low_stock_threshold: int = 5
    subcategory_name: str = ""
    category_name: str = ""

    @property
    def is_low_stock(self) -> bool:
        return self.current_stock <= self.low_stock_threshold

    @property
    def stock_cost_value(self) -> float:
        return self.current_stock * self.cost_price

    @property
    def stock_retail_value(self) -> float:
        return self.current_stock * self.selling_price
