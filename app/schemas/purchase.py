from pydantic import BaseModel
from decimal import Decimal
from typing import List


class PurchaseItemIn(BaseModel):
    item_id: int
    qty: int
    price: Decimal
    gst_percent: Decimal | None = 0


class PurchaseCreate(BaseModel):
    supplier_id: int
    invoice_no: str
    items: List[PurchaseItemIn]
