# Quarter contract workflow

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
- runtime scenarios;
- required localization structures;
- unresolved engine decisions that must not be guessed.

`project/specs/tailors/control.yaml` locks the hashes of the design and Bakers
references, records contract approval, gates implementation phases, and records
explicit exceptions.

The result has one source for intent, one source for implementation obligations,
and one source for change control. Traceability is embedded in each requirement
instead of being copied into a separate matrix.

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
outputs written. A phase ends with static validation and its listed FireTuner or
in-game scenarios.

## How to use it

First validate the proposed contracts:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors
```

Review these files in order:

1. `project/specs/tailors/design.yaml`
2. `project/specs/reference/bakers-gameplay-patterns.yaml`
3. `project/specs/reference/bakers-localization-patterns.yaml`
4. `project/specs/tailors/implementation.yaml`
5. `project/specs/tailors/control.yaml`

During review, change contract approval states only when the corresponding file
is accepted. Resolve each `open_engine_decisions` entry before approving the
phase named by `resolution_required_before_phase`.

When a phase is approved, implement only the requirements listed under that
phase. Use:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors --no-clean-start-check
```

while approved outputs exist. The bootstrap switch is temporary; output-aware
SQL and localization validators will be added alongside the first phase so later
phases can verify exact row-level obligations.

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
