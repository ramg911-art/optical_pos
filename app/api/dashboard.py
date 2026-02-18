from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.crud.dashboard import get_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard(
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):
    return get_dashboard(db)
