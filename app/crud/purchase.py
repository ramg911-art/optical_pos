from decimal import Decimal
from app.models.all_models import (
    Purchase,
    PurchaseItem,
    Item,
    StockMovement
)


def create_purchase(db, data):

    total = Decimal(0)

    purchase = Purchase(
        supplier_id=data.supplier_id,
        invoice_no=data.invoice_no,
    )

    db.add(purchase)
    db.flush()

    for row in data.items:

        item = db.query(Item).get(row.item_id)

        line_total = row.qty * row.price
        total += line_total

        db.add(PurchaseItem(
            purchase_id=purchase.id,
            item_id=row.item_id,
            qty=row.qty,
            price=row.price,
            gst_percent=row.gst_percent
        ))

        # ---------- Update Stock ----------
        item.stock_qty += row.qty

        # ---------- Movement Log ----------
        db.add(StockMovement(
            item_id=row.item_id,
            change_qty=row.qty,
            movement_type="PURCHASE",
            reference_id=purchase.id
        ))

    purchase.total = total

    db.commit()
    db.refresh(purchase)

    return purchase
