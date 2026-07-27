# Quarter Contract Validation

`project/tools/quarter_contracts/validate_quarter.py` validates the controlled
inputs and declared source evidence for a Quarter implementation.

## Dependencies

- Python 3.11 or later.
- PyYAML (`py -3 -m pip install PyYAML`) for the existing YAML design specs.

Shadow's normal Python environment already provides PyYAML.

## Modes

```powershell
# L0: control, paths, hashes, cross-spec identity, applicability and traceability
py -3 project/tools/quarter_contracts/validate_quarter.py tailors

# L0 + declared L1 assertions for one phase
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --phase phase_3_textile_workshop

# L0 + repository-wide localization generation and ModBuddy action consistency
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --generated

# Approval gate; intentionally fails for draft controls
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --ready
```

The validator never marks a runtime scenario as passed. Runtime evidence must
be recorded from runtime database inspection or FireTuner.

## What L0 checks

- Required control and contract files exist and parse.
- Design, gameplay, art, and control Quarter identities agree.
- Internal spec paths resolve.
- Bakers reference hashes still match the reviewed snapshot.
- Every applicability entry has a valid classification and a real source
  anchor.
- Traceability IDs are unique.
- Every design path resolves in the approved design YAML.
- Every Bakers pattern reference resolves to an applicability entry.
- Every traceability row declares outputs, static checks, and runtime checks.
- Phase output files fit the phase allowlist and not its denylist.

## What phase assertions check

Traceability rows may declare:

- `contains`: exact source fragments that must exist;
- `not_contains`: exact source fragments that must not exist;
- localization `contains` and `ordered_contains` assertions scoped to a LOC key.

These are reviewable source proofs, not a substitute for SQL execution. They
are intentionally explicit: the validator does not infer design intent from
identifier similarity.

## Exit behavior

- Errors produce exit code `1`.
- A valid draft produces exit code `0` in ordinary mode.
- `--ready` produces exit code `1` until Henno has approved the control and all
  readiness fields are complete.

Use `--json` for machine-readable output.
