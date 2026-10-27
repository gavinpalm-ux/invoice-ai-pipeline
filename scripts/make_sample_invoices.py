"""Generate fictional sample invoices for the demo.

Every vendor, address and amount here is invented. The set deliberately
includes problem cases so the validation layer has something to catch:
a duplicate, a missing invoice number, an over-threshold amount, a total
that doesn't match its line items, and a vendor not on the approved list.

Usage:  python scripts/make_sample_invoices.py
"""
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "invoices" / "inbox"

INVOICES = [
    # file, vendor, invoice_no, date, due, lines[(desc, qty, unit)], stated_total (None = compute)
    ("inv_001_gulfcoast_office.pdf", "Gulf Coast Office Supply", "GCO-10482", "2026-09-02", "2026-10-02",
     [("Copy paper, case", 4, 42.50), ("Toner cartridge", 2, 89.99)], None),
    ("inv_002_suncoast_print.pdf", "Suncoast Print & Design", "SPD-2231", "2026-09-05", "2026-09-30",
     [("Event flyers (500)", 1, 185.00), ("Banner 3x6", 1, 120.00)], None),
    ("inv_003_peace_river_it.pdf", "Peace River IT Services", "PRIT-0917", "2026-09-08", "2026-10-08",
     [("Managed IT support - Sept", 1, 650.00), ("Laptop setup", 3, 75.00)], None),
    ("inv_004_gulfcoast_office_dup.pdf", "Gulf Coast Office Supply", "GCO-10482", "2026-09-02", "2026-10-02",
     [("Copy paper, case", 4, 42.50), ("Toner cartridge", 2, 89.99)], None),  # duplicate of 001
    ("inv_005_harbor_catering.pdf", "Harbor Catering Co.", "", "2026-09-12", "2026-09-26",
     [("Volunteer luncheon, 40 guests", 40, 14.75)], None),  # missing invoice number
    ("inv_006_myakka_av.pdf", "Myakka Audio Visual", "MAV-5520", "2026-09-15", "2026-10-15",
     [("Projector rental, 2 days", 1, 400.00), ("Sound system + tech", 1, 4850.00)], None),  # over threshold
    ("inv_007_tidewater_cleaning.pdf", "Tidewater Cleaning", "TWC-311", "2026-09-18", "2026-10-18",
     [("Office cleaning, 4 visits", 4, 95.00)], 420.00),  # stated total != line items (380)
    ("inv_008_quick_logo_llc.pdf", "QuickLogo Merch LLC", "QL-88", "2026-09-20", "2026-10-05",
     [("Branded t-shirts", 60, 11.25)], None),  # unapproved vendor
]


def draw_invoice(path, vendor, number, date, due, lines, stated_total):
    c = canvas.Canvas(str(path), pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, h - 60, vendor)
    c.setFont("Helvetica", 10)
    c.drawString(50, h - 76, "123 Example Street, Sample City, FL 00000")
    c.setFont("Helvetica-Bold", 22)
    c.drawRightString(w - 50, h - 60, "INVOICE")
    c.setFont("Helvetica", 10)
    y = h - 110
    for label, val in [("Invoice #:", number or ""), ("Invoice Date:", date), ("Due Date:", due),
                       ("Bill To:", "Example Community Nonprofit")]:
        c.drawString(w - 250, y, label)
        c.drawString(w - 160, y, val)
        y -= 14
    y = h - 200
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawRightString(380, y, "Qty")
    c.drawRightString(460, y, "Unit Price")
    c.drawRightString(w - 50, y, "Amount")
    c.line(50, y - 4, w - 50, y - 4)
    c.setFont("Helvetica", 10)
    subtotal = 0.0
    for desc, qty, unit in lines:
        y -= 18
        amt = qty * unit
        subtotal += amt
        c.drawString(50, y, desc)
        c.drawRightString(380, y, str(qty))
        c.drawRightString(460, y, f"${unit:,.2f}")
        c.drawRightString(w - 50, y, f"${amt:,.2f}")
    total = stated_total if stated_total is not None else subtotal
    y -= 30
    c.line(350, y + 12, w - 50, y + 12)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, "TOTAL DUE")
    c.drawRightString(w - 50, y, f"${total:,.2f}")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 40, "Fictional sample invoice generated for a portfolio demo.")
    c.save()


HARD_OUT = Path(__file__).resolve().parent.parent / "evals" / "hard_cases"


def draw_alt_layout(path, vendor, number, date_text, terms_text, items, total):
    """A different vendor template: labels, date format and table style all change.
    Template parsers break here; a model that reads the page doesn't."""
    c = canvas.Canvas(str(path), pagesize=letter)
    w, h = letter
    c.setFont("Times-Bold", 16)
    c.drawCentredString(w / 2, h - 60, vendor.upper())
    c.setFont("Times-Roman", 11)
    c.drawCentredString(w / 2, h - 78, "Statement of Charges")
    c.drawString(60, h - 120, f"Bill No. {number}    |    Issued {date_text}    |    {terms_text}")
    c.drawString(60, h - 138, "Customer: Example Community Nonprofit")
    y = h - 180
    for desc, amt in items:
        c.drawString(60, y, f"- {desc}")
        c.drawRightString(w - 60, y, f"{amt:,.2f} USD")
        y -= 16
    c.setFont("Times-Bold", 12)
    c.drawString(60, y - 20, "Balance owing")
    c.drawRightString(w - 60, y - 20, f"{total:,.2f} USD")
    c.setFont("Times-Italic", 8)
    c.drawString(60, 40, "Fictional sample invoice generated for a portfolio demo.")
    c.save()


HARD_CASES = [
    ("hard_01_alt_layout.pdf", "Venice Grounds Landscaping", "VGL/2026/044", "September 22, 2026",
     "Net 30 (due October 22, 2026)", [("Monthly grounds maintenance", 275.00), ("Mulch, 10 bags", 64.50)], 339.50),
    ("hard_02_alt_layout.pdf", "Englewood Signworks", "ES-7781", "October 1, 2026",
     "Payable by October 15, 2026", [("Outdoor vinyl banner, printed", 210.00)], 210.00),
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for row in INVOICES:
        draw_invoice(OUT / row[0], *row[1:])
    print(f"Wrote {len(INVOICES)} invoices to {OUT}")
    HARD_OUT.mkdir(parents=True, exist_ok=True)
    for row in HARD_CASES:
        draw_alt_layout(HARD_OUT / row[0], *row[1:])
    print(f"Wrote {len(HARD_CASES)} alternate-layout eval invoices to {HARD_OUT}")
