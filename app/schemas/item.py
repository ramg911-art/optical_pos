from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


# ---------- CATEGORY ----------
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: str
    description: Optional[str] = None


# ---------- ITEM ----------
class ItemCreate(BaseModel):
    name: str
    category_id: int
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None

    # Supplier info (kept optional for backward compatibility)
    supplier_name: Optional[str] = None
    supplier_gst: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_address: Optional[str] = None

    # Tax and pricing
    barcode: Optional[str] = None
    hsn_code: Optional[str] = None
    cost_price: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    gst_percent: Optional[Decimal] = None
    stock_qty: Optional[int] = 0


class ItemOut(BaseModel):
    id: int
    name: str
    category_id: int
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None

    supplier_name: Optional[str] = None
    supplier_gst: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_address: Optional[str] = None

    barcode: Optional[str] = None
    hsn_code: Optional[str] = None
    cost_price: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    gst_percent: Optional[Decimal] = None
    stock_qty: int

    class Config:
        from_attributes = True


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None

    supplier_name: Optional[str] = None
    supplier_gst: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_address: Optional[str] = None

    barcode: Optional[str] = None
    hsn_code: Optional[str] = None
    cost_price: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    gst_percent: Optional[Decimal] = None
    stock_qty: Optional[int] = None

