from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.schemas.lens import *
from app.crud import lens as crud

router = APIRouter(prefix="/lens", tags=["Lens"])


@router.post("/prescription")
def add_prescription(
        data: PrescriptionCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    try:
        return crud.create_prescription(db, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/order")
def create_order(
        data: LensOrderCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    try:
        return crud.create_lens_order(db, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{order_id}/status")
def change_status(
        order_id: int,
        data: StatusUpdate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    try:
        return crud.update_status(db, order_id, data.status, user.id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/")
def get_orders(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return crud.list_orders(db)
