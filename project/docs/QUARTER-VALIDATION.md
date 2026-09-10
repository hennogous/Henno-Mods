# Quarter contract and build validation

Validation is layered. A passing YAML check does not imply that Civ VI gameplay
is correct.

## Contract validation

Run:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors
```

It checks:

- all YAML against the three JSON Schemas;
- the canonical design hash;
- every locked Bakers gameplay/localization hash;
- every design reference;
- complete design-ID implementation coverage;
- gameplay and localization pattern IDs;
- rejection of Bakers-only patterns;
- phase/control/validation-contract agreement;
- exact hashes of the design subtrees approved for each active phase;
- explicit approval, readiness, and acceptance metadata for active phases;
- output key ownership;
- open-decision references;
- exact retained ModSupport resource-to-class mappings;
- absence of gameplay outputs before any implementation phase is approved;
- declared ModBuddy action identities, file paths, load orders, and criteria.

Open engine decisions are warnings while the contracts are under review. They
become phase blockers through `control.yaml`.

## Visual and architectural SQL style

`validate_quarter.py` automatically runs the profile declared for each existing
Tailors SQL output. The standalone form is:

```powershell
py -3 project/tools/quarter_contracts/validate_sql_style.py `
  "Civ Supply Chains/Data/CSC_Q_TAILORS.sql" `
  --profile core --quarter tailors
```

The style test is Bakers-derived but does not compare raw whitespace or demand an
identical file. It checks the reusable house structure:

- CSC header and author;
- major and subsection delimiter hierarchy;
- canonical core section order;
- uppercase, column-one SQL keywords;
- per-value comments for wide Districts and Buildings rows;
- no trailing whitespace in new Quarter files;
- canonical Bakers-derived alignment for simple `INSERT ... VALUES` tables;
- vertically aligned values in wide `Districts` and `Buildings` comment blocks;
- canonical Bakers-derived alignment for simple `INSERT ... VALUES` tables;
- vertically aligned values in wide `Districts` and `Buildings` comment blocks;
- no Bakers identifiers in Tailors;
- Gold-only and M&C companion boundaries;
- no redefinition of infrastructure owned by `CSC_Q_ALL.sql`.

This test improves reviewability and catches architectural drift, but it cannot
prove modifier semantics or gameplay behavior.

The alignment rules are auto-fixable and idempotent:

```powershell
py -3 project/tools/quarter_contracts/format_sql_layout.py `
  "Civ Supply Chains/Data/CSC_Q_TAILORS.sql"
```

The normal phase validator runs the same layout function in check mode, so a
future edit that collapses the SQL back into compact tuples fails before handoff.

The alignment rules are auto-fixable and idempotent:

```powershell
py -3 project/tools/quarter_contracts/format_sql_layout.py `
  "Civ Supply Chains/Data/CSC_Q_TAILORS.sql"
```

The normal phase validator runs the same layout function in check mode, so a
future edit that collapses the SQL back into compact tuples fails before handoff.

## Per-phase implementation validation

Every phase has a separate approval and an executable assertion suite. Start an
approved phase with:

```powershell
py -3 project/tools/quarter_contracts/validate_phase.py tailors foundation
```

The initial failure is the TDD red state: missing outputs, missing action wiring,
and the phase's explicit semantic-test sentinel. Replace only that phase's
sentinel with executable assertions, implement the phase, and rerun until green.
For handoff, the control gate must be `ready_for_review` and this must pass:

```powershell
py -3 project/tools/quarter_contracts/validate_phase.py tailors foundation --handoff
```

The phase checks verify:

- identifier and row uniqueness;
- exact values from the design contract;
- companion-file separation for Gold and M&C;
- complete requirements, arguments, and modifier attachment chains;
- direct one-level replacement coverage;
- ModBuddy Content/action wiring and load criteria;
- localization keys and gameplay-to-text coverage;
- no unapproved pattern or exception.

The user approves the relevant `design.yaml` slice. The validator recomputes its
hash from the phase's `design_refs`; implementation and pattern manifests are
agent-maintained and validated as live derivations rather than requiring a
second user review.

They also verify every required file is registered once in the source ModBuddy
action manifest and as project Content, with the contract's exact action type,
load order, and criteria. The action JSON must round-trip into the `.civ6proj`.

The Bakers file is an implementation reference, not a golden text diff: Tailors
must match applicable structures while containing only Tailors behavior.

## Database and UI validation

Build/load checks include:

- ModBuddy action manifest agrees with `.civ6proj`;
- database and localization logs contain no Tailors errors;
- all LOC keys resolve;
- conditional companions load only under their intended mode or mod;
- route preview, route execution, UnitPanel display, and service discovery agree.

## Runtime validation

Every implementation requirement contains its own `runtime_scenarios`. These are
user-owned and are not required for the implementation agent's
`ready_for_review` handoff. Execute them later using FireTuner or normal in-game
testing and record the result before explicitly accepting the phase. Boundary
cases remain mandatory for population thresholds, radius, unit-era limits,
service prerequisites, replacement buildings, route stacking, and conditional
integrations.

Art validation is a separate final phase. Existing Tailors art is preserved, but
no art property contract is inferred before gameplay behavior is accepted.
