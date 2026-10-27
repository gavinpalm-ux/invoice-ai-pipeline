"""Guardrails: deterministic business rules applied to every AI extraction.

The model reads the document; plain code decides whether the result is safe
to post. Each failed rule becomes a flag, and any flag sends the invoice to
a person instead of straight into the books.
"""


def validate(records: list[dict], config: dict) -> list[dict]:
    seen = {}
    approved_vendors = {v.lower() for v in config["approved_vendors"]}

    for rec in records:
        flags = []

        missing = [f for f in config["required_fields"] if rec.get(f) in (None, "")]
        if missing:
            flags.append(f"Missing required field(s): {', '.join(missing)}")

        if (rec.get("vendor") or "").lower() not in approved_vendors:
            flags.append("Vendor not on approved list - verify W-9 and set up vendor before paying")

        total = rec.get("total")
        line_sum = round(sum(li.get("amount", 0) for li in rec.get("line_items", [])), 2)
        if total is not None and abs(line_sum - total) > config["total_tolerance"]:
            flags.append(f"Total ${total:,.2f} does not match line items ${line_sum:,.2f}")

        if total is not None and total >= config["approval_threshold"]:
            flags.append(f"Over ${config['approval_threshold']:,.0f} approval threshold - needs manager sign-off")

        if rec.get("confidence", 0) < config["min_confidence"]:
            flags.append(f"Low extraction confidence ({rec.get('confidence', 0):.2f})")

        # Same vendor + number, or same vendor + date + total when the number is missing.
        key = ((rec.get("vendor") or "").lower(), rec.get("invoice_number")) if rec.get("invoice_number") \
            else ((rec.get("vendor") or "").lower(), rec.get("invoice_date"), total)
        if key in seen:
            flags.append(f"Possible duplicate of {seen[key]}")
        else:
            seen[key] = rec["source_file"]

        rec["flags"] = flags
        rec["status"] = "NEEDS_REVIEW" if flags else "READY_TO_POST"
    return records
