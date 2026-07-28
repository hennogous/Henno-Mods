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
- phase/control gate agreement;
- output key ownership;
- open-decision references;
- exact retained ModSupport resource-to-class mappings;
- absence of gameplay outputs before any implementation phase is approved.

Open engine decisions are warnings while the contracts are under review. They
become phase blockers through `control.yaml`.

## Static implementation validation

The first approved phase must extend the validator to inspect generated SQL and
localization. At minimum, later checks must verify:

- identifier and row uniqueness;
- exact values from the design contract;
- companion-file separation for Gold and M&C;
- complete requirements, arguments, and modifier attachment chains;
- direct one-level replacement coverage;
- ModBuddy Content/action wiring and load criteria;
- localization keys and gameplay-to-text coverage;
- no unapproved pattern or exception.

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

Every implementation requirement contains its own `runtime_scenarios`. Execute
them using FireTuner where practical and record the result before completing its
phase. Boundary cases are mandatory for population thresholds, radius, unit-era
limits, service prerequisites, replacement buildings, route stacking, and
conditional integrations.

Art validation is a separate final phase. Existing Tailors art is preserved, but
no art property contract is inferred before gameplay behavior is accepted.
