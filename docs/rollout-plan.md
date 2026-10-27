# Rollout Plan: AI-Assisted Invoice Processing

How I would introduce this pipeline to a small finance team (2–5 people, 100–300 invoices a month). The technology is a few hundred lines of code; the rollout is where these projects succeed or fail.

## 1. Measure the baseline (weeks 1–2)

You can't claim savings you never measured.

- Time 30–50 invoices through the current process, start to finish.
- Pull the last 12 months of error data: duplicate payments, miscoded GL entries, late fees, invoices posted over the approval limit.
- Collect 100+ past invoices from the top 20 vendors, redact them, and hand-check the correct answers. This becomes the real eval set.

**Exit criteria:** documented minutes per invoice, error rate, and an eval set the AP lead has signed off on.

## 2. Shadow mode (weeks 3–6)

The pipeline runs on every incoming invoice, but **nothing it produces gets posted.** Staff process invoices the normal way, and we compare.

- Weekly review: where did the AI disagree with staff, and who was right?
- Tune `config.yaml` (confidence floor, GL keywords, vendor list) based on what the comparison shows.
- Every corrected invoice gets added to the eval set.

**Exit criteria:**

| Metric | Target |
|---|---|
| Unsafe passes (should be reviewed, marked ready) | 0 across the full pilot |
| Field accuracy on clean invoices | ≥ 97% |
| GL category agreement with AP lead | ≥ 90% |
| Staff confidence (short survey) | Majority "would use this" |

## 3. Assisted mode (weeks 7–12)

Clean invoices go to the ready-to-post file, and a person spot-checks a random 10% before posting. Flagged invoices go to the review queue.

- Track minutes per invoice again and compare to the baseline.
- Keep the eval gate in CI: any rule or prompt change has to pass before it runs on live invoices.

## 4. Steady state

- Spot-check rate drops to 5% once three months pass with zero unsafe passes.
- Monthly: review flags that turned out to be false alarms and tune rules to cut noise.
- Quarterly: refresh the eval set with new vendors and re-run.

## Roles

| Role | Owns |
|---|---|
| AP lead | Approving the eval set, final say on GL rules, weekly pilot review |
| Finance manager / controller | Approval threshold, vendor master, sign-off to leave each phase |
| Implementation lead (me) | Pipeline, evals, metrics, training, documentation |
| Auditor / board treasurer | Informed at each phase; gets the control list and audit trail |

## Training and change management

- **Frame it accurately:** the tool takes over data entry so staff can spend their time on exceptions, vendor relationships and month-end work. Nobody's job is "checking the robot".
- 30-minute walkthrough: how to read the review queue, what each flag means, and how to report a wrong extraction.
- One named person staff can go to with questions during the pilot.
- Share the weekly pilot numbers with the whole team, including the misses.

## Risks

| Risk | Mitigation |
|---|---|
| Model reads a number wrong and it gets posted | Math check, confidence floor, spot-checks, and the eval gate. The unsafe-pass target is zero. |
| Staff trust it too much and stop spot-checking | Random spot-checks are logged; the misses found are shared openly. |
| Sensitive data exposure | Invoices stay in the organization's storage; API used under appropriate data-retention terms; no bank details extracted. |
| Rules drift out of date (new vendors, new threshold) | Rules live in one config file owned by the AP lead, with a quarterly review. |
| Vendor changes invoice format | That's exactly the case the model handles and templates don't, and new formats get added to the eval set. |
