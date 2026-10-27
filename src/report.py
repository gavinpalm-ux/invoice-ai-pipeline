"""Write the outputs a finance team actually uses."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

CSV_FIELDS = ["source_file", "vendor", "invoice_number", "invoice_date", "due_date",
              "total", "gl_category", "confidence", "status", "flags"]


def _write_csv(path: Path, rows: list[dict]):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "flags": " | ".join(r["flags"])})


def write_reports(records: list[dict], config: dict, mode: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    ready = [r for r in records if r["status"] == "READY_TO_POST"]
    review = [r for r in records if r["status"] == "NEEDS_REVIEW"]

    (out_dir / "extracted.json").write_text(json.dumps(records, indent=2))
    _write_csv(out_dir / "ready_to_post.csv", ready)
    _write_csv(out_dir / "review_queue.csv", review)

    # Time-savings estimate, scaled to monthly volume using this run's flag rate.
    roi = config["roi"]
    n = len(records) or 1
    flag_rate = len(review) / n
    vol = roi["monthly_invoice_volume"]
    manual_hrs = vol * roi["manual_minutes_per_invoice"] / 60
    assisted_hrs = vol * (flag_rate * roi["review_minutes_flagged"]
                          + (1 - flag_rate) * roi["review_minutes_clean"]) / 60
    saved_hrs = manual_hrs - assisted_hrs

    total_ready = sum(r["total"] or 0 for r in ready)
    total_review = sum(r["total"] or 0 for r in review)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Invoice Processing Run",
        "",
        f"_Run: {stamp} · Extractor: **{mode}** · Invoices: **{len(records)}**_",
        "",
        "| | Count | Amount |",
        "|---|---:|---:|",
        f"| ✅ Ready to post | {len(ready)} | ${total_ready:,.2f} |",
        f"| ⚠️ Needs human review | {len(review)} | ${total_review:,.2f} |",
        "",
        "## Review queue",
        "",
    ]
    if review:
        lines += ["| File | Vendor | Total | Why it was flagged |", "|---|---|---:|---|"]
        for r in review:
            total = f"${r['total']:,.2f}" if r.get("total") is not None else "—"
            lines.append(f"| {r['source_file']} | {r.get('vendor', '')} | {total} | {'<br>'.join(r['flags'])} |")
    else:
        lines.append("Nothing flagged.")

    lines += ["", "## Ready to post", "", "| File | Vendor | GL category | Total |", "|---|---|---|---:|"]
    for r in ready:
        lines.append(f"| {r['source_file']} | {r['vendor']} | {r['gl_category']} | ${r['total']:,.2f} |")

    lines += [
        "",
        "## Estimated monthly impact",
        "",
        f"At {vol} invoices/month and this run's {flag_rate:.0%} review rate:",
        "",
        f"- Manual processing: **{manual_hrs:.1f} hrs/month**",
        f"- AI-assisted with human review: **{assisted_hrs:.1f} hrs/month**",
        f"- Time returned to staff: **{saved_hrs:.1f} hrs/month** "
        f"(≈ ${saved_hrs * roi['loaded_hourly_cost']:,.0f} at ${roi['loaded_hourly_cost']:.0f}/hr)",
        "",
        "_Assumptions are in `config.yaml` → `roi`. Time them in your own office before quoting. "
        "The sample inbox is deliberately problem-heavy, so its review rate (and this estimate) is conservative._",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")
    return out_dir / "summary.md"
