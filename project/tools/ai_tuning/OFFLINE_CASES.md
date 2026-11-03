# Archived chain decision cases

`offline_cases.py` reads the closed 25 October turn100 mechanism-study schema.
It does not connect to Civ, read live caches, import the game controller or modify
the source archive. It is not a general current-game planner or simulation.

Run with bundled Python `-B -X utf8`:

```text
offline_cases.py <closed-study-directory> --output <Desktop-Codex-output>/cases.json
test_offline_cases.py
```

The archive must contain natural-exposure100.json,
coimbra-customer-decision-review.json and quantified-outcomes.json. Outputs record
SHA256 provenance and JSON pointers. Same-city comparisons join player, city ID
and district type. Private values remain separate from real adjacency; missing
yields remain unknown. Pairs are not unique decisions or whole-site profit
comparisons. Duplicate option identities fail explicitly.

See [case review and evaluator contract](../../docs/research/mods/csc-ai-offline-chain-cases-20261028.md)
for the observed cases and limitations. New source schemas require explicit
adaptation; never silently rerun a game to repair a reporter.
