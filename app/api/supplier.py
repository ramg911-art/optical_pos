from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.schemas.supplier import *
from app.crud import supplier as crud

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("/")
def create(
        data: SupplierCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud.create_supplier(db, data)


@router.get("/")
def list_all(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud.list_suppliers(db)


@router.delete("/{sid}")
def remove(
        sid: int,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    crud.delete_supplier(db, sid)
    return {"status": "deleted"}

@router.get("/")
def list_suppliers(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    from app.models.all_models import Supplier

    s = db.query(Supplier).all()

    return [
        {"id":i.id,"name":i.name}
        for i in s
    ]

