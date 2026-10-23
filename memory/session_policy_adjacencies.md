# Policy return adjacencies — 20 October 2026

User authorized doubling Bakers/Tailors customer returns with the corresponding
vanilla adjacency cards, counting every adjacent owned Quarter, and merging
native/custom placement UI totals. Implemented in Quarter registry declarations,
shared schema/processor, shared presentation/optional Firaxis formatting argument,
and native policy refresh events. No new ModBuddy actions or dependency.

Durable behavior and validation:
`project/docs/integrations/csc-adjacencies.md`, policy-card section.
Regression: `project/tools/adjacencies/test_policy_returns.py`.
Frozen and current cached DB copies: 9 mappings / 20 unique+base rules / 200 bits /
220 gameplay+UI cases pass. Baseline 61-rule parity / 1,465 cases and 6 localized
placement comparisons pass. Quarter SQL style and action checks pass.

Tailors implementation contract amended under user's explicit request; refreshed
only the Bakers gameplay SQL reference lock. Pre-existing localization lock and
canonical Bakers materials mismatch still prevent full Tailors validator success.
No acceptance metadata changed. No installation, game mutation or new game run;
ModBuddy rebuild and in-game confirmation remain pending.
