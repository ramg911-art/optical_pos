from pydantic import BaseModel
from typing import Optional


class SupplierCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    gstin: Optional[str] = None
    address: Optional[str] = None


class SupplierOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    gstin: Optional[str]
    address: Optional[str]

    class Config:
        from_attributes = True
