from pydantic import BaseModel
from typing import List
from decimal import Decimal


class SaleItemIn(BaseModel):
    item_id: int
    qty: int
    price: Decimal


class SaleCreate(BaseModel):
    customer_id: int | None = None
    items: List[SaleItemIn]
    payment_amount: Decimal = 0
    payment_method: str = "cash"


class SaleOut(BaseModel):
    sale_id: int
    total: Decimal
    balance: Decimal

class SaleItemOut(BaseModel):
    item_id: int
    qty: int
    price: Decimal

    gst_percent: Decimal | None
    taxable_value: Decimal | None
    gst_amount: Decimal | None
    cgst: Decimal | None
    sgst: Decimal | None

    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    amount: Decimal
    method: str
    payment_type: str

    class Config:
        from_attributes = True


class SaleDetailOut(BaseModel):
    id: int
    total: Decimal
    paid: Decimal
    balance: Decimal
    status: str

    items: list[SaleItemOut]
    payments: list[PaymentOut]

    class Config:
        from_attributes = True

class SaleOut(BaseModel):
    sale_id: int
    total: Decimal
    balance: Decimal
    # optional
    # tax_total: Decimal
