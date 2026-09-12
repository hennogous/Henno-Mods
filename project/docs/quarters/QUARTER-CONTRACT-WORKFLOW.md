# Quarter contract workflow

> **Documentation audit — 2026-09-12: Needs refresh.** The clean Tailors baseline and blanket deferral of art are obsolete. control.yaml records foundation, materials_and_stage2, stage3 and art_integration ready_for_review with user approvals; acceptance is separate. Its phase approval_rule supersedes the old whole-contract approval sequence.
> Classification: Quarter workflow. See the [full audit](../DOCUMENT-AUDIT.md).

This workflow turns a Quarter design into gameplay without allowing the
implementation to drift toward a generic interpretation. Tailors is the first
clean implementation under it. Once Tailors is accepted, its implementation can
replace Bakers as the normal structural reference while Bakers remains a source
for mechanics Tailors does not exercise.

## The three Tailors contracts

`project/specs/tailors/design.yaml` is a literal machine transcription of the
canonical public design. It records intended values and relationships but makes
no engine decisions.

`project/specs/tailors/implementation.yaml` binds every design statement to:

- one or more classified reference patterns;
- the files that will implement it;
- exact static assertions;
- user-owned, later in-game acceptance scenarios;
- required localization structures;
- unresolved engine decisions that must not be guessed.

`project/specs/tailors/control.yaml` locks the hashes of the canonical and Bakers
references, records an exact design-subtree hash for each approved phase, gates
implementation and handoff states, and records exceptions.

The result has one source for intent, one source for implementation obligations,
and one source for change control. Traceability is embedded in each requirement
instead of being copied into a separate matrix.

## Is this TDD?

The contract stage is acceptance-test-driven development: expected behavior,
static assertions, runtime scenarios, localization obligations, and code style
are written before gameplay code. Each implementation phase becomes conventional
TDD when its validators are first run against the absent/incomplete output, fail
for the expected reasons, and are then made to pass by the smallest compliant
implementation.

The contracts alone are not a substitute for TDD. Agent implementation handoff
requires the contract, SQL, text, style, and other automated checks to pass. The
listed `runtime_scenarios` are acceptance-test specifications for the user to run
later; they do not require the implementation agent to launch Civ VI or block the
current handoff. Final gameplay acceptance still requires the user to pass those
scenarios.

## Authority and conflict handling

1. The canonical Quarter design decides intended behavior.
2. Its approved design contract is the exact machine-readable transcription.
3. Applicable reusable Bakers patterns decide implementation structure and text
   form.
4. Bakers-only behavior is forbidden unless the Quarter design independently
   requires it.
5. A real conflict is recorded in `control.yaml`; it is never silently resolved.

“Applicable” is therefore a reviewed classification, not an invitation to copy
the whole Bakers file.

## Tailors restart sequence

The clean baseline intentionally contains no Tailors gameplay SQL, gameplay
localization, action wiring, adjacency processor entries, or art-property
scaffolding. The public Tailors design and existing art are preserved. Existing
optional-mod resource mappings are also preserved and validated as inputs:

- Hemp from Cannabis & Hemp;
- Llamas from Latin American Resources;
- Bamboo and Gold from Resourceful 2;
- Cashmere from Resourceful 2 Assets;
- Gold from Sukritact's Resources.

Implementation proceeds phase by phase:

1. `foundation`
2. `materials_and_stage2`
3. `stage3`
4. `stage4`
5. `compatibility`
6. `localization_and_integration`
7. `art_integration` (deliberately deferred)

Each phase is reviewed before its gate becomes `approved`. Only then are its
outputs written. An approved phase moves through `implementing`,
`ready_for_review`, and finally `accepted`; those states are never inferred.
The implementation agent may use `ready_for_review` only after the phase
validator passes. The user later closes gameplay acceptance by running the
listed FireTuner or in-game scenarios and explicitly accepting the phase.

## How to use it

First validate the proposed contracts:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors
```

The same command automatically applies the Bakers-derived SQL style profile to
each Tailors gameplay SQL file as soon as that output exists.

The user's approval surface is `project/specs/tailors/design.yaml`, reviewed one
phase-sized subtree at a time. The implementation agent derives and maintains
the pattern catalogs, implementation manifest, assertions, and control record.
An approved phase stores a canonical hash of only its referenced design
subtrees, so edits to later unapproved stages do not invalidate it. Resolve each
`open_engine_decisions` entry before approving its named phase and record settled
choices in `resolved_engine_decisions` so later agents do not reopen them.

When a phase is approved, implement only the requirements listed under that
phase. First run the phase validator to establish the expected red state:

```powershell
py -3 project/tools/quarter_contracts/validate_phase.py tailors foundation
```

Replace that phase's red semantic sentinel in
`project/tools/quarter_contracts/quarter_checks/tailors_assertions.py` with
executable checks derived from every static assertion, then implement until the
same command passes. Before handoff, move the gate to `ready_for_review` and run:

```powershell
py -3 project/tools/quarter_contracts/validate_phase.py tailors foundation --handoff
```

The phase validator checks cumulative output completeness, strict SQL structure
and complete statement boundaries, executable semantic assertions, exact
localization generation, and ModBuddy Content/action/load-order/criteria wiring.
Later phases extend the same files while retaining all earlier checks.

## Promoting Tailors to the reference

After Tailors passes all non-art runtime scenarios:

1. classify which Tailors structures are genuinely universal;
2. replace Bakers anchors with Tailors anchors where Tailors is cleaner;
3. retain specialized Bakers catalog entries for mechanics Tailors lacks;
4. generate the next Quarter contract from the catalogs, never by cloning SQL;
5. continue parameterizing only behavior proven by at least one completed
   implementation.

This makes later Quarters faster without treating an accidental implementation
detail as a permanent template rule.
