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

    return {
        "id": sale.id,
        "total": sale.total,
        "paid": sale.paid,
        "balance": sale.balance,
        "status": sale.status,
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
        }
        for s in sales
    ]

