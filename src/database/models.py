"""Typed records mapped from the source CSV files."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Category:
    category_id: int
    name: str
    description: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Category":
        return cls(int(row["category_id"]), row["name"], row["description"])


@dataclass(frozen=True)
class Product:
    product_id: int
    price_brl: Decimal
    name: str
    category_id: int
    description: str
    stock_quantity: int
    status: str
    specs: str
    created_at: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Product":
        return cls(
            product_id=int(row["product_id"]),
            price_brl=Decimal(row["price_brl"]),
            name=row["name"],
            category_id=int(row["category_id"]),
            description=row["description"],
            stock_quantity=int(row["stock_quantity"]),
            status=row["status"],
            specs=row["specs"],
            created_at=row["created_at"],
        )


@dataclass(frozen=True)
class Customer:
    customer_id: int
    name: str
    phone: str
    email: str
    city: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Customer":
        return cls(int(row["customer_id"]), row["name"], row["phone"], row["email"], row["city"])


@dataclass(frozen=True)
class Order:
    order_id: int
    customer_id: int
    order_date: str
    status: str
    total_brl: Decimal
    payment_method: str
    tracking_code: str
    estimated_delivery: str
    notes: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Order":
        return cls(
            order_id=int(row["order_id"]),
            customer_id=int(row["customer_id"]),
            order_date=row["order_date"],
            status=row["status"],
            total_brl=Decimal(row["total_brl"]),
            payment_method=row["payment_method"],
            tracking_code=row["tracking_code"],
            estimated_delivery=row["estimated_delivery"],
            notes=row["notes"],
        )


@dataclass(frozen=True)
class OrderItem:
    order_id: int
    quantity: int
    product_id: int

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "OrderItem":
        return cls(int(row["order_id"]), int(row["quantity"]), int(row["product_id"]))


@dataclass(frozen=True)
class Promotion:
    promotion_id: int
    product_id: int
    discount_percent: Decimal
    description: str
    is_active: bool

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Promotion":
        return cls(
            int(row["promotion_id"]),
            int(row["product_id"]),
            Decimal(row["discount_percent"]),
            row["description"],
            row["is_active"] == "1",
        )
