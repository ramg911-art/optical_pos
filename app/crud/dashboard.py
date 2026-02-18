from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models.all_models import Sale, Item, LensOrder, Purchase


def get_dashboard(db: Session):

    today = date.today()

    # SALES TODAY
    sales_today = db.query(
        func.coalesce(func.sum(Sale.total), 0)
    ).filter(
        func.date(Sale.created_at) == today
    ).scalar()

    # SALES COUNT
    sales_count = db.query(
        func.count(Sale.id)
    ).filter(
        func.date(Sale.created_at) == today
    ).scalar()

    # LOW STOCK
    low_stock_items = db.query(
        func.count(Item.id)
    ).filter(
        Item.stock_qty <= Item.reorder_level
    ).scalar()

    # PENDING LENS
    pending_lens_orders = db.query(
        func.count(LensOrder.id)
    ).filter(
        LensOrder.status != "DELIVERED"
    ).scalar()

    # READY LENS
    ready_orders = db.query(
        func.count(LensOrder.id)
    ).filter(
        LensOrder.status == "READY"
    ).scalar()

    # PURCHASE TODAY
    purchase_today = db.query(
        func.coalesce(func.sum(Purchase.total), 0)
    ).filter(
        func.date(Purchase.created_at) == today
    ).scalar()

    return {
        "sales_today": float(sales_today),
        "sales_count": sales_count,
        "low_stock_items": low_stock_items,
        "pending_lens_orders": pending_lens_orders,
        "ready_orders": ready_orders,
        "purchase_today": float(purchase_today),
    }
