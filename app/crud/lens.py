from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.all_models import (
    LensOrder,
    Prescription,
    LensOrderStatusLog,
    Sale,
    Supplier,
)


def _safe_commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


# =====================================================
# CREATE PRESCRIPTION
# =====================================================

def create_prescription(db: Session, data):

    rx = Prescription(
        sale_id=data.sale_id,
        sphere_r=data.sphere_r,
        cyl_r=data.cyl_r,
        axis_r=data.axis_r,
        add_r=data.add_r,
        sphere_l=data.sphere_l,
        cyl_l=data.cyl_l,
        axis_l=data.axis_l,
        add_l=data.add_l,
        pd=data.pd,
        notes=data.notes,
    )

    db.add(rx)
    _safe_commit(db)
    db.refresh(rx)

    return rx


# =====================================================
# CREATE LENS ORDER
# =====================================================

def create_lens_order(db: Session, data):

    order = LensOrder(
        sale_id=data.sale_id,
        prescription_id=data.prescription_id,
        supplier_id=data.supplier_id,
        lens_type=data.lens_type,
        index_value=data.index_value,
        coating=data.coating,
        tint=data.tint,
        order_date=date.today(),
        expected_date=(
            data.expected_date
            if hasattr(data, "expected_date") and data.expected_date
            else None
        ),
        status="ORDERED",
    )

    db.add(order)
    _safe_commit(db)
    db.refresh(order)

    # CREATE STATUS LOG
    log = LensOrderStatusLog(
        lens_order_id=order.id,
        status="ORDERED",
        changed_by=None,
    )

    db.add(log)
    _safe_commit(db)

    return order


# =====================================================
# UPDATE STATUS  (THIS FIXES YOUR 500 ERROR)
# =====================================================

def update_status(db: Session, order_id: int, status: str, user_id: int):

    order = db.query(LensOrder).filter(
        LensOrder.id == order_id
    ).first()

    if not order:

        return {
            "error": "Order not found"
        }

    # update order
    order.status = status

    # create log
    log = LensOrderStatusLog(
        lens_order_id=order_id,
        status=status,
        changed_by=user_id,
    )

    db.add(log)

    _safe_commit(db)

    db.refresh(order)

    return {
        "success": True,
        "order_id": order.id,
        "new_status": order.status,
    }


# =====================================================
# LIST ORDERS (your existing correct version)
# =====================================================

def list_orders(db: Session):

    orders = (
        db.query(LensOrder)
        .options(
            selectinload(LensOrder.sale).selectinload(Sale.customer),
            selectinload(LensOrder.supplier),
        )
        .order_by(LensOrder.id.desc())
        .all()
    )

    result = []

    for o in orders:

        result.append({

            "id": o.id,

            "patient_name": (
                o.sale.customer_name
                or (o.sale.customer.name if o.sale and o.sale.customer else "")
                if o.sale else ""
            ),

            "patient_phone": (
                o.sale.customer_phone
                or (o.sale.customer.phone if o.sale and o.sale.customer else "")
                if o.sale else ""
            ),

            "supplier": o.supplier.name if o.supplier else "",

            "lens_type": o.lens_type,
            "index_value": o.index_value,
            "coating": o.coating,
            "tint": o.tint,

            "status": o.status,

            "order_date": (
                o.order_date.strftime("%Y-%m-%d")
                if o.order_date else ""
            ),

            "expected_date": (
                o.expected_date.strftime("%Y-%m-%d")
                if o.expected_date else ""
            ),

            "sale_id": o.sale_id,
            "supplier_id": o.supplier_id,
            "prescription_id": o.prescription_id,

        })

    return result
