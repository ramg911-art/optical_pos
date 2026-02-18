from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.all_models import (
    Sale,
    SaleItem,
    Payment,
    Item,
)


def _safe_commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


# =========================================================
# CREATE SALE
# =========================================================
def create_sale(db: Session, data, user_id: int):
    """
    Create a GST-compliant sale:
    - Calculates GST per item
    - Stores GST values in SaleItem
    - Deducts stock
    - Records payment
    """

    total = Decimal("0.00")
    total_tax = Decimal("0.00")

    calculated_rows = []

    # =====================================================
    # STEP 1: VALIDATE ITEMS & CALCULATE GST
    # =====================================================
    for row in data.items:

        item = db.query(Item).get(row.item_id)

        if not item:
            raise Exception("Item not found")

        if item.stock_qty < row.qty:
            raise Exception(f"Insufficient stock for {item.name}")

        taxable_value = Decimal(row.price) * Decimal(row.qty)

        gst_rate = item.gst_percent or Decimal("0.00")

        gst_amount = (taxable_value * gst_rate) / Decimal("100")

        cgst = gst_amount / Decimal("2")
        sgst = gst_amount / Decimal("2")

        total += taxable_value + gst_amount
        total_tax += gst_amount

        calculated_rows.append(
            (
                row,
                item,
                taxable_value,
                gst_rate,
                gst_amount,
                cgst,
                sgst
            )
        )

    balance = total - Decimal(data.payment_amount or 0)

    # =====================================================
    # STEP 2: CREATE SALE MASTER RECORD
    # =====================================================
    sale = Sale(
        customer_id=data.customer_id,
        total=total,
        paid=data.payment_amount,
        balance=balance,
        status="COMPLETED",
        created_by=user_id
    )

    db.add(sale)
    db.flush()   # ensures sale.id is generated

    # =====================================================
    # STEP 3: INSERT SALE ITEMS
    # =====================================================
    for row, item, taxable, gst_rate, gst_amt, cgst, sgst in calculated_rows:

        sale_item = SaleItem(
            sale_id=sale.id,
            item_id=row.item_id,
            qty=row.qty,
            price=row.price,

            # GST fields
            gst_percent=gst_rate,
            taxable_value=taxable,
            gst_amount=gst_amt,
            cgst=cgst,
            sgst=sgst
        )

        db.add(sale_item)

        # deduct stock
        item.stock_qty -= row.qty

    # =====================================================
    # STEP 4: RECORD PAYMENT
    # =====================================================
    if data.payment_amount and Decimal(data.payment_amount) > 0:

        payment = Payment(
            sale_id=sale.id,
            amount=data.payment_amount,
            method=data.payment_method   # ✅ CORRECT FIELD
        )

        db.add(payment)

    # =====================================================
    # STEP 5: COMMIT
    # =====================================================
    _safe_commit(db)

    db.refresh(sale)

    return sale


# =========================================================
# GET SALE
# =========================================================
def get_sale(db: Session, sale_id: int):
    """
    Fetch full sale including items and payments
    """

    return db.query(Sale).get(sale_id)
