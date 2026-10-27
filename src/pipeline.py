"""Invoice pipeline: extract -> validate -> report.

    python src/pipeline.py                 # uses Claude if ANTHROPIC_API_KEY is set
    python src/pipeline.py --mode offline  # rule-based baseline, no API key needed
"""
import argparse
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import extract_claude  # noqa: E402
import extract_offline  # noqa: E402
from report import write_reports  # noqa: E402
from validate import validate  # noqa: E402


def run(inbox: Path, out_dir: Path, mode: str) -> list[dict]:
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    extractor = extract_claude if mode == "claude" else extract_offline

    records = []
    for pdf in sorted(inbox.glob("*.pdf")):
        try:
            rec = extractor.extract(pdf, config)
        except Exception as e:  # one bad file shouldn't stop the batch
            rec = {"vendor": None, "invoice_number": None, "invoice_date": None, "due_date": None,
                   "line_items": [], "total": None, "gl_category": None, "confidence": 0.0,
                   "notes": f"Extraction failed: {e}"}
        rec["source_file"] = pdf.name
        records.append(rec)
        print(f"  extracted {pdf.name}")

    records = validate(records, config)
    summary = write_reports(records, config, mode, out_dir)
    print(f"\n{sum(r['status'] == 'NEEDS_REVIEW' for r in records)} of {len(records)} flagged for review")
    print(f"Summary: {summary}")
    return records


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["claude", "offline", "auto"], default="auto")
    p.add_argument("--inbox", type=Path, default=ROOT / "invoices" / "inbox")
    p.add_argument("--out", type=Path, default=ROOT / "reports")
    a = p.parse_args()
    mode = a.mode
    if mode == "auto":
        mode = "claude" if os.environ.get("ANTHROPIC_API_KEY") else "offline"
    print(f"Running in {mode} mode")
    run(a.inbox, a.out, mode)
