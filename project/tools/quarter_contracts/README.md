# Quarter contract validator

Run from the repository root:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors
```

The validator checks schemas, canonical/reference hashes, design traceability,
pattern IDs, phase gates, preserved ModSupport mappings, Bakers-derived SQL
style for outputs that exist, and the clean-start rule. Open design/engine
decisions are warnings until their phase is approved.

Run the SQL style test directly with:

```powershell
py -3 project/tools/quarter_contracts/validate_sql_style.py `
  "Civ Supply Chains/Data/CSC_Q_TAILORS.sql" `
  --profile core --quarter tailors
```

During an approved implementation phase, use `--no-clean-start-check` if earlier
approved outputs already exist. The final implementation validator will later
replace this bootstrap switch with per-output phase ownership checks.
