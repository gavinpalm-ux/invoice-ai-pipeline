"""Rule-based extractor used when no API key is set.

This is the "before AI" baseline: brittle, template-specific parsing of the
kind many small offices script by hand. It only understands the sample
invoice layout. Keeping it in the repo does two jobs:
  1. the pipeline and GitHub Action run end to end with no API key, and
  2. evals/run_evals.py can compare it against Claude on the same test set.
"""
import re
from pathlib import Path

from pypdf import PdfReader

LABELS = {"Invoice #:": "invoice_number", "Invoice Date:": "invoice_date",
          "Due Date:": "due_date", "Bill To:": "bill_to"}


def _money(s: str) -> float:
    return float(s.replace("$", "").replace(",", ""))


def _categorize(text: str, gl_categories: dict) -> str:
    low = text.lower()
    for category, keywords in gl_categories.items():
        if any(k in low for k in keywords):
            return category
    return list(gl_categories)[-1]


def extract(pdf_path: Path, config: dict) -> dict:
    lines = [l.strip() for l in PdfReader(str(pdf_path)).pages[0].extract_text().splitlines() if l.strip()]
    out = {"vendor": lines[0], "invoice_number": None, "invoice_date": None,
           "due_date": None, "line_items": [], "total": None, "notes": ""}

    for i, line in enumerate(lines):
        if line in LABELS:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if nxt not in LABELS:  # empty value -> next line is another label
                out[LABELS[line]] = nxt
    out.pop("bill_to", None)

    try:
        start = lines.index("Amount") + 1
        end = lines.index("TOTAL DUE")
        rows = lines[start:end]
        for j in range(0, len(rows) - 3, 4):
            desc, qty, unit, amt = rows[j:j + 4]
            out["line_items"].append({"description": desc, "quantity": float(qty),
                                      "unit_price": _money(unit), "amount": _money(amt)})
        out["total"] = _money(lines[end + 1])
    except (ValueError, IndexError):
        out["notes"] = "Layout not recognized by rule-based parser."

    descriptions = " ".join(li["description"] for li in out["line_items"])
    out["gl_category"] = _categorize(descriptions, config["gl_categories"])
    # A template parser can't judge its own certainty; it's sure or it failed.
    out["confidence"] = 0.9 if out["line_items"] and out["total"] is not None else 0.2
    return out
