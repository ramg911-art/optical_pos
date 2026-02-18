from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import get_current_user
from app.schemas.sales import *
from app.crud.sales import create_sale
from app.crud.sales import create_sale, get_sale
from fastapi.responses import FileResponse
from app.services.invoice_pdf import generate_invoice_pdf
from app.api.deps import get_current_user




router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleOut)
def create_sale_endpoint(
        data: SaleCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):

    try:
        sale = create_sale(db, data, user.id)
        return {
            "sale_id": sale.id,
            "total": sale.total,
            "balance": sale.balance
        }
    except Exception as e:
        raise HTTPException(400, str(e))
        
@router.get("/{sale_id}")
def get_sale_endpoint(
        sale_id: int,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)):

    sale = get_sale(db, sale_id)

    if not sale:
        raise HTTPException(404, "Sale not found")

    # ----- GST Summary -----
    total_cgst = sum([i.cgst or 0 for i in sale.items])
    total_sgst = sum([i.sgst or 0 for i in sale.items])
    total_gst = sum([i.gst_amount or 0 for i in sale.items])

    return {
        "id": sale.id,
        "total": sale.total,
        "paid": sale.paid,
        "balance": sale.balance,
        "status": sale.status,

        "gst_summary": {
            "cgst": total_cgst,
            "sgst": total_sgst,
            "total_gst": total_gst
        },

        "items": sale.items,
        "payments": sale.payments
    }


@router.get("/{sale_id}/pdf")
def invoice_pdf(
    sale_id:int,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)
 ):


    sale = get_sale(db, sale_id)

    if not sale:
        raise HTTPException(404, "Sale not found")

    pdf_path = generate_invoice_pdf(sale)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"invoice_{sale_id}.pdf"
    )

from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Body


@router.post("/{sale_id}/return")
def return_items(
    sale_id:int,
    data:dict = Body(...),
    db:Session = Depends(get_db),
    user=Depends(get_current_user)
):
    from app.models.all_models import Sale, SaleItem, Item

    sale = db.query(Sale).get(sale_id)
    if not sale:
        raise HTTPException(404,"Sale not found")

    returned_items = data.get("items", [])
    refund_method = data.get("method","CASH")

    refund_total = Decimal(0)

    for r in returned_items:

        sale_item = db.query(SaleItem).filter(
            SaleItem.sale_id==sale_id,
            SaleItem.item_id==r["item_id"]
        ).first()

        if not sale_item:
            raise HTTPException(400,"Invalid item")

        if r["qty"] > sale_item.qty:
            raise HTTPException(400,"Return exceeds sold")

        # Restore stock
        item = db.query(Item).get(r["item_id"])
        item.stock_qty += r["qty"]

        refund_total += Decimal(r["qty"]) * sale_item.price

    # Update sale status
    if refund_total == sale.total:
        sale.status = "FULL_RETURN"
    else:
        sale.status = "PARTIAL_RETURN"

    db.commit()

    return {
        "refund": float(refund_total),
        "method": refund_method,
        "time": datetime.now()
    }

from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from io import BytesIO


@router.get("/{sale_id}/return-pdf")
def return_pdf(
    sale_id:int,
    db:Session = Depends(get_db),
    user=Depends(get_current_user)
):

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    y = 800
    p.drawString(200,y,"RETURN RECEIPT")
    y -= 40

    p.drawString(50,y,f"Sale ID: {sale_id}")
    y -= 20

    p.drawString(50,y,"Refund processed")
    y -= 40

    p.drawString(50,y,"Thank you")
    p.showPage()
    p.save()

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"inline; filename=return_{sale_id}.pdf"
        }
    )

@router.get("/")
def list_sales(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    from app.models.all_models import Sale

    sales = db.query(Sale).order_by(Sale.id.desc()).all()

    return [
        {
            "id": s.id,
            "total": float(s.total),
            "status": s.status
        }
        for s in sales
    ]

