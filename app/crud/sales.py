from datetime import datetime
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

    advance = Decimal(data.advance_amount or data.payment_amount or 0)
    balance_amt = total - advance
    if advance >= total:
        payment_status = "paid"
        balance_amt = Decimal("0")
    elif advance > 0:
        payment_status = "partial"
    else:
        payment_status = "pending"
    advance_mode = data.advance_payment_mode or data.payment_method or "CASH"

    paid_stored = data.payment_amount or advance
    balance_stored = total - paid_stored

    sale = Sale(
        customer_id=data.customer_id,
        total=total,
        paid=paid_stored,
        balance=balance_stored,
        status="COMPLETED",
        created_by=user_id,
        advance_amount=advance,
        advance_payment_mode=advance_mode if advance > 0 else None,
        advance_payment_date=datetime.utcnow() if advance > 0 else None,
        balance_amount=balance_amt,
        balance_payment_mode=None,
        balance_payment_date=None,
        payment_status=payment_status,
        delivery_status="pending",
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
    amt = data.payment_amount or advance
    mode = data.advance_payment_mode or data.payment_method or "CASH"
    if amt and Decimal(amt) > 0:
        payment = Payment(
            sale_id=sale.id,
            amount=amt,
            method=mode,
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


# =========================================================
# DELIVER SALE
# =========================================================
def deliver_sale(db: Session, sale_id: int, balance_payment_mode: str):
    """
    Mark sale as delivered, record balance payment.
    Sets balance_payment_date=now(), payment_status=paid, delivery_status=delivered, balance_amount=0.
    Records balance payment in Payment table if balance_amount > 0.
    """
    sale = db.query(Sale).get(sale_id)
    if not sale:
        return None
    bal = Decimal(str(getattr(sale, "balance_amount", 0) or 0))
    sale.balance_payment_mode = balance_payment_mode
    sale.balance_payment_date = datetime.utcnow()
    sale.payment_status = "paid"
    sale.delivery_status = "delivered"
    sale.balance_amount = Decimal("0")
    sale.balance = Decimal("0")
    sale.paid = (sale.paid or Decimal("0")) + bal
    if bal > 0:
        db.add(Payment(sale_id=sale_id, amount=bal, method=balance_payment_mode))
    _safe_commit(db)
    db.refresh(sale)
    return sale
