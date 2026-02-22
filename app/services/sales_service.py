from typing import Any, Dict, List

from app.models.all_models import Sale


def build_sale_detail_response(sale: Sale) -> Dict[str, Any]:
    """
    Shape a detailed sale response, including GST summary,
    matching the existing API output structure.
    """
    total_cgst = sum([i.cgst or 0 for i in sale.items])
    total_sgst = sum([i.sgst or 0 for i in sale.items])
    total_gst = sum([i.gst_amount or 0 for i in sale.items])

    adv = getattr(sale, "advance_amount", None)
    adv_mode = getattr(sale, "advance_payment_mode", None)
    adv_date = getattr(sale, "advance_payment_date", None)
    bal_amt = getattr(sale, "balance_amount", None)
    bal_mode = getattr(sale, "balance_payment_mode", None)
    bal_date = getattr(sale, "balance_payment_date", None)
    pay_status = getattr(sale, "payment_status", None)
    del_status = getattr(sale, "delivery_status", None)

    return {
        "id": sale.id,
        "total": sale.total,
        "paid": sale.paid,
        "balance": sale.balance,
        "status": sale.status,
        "advance_amount": float(adv) if adv is not None else None,
        "advance_payment_mode": adv_mode,
        "advance_payment_date": adv_date.strftime("%Y-%m-%d %H:%M") if adv_date else None,
        "balance_amount": float(bal_amt) if bal_amt is not None else None,
        "balance_payment_mode": bal_mode,
        "balance_payment_date": bal_date.strftime("%Y-%m-%d %H:%M") if bal_date else None,
        "payment_status": pay_status,
        "delivery_status": del_status,
        "gst_summary": {
            "cgst": total_cgst,
            "sgst": total_sgst,
            "total_gst": total_gst,
        },
        "items": sale.items,
        "payments": sale.payments,
    }


def build_sales_list_response(sales: List[Sale]) -> List[Dict[str, Any]]:
    """
    Compact list representation for /sales listing endpoint.
    """
    return [
        {
            "id": s.id,
            "total": float(s.total),
            "status": s.status,
            "payment_status": getattr(s, "payment_status", None),
            "delivery_status": getattr(s, "delivery_status", None),
        }
        for s in sales
    ]

