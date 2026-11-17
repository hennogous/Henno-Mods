# Implementation contracts follow shared SQL architecture — 17 November 2026

Henno requested contracts/validators that guide future Quarter implementations
into the current seven-section layout and shared economic pipeline.

The shared ownership/loading contract is
project/specs/reference/csc-shared-sql.yaml. Implementation schema requires its
shared_sql_contract pointer. Tailors contract now binds canonical material and
building catalogues, generated compatibility registries, shared_economy_schema,
current grouped actions and Stage 3 Q8 units (256, calibrated input 0.101).
Reusable Bakers patterns describe CSC bundled adjacency and shared compilation;
obsolete MAB instructions and duplicate atlas metadata were removed.

sql_architecture.py enforces table sections, batching, every literal definition's
column labels, generated-vs-authored ownership, persistent schema ownership,
single file registrations/criteria/phases, shared dependencies and declarations
before compilation. validate_sql_architecture.py is a focused maintenance CLI;
style/contract/phase validators also use these checks. It never advances approval
gates or refreshes unrelated design hashes.

Grouped declarative actions are accepted per file while duplicate ownership,
changed criteria and merged UI/gameplay contexts fail. Route UI validation now
requires its DB projection after the final route reader, instead of numerically
comparing DB and UI phases. Corrected stale Fashion fixtures load actual compiled
population/route definitions; all 21 tests now pass. Duplicate validator functions
were identical and removed without changing their behavior.

No gameplay data, Lua policy or native API changed. No game/Tuner/controller used.
Preserve existing WIP, particularly Tailors PLUNDER_GOLD, Pedia-related phase
assertions and design/localization locks. The remaining global contract failure
is existing canonical-design/localization hash drift; do not silently reapprove it.

Validation: focused architecture CLI and 17 architecture regression cases pass;
full Quarter suite 200/201 (one existing global design/localization lock failure),
83 transaction tests and 9 ModBuddy tests pass. No approvals or hash locks reset.
