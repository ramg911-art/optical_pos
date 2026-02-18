from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


# ---------- PRESCRIPTION ----------
class PrescriptionCreate(BaseModel):
    sale_id: int

    sphere_r: Optional[Decimal] = None
    cyl_r: Optional[Decimal] = None
    axis_r: Optional[int] = None
    add_r: Optional[Decimal] = None

    sphere_l: Optional[Decimal] = None
    cyl_l: Optional[Decimal] = None
    axis_l: Optional[int] = None
    add_l: Optional[Decimal] = None

    pd: Optional[Decimal] = None
    notes: Optional[str] = None


# ---------- LENS ORDER ----------
from pydantic import BaseModel
from typing import Optional
from datetime import date

class LensOrderCreate(BaseModel):

    sale_id: int
    prescription_id: int
    supplier_id: int

    lens_type: Optional[str] = None
    index_value: Optional[str] = None
    coating: Optional[str] = None
    tint: Optional[str] = None

    order_date: Optional[date] = None
    expected_date: Optional[date] = None

    status: Optional[str] = "ORDERED"



class StatusUpdate(BaseModel):
    status: str
