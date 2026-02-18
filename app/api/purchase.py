from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.schemas.purchase import *
from app.crud.purchase import create_purchase

router = APIRouter(prefix="/purchase", tags=["Purchase"])


@router.post("/")
def create_purchase_endpoint(
        data: PurchaseCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    try:
        return create_purchase(db, data)
    except Exception as exc:
        # Surface as a client error while avoiding unhandled 500s
        raise HTTPException(status_code=400, detail=str(exc))
