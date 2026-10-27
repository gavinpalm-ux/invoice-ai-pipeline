"""Score an extractor against hand-checked ground truth.

    python evals/run_evals.py --mode offline
    python evals/run_evals.py --mode claude      # needs ANTHROPIC_API_KEY

The number that matters most is "unsafe passes": invoices that should have
gone to a person but were marked ready to post. That has to be zero before
anything goes live; field accuracy is secondary because humans review flags.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import extract_claude  # noqa: E402
import extract_offline  # noqa: E402
from validate import validate  # noqa: E402

FIELDS = ["vendor", "invoice_number", "invoice_date", "due_date", "total", "gl_category"]


def same(field, got, want):
    if want is None or got is None:
        return got in (None, "") and want is None
    if field == "total":
        return abs(float(got) - float(want)) < 0.01
    return str(got).strip().lower() == str(want).strip().lower()


def main(mode: str):
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    truth = json.loads((ROOT / "evals" / "expected.json").read_text())["cases"]
    extractor = extract_claude if mode == "claude" else extract_offline
    pdfs = sorted((ROOT / "invoices" / "inbox").glob("*.pdf")) + sorted((ROOT / "evals" / "hard_cases").glob("*.pdf"))

    records = []
    for pdf in pdfs:
        try:
            rec = extractor.extract(pdf, config)
        except Exception as e:
            rec = {"line_items": [], "confidence": 0.0, "notes": str(e)}
        rec["source_file"] = pdf.name
        records.append(rec)
    records = validate(records, config)

    field_hits = {f: 0 for f in FIELDS}
    routing_hits, unsafe, rows = 0, [], []
    for rec in records:
        want = truth[rec["source_file"]]
        misses = [f for f in FIELDS if not same(f, rec.get(f), want[f])]
        for f in FIELDS:
            field_hits[f] += f not in misses
        routed_ok = rec["status"] == want["status"]
        routing_hits += routed_ok
        if want["status"] == "NEEDS_REVIEW" and rec["status"] == "READY_TO_POST":
            unsafe.append(rec["source_file"])
        rows.append((rec["source_file"], len(FIELDS) - len(misses), routed_ok, ", ".join(misses) or "—"))

    n = len(records)
    total_fields = n * len(FIELDS)
    field_acc = sum(field_hits.values()) / total_fields
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [
        f"# Eval results: `{mode}` extractor",
        "",
        f"_Run: {stamp} · {n} test invoices ({sum('hard_' in r['source_file'] for r in records)} in an unfamiliar layout)_",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Field accuracy | {field_acc:.0%} ({sum(field_hits.values())}/{total_fields}) |",
        f"| Correct routing (post vs. review) | {routing_hits}/{n} |",
        f"| **Unsafe passes** (should be reviewed, marked ready) | **{len(unsafe)}** |",
        "",
        "## By field",
        "",
        "| Field | Correct |",
        "|---|---:|",
        *[f"| {f} | {field_hits[f]}/{n} |" for f in FIELDS],
        "",
        "## By invoice",
        "",
        "| Invoice | Fields correct | Routed correctly | Missed fields |",
        "|---|---:|:---:|---|",
        *[f"| {f} | {c}/{len(FIELDS)} | {'✅' if ok else '❌'} | {m} |" for f, c, ok, m in rows],
    ]
    path = ROOT / "evals" / f"results_{mode}.md"
    path.write_text("\n".join(out) + "\n")
    print("\n".join(out[:10]))
    print(f"\nFull results: {path}")
    return 1 if unsafe else 0  # fail CI on any unsafe pass


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["claude", "offline"], default="offline")
    sys.exit(main(p.parse_args().mode))
