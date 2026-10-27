# Eval results: `offline` extractor

_Run: 2026-10-26 23:54 UTC · 10 test invoices (2 in an unfamiliar layout)_

| Metric | Result |
|---|---:|
| Field accuracy | 83% (50/60) |
| Correct routing (post vs. review) | 10/10 |
| **Unsafe passes** (should be reviewed, marked ready) | **0** |

## By field

| Field | Correct |
|---|---:|
| vendor | 10/10 |
| invoice_number | 8/10 |
| invoice_date | 8/10 |
| due_date | 8/10 |
| total | 8/10 |
| gl_category | 8/10 |

## By invoice

| Invoice | Fields correct | Routed correctly | Missed fields |
|---|---:|:---:|---|
| inv_001_gulfcoast_office.pdf | 6/6 | ✅ | — |
| inv_002_suncoast_print.pdf | 6/6 | ✅ | — |
| inv_003_peace_river_it.pdf | 6/6 | ✅ | — |
| inv_004_gulfcoast_office_dup.pdf | 6/6 | ✅ | — |
| inv_005_harbor_catering.pdf | 6/6 | ✅ | — |
| inv_006_myakka_av.pdf | 6/6 | ✅ | — |
| inv_007_tidewater_cleaning.pdf | 6/6 | ✅ | — |
| inv_008_quick_logo_llc.pdf | 6/6 | ✅ | — |
| hard_01_alt_layout.pdf | 1/6 | ✅ | invoice_number, invoice_date, due_date, total, gl_category |
| hard_02_alt_layout.pdf | 1/6 | ✅ | invoice_number, invoice_date, due_date, total, gl_category |
