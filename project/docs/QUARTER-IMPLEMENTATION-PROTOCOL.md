# Quarter Implementation Protocol

This protocol governs gameplay implementation for every CSC Quarter after the
Bakers' Quarter. Its purpose is deterministic translation, not creative design.

## Authority model

Three authorities apply on different axes:

1. **Quarter design — what.** The approved public design and structured design
   spec define identities, values, scopes, gates, participants, and effects.
2. **Bakers reference — how.** The pinned Bakers files define applicable SQL
   architecture, modifier and requirement construction, naming, file
   separation, replacement handling, and implementation style.
3. **Bakers localization — how it is said.** The pinned Bakers Markdown defines
   applicable ordering, transaction phrasing, icons, line breaks, service
   framing, and Civilopedia structure.

Existing partial Quarter code is evidence, not authority. Retain it only where
it independently conforms to all applicable authorities.

No authority silently overrides another. If they cannot be reconciled on their
own axes, implementation stops and records a conflict for Henno.

## Review states

Each Quarter has an implementation-control file with two separate fields:

- `review_status`: `draft`, `approved`, or `superseded`.
- `implementation_ready`: Boolean authorization gate.

A Quarter is authorized for gameplay work only when `review_status` is
`approved`, `implementation_ready` is `true`, every required input is pinned,
and the readiness validator passes. A structurally valid draft is not approval.

Changing an approved design or reference lock invalidates approval until Henno
reviews the new inputs.

## Required artifacts

Before a phase is implemented, the Quarter must have:

- `<quarter>-design.yaml`: structured design truth.
- `<quarter>-gameplay.yaml`: phase scope, outputs, and verification contract.
- `<quarter>-implementation-control.json`: approval state and pinned inputs.
- `<quarter>-bakers-applicability.json`: classification of each relevant
  Bakers pattern.
- `<quarter>-traceability.json`: requirement-to-source-to-output-to-test map.
- A Quarter localization Markdown source.

The applicability classification vocabulary is:

- `invariant`: preserve the structure without semantic change.
- `parameterized`: preserve the structure; substitute approved design values.
- `conditional`: include only because an explicit design condition applies.
- `quarter_specific`: design requires a different implementation family.
- `shared`: use existing shared infrastructure instead of cloning it.
- `not_applicable`: deliberately omit, with a reason.
- `superseded`: the Bakers fragment is historical and must not propagate.

No relevant Bakers pattern may remain unclassified when a phase is approved.

## Phase workflow

### 1. Reconcile

Read the live design, gameplay contract, pinned Bakers sources, localization
contract, and existing Quarter code. Do not edit gameplay files yet.

Produce or update the applicability and traceability manifests. Every mechanic
must have a stable requirement ID. Every requirement must point to:

- one or more exact design paths;
- one or more classified Bakers patterns;
- expected output files and source assertions;
- static verification;
- runtime verification, or an explicit reason runtime testing is impossible.

Unmapped design requirements and unproven output rows are blocking.

### 2. Approve

Henno reviews the design, applicability decisions, localization mapping, and
traceability coverage. Approval is recorded in the control file. An agent may
not grant approval to its own interpretation.

### 3. Implement

Implement one phase at a time and only in its allowed files.

Prohibited behavior:

- adding, omitting, rebalancing, simplifying, or generalizing mechanics;
- editing approved design inputs to make code pass;
- inventing a modifier/effect/requirement when no authoritative analogue is
  established;
- copying Bakers-specific behavior merely because it is nearby;
- placing Gold or M&C logic outside its declared load boundary;
- describing intended behavior that is not implemented;
- marking runtime verification complete from source inspection alone.

If a better implementation is discovered, record it as a proposed deviation.
Do not apply it until approved.

### 4. Validate

Validation levels are cumulative:

| Level | Evidence | Meaning |
|---|---|---|
| L0 | Contract validator | Inputs exist, agree, are pinned, and are traceable. |
| L1 | Phase/source assertions | Required identifiers and patterns exist in allowed outputs; forbidden patterns do not. |
| L2 | Generated/build checks | Localization and ModBuddy generated outputs are current; SQL/build smoke checks pass. |
| L3 | Runtime database checks | Loaded rows, arguments, requirements, and attachments match expectations. |
| L4 | FireTuner scenarios | Actual gates, transactions, scaling, replacements, pillaging, and services behave correctly. |

`implemented` requires L0–L2. `tested` requires the declared L3–L4 evidence.

### 5. Handoff

Every phase handoff reports:

- requirements implemented and their IDs;
- missing requirements;
- applicable Bakers patterns used;
- non-applicable Bakers patterns and reasons;
- localization patterns checked;
- deviations and conflicts;
- validation levels actually completed;
- tests not run and why.

The target acceptance summary is:

> Missing requirements: 0. Unauthorized mechanics: 0. Unresolved deviations:
> 0. Unverified completion claims: 0.

## Standard commands

From the repository root:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --phase phase_3_textile_workshop
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --generated
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --ready
```

The final command is expected to fail while the control file remains a draft.
