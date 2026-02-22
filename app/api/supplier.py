from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.schemas.supplier import SupplierCreate, SupplierOut
from app.crud import supplier as crud

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return crud.list_suppliers(db)


@router.post("/", response_model=SupplierOut)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_supplier(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sid}")
def remove(
    sid: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ok = crud.delete_supplier(db, sid)
    if not ok:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"status": "deleted"}

