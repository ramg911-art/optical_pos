from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


# ---------- CATEGORY ----------
class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------- ITEM ----------
class ItemCreate(BaseModel):
    name: str
    category_id: int
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    barcode: Optional[str] = None
    hsn_code: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    gst_percent: Optional[Decimal] = None
    stock_qty: Optional[int] = 0
    supplier_name: Optional[str] = None
    supplier_gst: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_address: Optional[str] = None


class ItemOut(BaseModel):
    id: int
    name: str
    stock_qty: int
    selling_price: Optional[Decimal]
    purchase_price: Optional[Decimal] = None
    gst_percent: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_gst: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_address: Optional[str] = None

    class Config:
        from_attributes = True

# ---------- UPDATE ----------
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    barcode: Optional[str] = None
    hsn_code: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    gst_percent: Optional[Decimal] = None
    stock_qty: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_gst: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_address: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: str

