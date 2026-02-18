import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PDF_DIR = os.path.join(BASE_DIR, "invoices")

os.makedirs(PDF_DIR, exist_ok=True)


CLINIC_NAME = "Your Optical Clinic"
CLINIC_ADDRESS = "Address Line 1, City"
CLINIC_PHONE = "Phone: 9999999999"
CLINIC_GSTIN = "GSTIN: 32XXXXXXXXXXX"


def generate_invoice_pdf(sale):

    file_path = os.path.join(PDF_DIR, f"invoice_{sale.id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    y = height - 30

    # ================= HEADER =================

    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, y, CLINIC_NAME)

    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(30, y, CLINIC_ADDRESS)

    y -= 15
    c.drawString(30, y, CLINIC_PHONE)

    y -= 15
    c.drawString(30, y, CLINIC_GSTIN)

    y -= 25

    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, y, "TAX INVOICE")

    y -= 30

    # ================= SALE INFO =================

    c.setFont("Helvetica", 10)

    c.drawString(30, y, f"Invoice No: {sale.id}")
    c.drawRightString(width - 30, y, f"Date: {sale.created_at.strftime('%d-%m-%Y')}")

    y -= 20

    c.drawString(30, y, f"Customer: {sale.customer_name or '-'}")

    y -= 15
    c.drawString(30, y, f"Phone: {sale.customer_phone or '-'}")

    y -= 30

    # ================= ITEM TABLE =================

    data = []

    data.append([
        "Sl",
        "Item",
        "HSN",
        "Qty",
        "Rate",
        "Taxable",
        "GST %",
        "GST Amt",
        "Total"
    ])

    total_taxable = 0
    total_gst = 0
    grand_total = 0

    for idx, si in enumerate(sale.items, start=1):

        item = si.item

        taxable = float(si.taxable_value or 0)
        gst_amt = float(si.gst_amount or 0)
        total = taxable + gst_amt

        total_taxable += taxable
        total_gst += gst_amt
        grand_total += total

        data.append([
            idx,
            item.name,
            item.hsn_code or "",
            si.qty,
            float(si.price),
            f"{taxable:.2f}",
            f"{float(si.gst_percent or 0):.2f}",
            f"{gst_amt:.2f}",
            f"{total:.2f}"
        ])

    table = Table(data, colWidths=[
        30, 100, 60, 40, 60, 60, 50, 60, 60
    ])

    table.setStyle(TableStyle([

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),

        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),

        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),

        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),

    ]))

    w, h = table.wrap(0,0)

    table.drawOn(c, 30, y - h)

    y -= h + 20

    # ================= GST SUMMARY =================

    cgst = total_gst / 2
    sgst = total_gst / 2

    c.drawRightString(width - 30, y, f"Taxable Value : {total_taxable:.2f}")
    y -= 15

    c.drawRightString(width - 30, y, f"CGST : {cgst:.2f}")
    y -= 15

    c.drawRightString(width - 30, y, f"SGST : {sgst:.2f}")
    y -= 15

    c.setFont("Helvetica-Bold", 12)

    c.drawRightString(width - 30, y, f"Grand Total : {grand_total:.2f}")

    y -= 40

    # ================= SIGNATURE =================

    c.setFont("Helvetica", 10)

    c.drawString(30, y, "Authorized Signature")

    c.save()

    return file_path
