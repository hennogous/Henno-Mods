# Customer adjacency comparison at turn 225

Offline reconstruction from the original turn225 snapshots, players1–5 only.
The baseline pools five stock-AI Standard games; tuning/current columns are one
world each. Worlds, resource passes, builds and combined treatments differ.
No actual monetary payment ledger was captured. Eligible links below are
functioning same-owner producer/customer building pairs, not observed payments.

| Measure | Baseline | First tuning | Later improvement/research tuning | Current acquisition/foundations |
|---|---:|---:|---:|---:|
| Completed Quarters | 325 across five games | 65 | 56 | 67 |
| Matching non-City-Center customer district adjacent | 80/325 (25%) | 51/65 (78%) | 37/56 (66%) | 45/67 (67%) |
| At least one functioning eligible sales relationship, including Granaries | 99/325 (30%) | 42/65 (65%) | 34/56 (61%) | 36/67 (54%) |
| Eligible building-pair links | 106 total / 21.2 per game | 69 | 46 | 47 |

At225 the current game has functioning customer buildings beside 8/21 Bakeries
(Markets), 1/23 Textile Workshops (Lighthouses), 5/19 Tailors (Markets), 8/19
Tailors (Temples), and 0/5 Fashion Houses (Amphitheaters). One of nine Cafes has
a Ferris Wheel customer; none has a Zoo. These ratios require the source building
to function too. Among the same source cohorts, appropriate customer districts
exist beside 9/21, 2/23, 7/19, 8/19 and 0/5 respectively. Stage4 customer population
must be at least5. Pillaged/incomplete customer districts/buildings are excluded;
CityCenter defense pillage does not disqualify an intact Granary. Direct native
district/building replacements are included. An unrelated Wonder is not a customer.

No Base-material or Service-civic gate is imposed on ordinary goods sales.
Native Service flags are a separate measure. No cumulative transaction count,
actual transferred Gold, or causal improvement is established by this comparison.

Sources under Desktop/Codex: csc-ai-paired-standard-20261016/game-01..05,
csc-ai-placement-v1-20261017/trial/game-01,
csc-ai-improvement-research-20261019/trial-v1b/game-01, and
csc-donated-both-diagnostic-20261023/run-02/resume-114-light-v16/game-01.
The uniform offline calculation and detailed result are retained in the23October
session output as compare-customer-adjacency.py and customer-comparison-225.json.
The maintained route definitions are project/tools/ai_baseline/sales_prevalence.py.
