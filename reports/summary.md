# Invoice Processing Run

_Run: 2026-10-26 23:55 UTC · Extractor: **offline** · Invoices: **8**_

| | Count | Amount |
|---|---:|---:|
| ✅ Ready to post | 3 | $1,529.98 |
| ⚠️ Needs human review | 5 | $7,284.98 |

## Review queue

| File | Vendor | Total | Why it was flagged |
|---|---|---:|---|
| inv_004_gulfcoast_office_dup.pdf | Gulf Coast Office Supply | $349.98 | Possible duplicate of inv_001_gulfcoast_office.pdf |
| inv_005_harbor_catering.pdf | Harbor Catering Co. | $590.00 | Missing required field(s): invoice_number |
| inv_006_myakka_av.pdf | Myakka Audio Visual | $5,250.00 | Over $2,500 approval threshold - needs manager sign-off |
| inv_007_tidewater_cleaning.pdf | Tidewater Cleaning | $420.00 | Total $420.00 does not match line items $380.00 |
| inv_008_quick_logo_llc.pdf | QuickLogo Merch LLC | $675.00 | Vendor not on approved list - verify W-9 and set up vendor before paying |

## Ready to post

| File | Vendor | GL category | Total |
|---|---|---|---:|
| inv_001_gulfcoast_office.pdf | Gulf Coast Office Supply | 6100 Office Supplies | $349.98 |
| inv_002_suncoast_print.pdf | Suncoast Print & Design | 6200 Printing & Marketing | $305.00 |
| inv_003_peace_river_it.pdf | Peace River IT Services | 6300 IT & Technology | $875.00 |

## Estimated monthly impact

At 150 invoices/month and this run's 62% review rate:

- Manual processing: **15.0 hrs/month**
- AI-assisted with human review: **5.2 hrs/month**
- Time returned to staff: **9.8 hrs/month** (≈ $295 at $30/hr)

_Assumptions are in `config.yaml` → `roi`. Time them in your own office before quoting. The sample inbox is deliberately problem-heavy, so its review rate (and this estimate) is conservative._
