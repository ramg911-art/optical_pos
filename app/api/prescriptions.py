from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.all_models import Prescription

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.post("/")
def create_prescription(
    data: dict,
    db: Session = Depends(get_db)
):
    try:
        # QUICK FIX: convert empty strings to None
        cleaned_data = {}

        numeric_fields = [
            "sphere_r", "cyl_r", "axis_r", "add_r",
            "sphere_l", "cyl_l", "axis_l", "add_l",
            "pd",
        ]

        for key, value in data.items():
            if key in numeric_fields and value == "":
                cleaned_data[key] = None
            else:
                cleaned_data[key] = value

        rx = Prescription(**cleaned_data)

        db.add(rx)
        db.commit()
        db.refresh(rx)

        return {"id": rx.id}
    except Exception as exc:
        # Keep behavior simple: surface validation/DB issues as a 400
        raise HTTPException(status_code=400, detail=str(exc))
