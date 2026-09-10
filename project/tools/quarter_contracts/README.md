# Quarter contract validator

Run from the repository root:

```powershell
py -3 project/tools/quarter_contracts/validate_quarter.py tailors
```

The validator checks schemas, canonical/reference hashes, design traceability,
pattern IDs, the localization pattern catalog and its exact template slots,
phase gates, phase-validation coverage, approved design-slice hashes, preserved
ModSupport mappings, declared ModBuddy wiring, Bakers-derived SQL style for
outputs that exist, and the clean-start rule. Open design/engine decisions are
warnings until their phase is approved.

Quarter icon layout is an implementation convention inherited from the gameplay
catalog: district normal/FOW use 0/1, stage 2/3/4 buildings use 4/5/6, and stage
2/3/4 services use 8/9/10. Quarter contracts may declare a narrow override;
`design.yaml` does not repeat the default layout.

Building art validation is cumulative by stage. Every Quarter must have exactly
one `BuildingChain` in `CSC_Buildings.artdef`: the Quarter district is referenced
under `Districts`, while Stage 2, 3, and 4 buildings occupy `Buildings (Level
1)`, `Buildings (Level 2)`, and `Buildings (Level 3)` respectively. Future level
collections may be present but empty until that stage is implemented.

Each implementation phase has its own explicit gate. After approval, establish
the phase's red state and then converge its cumulative outputs with:

```powershell
py -3 project/tools/quarter_contracts/validate_phase.py tailors foundation
```

The command requires the phase to be approved or implementing, verifies every
required output, runs strict SQL and statement-boundary checks, executes the
Quarter-specific semantic assertion module, verifies localization generation,
and checks exact ModBuddy Content/action/load-order/criteria wiring. It does not
launch Civilization VI.

Before implementation handoff, set the phase gate to `ready_for_review` and run:

```powershell
py -3 project/tools/quarter_contracts/validate_phase.py tailors foundation --handoff
```

The Tailors assertion module deliberately starts each phase with a red sentinel.
Replace only the approved phase's sentinel with executable checks for all of its
static assertions before writing the gameplay implementation. Earlier phase
checks remain active as later phases extend the cumulative SQL and text files.

Validate the localization pattern catalog directly with:

```powershell
py -3 project/tools/quarter_contracts/validate_localization_patterns.py
```

Render a reviewed pattern by supplying every slot explicitly:

```powershell
py -3 project/tools/quarter_contracts/validate_localization_patterns.py `
  --render LP.LOCAL.EXCHANGE_BULLET `
  --slot "received=1 [ICON_Culture] Culture" `
  --slot "target=Textile Workshop" `
  --slot "provided=1 [ICON_Production] Production and +1 [ICON_Gold] Gold" `
  --bullet-marker -
```

Rendering rejects missing and extra slots. Exact matching normalizes only line
wrapping, repeated whitespace, and Markdown's interchangeable `-`/`*` bullet
marker; wording, punctuation, icon tokens, and transaction direction remain
significant. Building-description pattern sequences are checked in this order:
material/input, local exchange, customer output, trade output, then service
text. Citizen slots, specialist yields, and intrinsic local/regional Amenities
are omitted from authored building descriptions because Civ VI renders those
database fields automatically below the description. Transaction effects on a
different city, such as a trade-route origin Amenity, remain explicit.

Run the SQL style test directly with:

```powershell
py -3 project/tools/quarter_contracts/validate_sql_style.py `
  "Civ Supply Chains/Data/CSC_Q_TAILORS.sql" `
  --profile core --quarter tailors
```

Apply the exact row layout required by that check with:

```powershell
py -3 project/tools/quarter_contracts/format_sql_layout.py `
  "Civ Supply Chains/Data/CSC_Q_TAILORS.sql"
```

The formatter aligns simple tuple columns and the values following wide
`/* ColumnName, */` comments. It is deterministic and idempotent; new Quarter
SQL must already match its output for validation to pass.

`validate_quarter.py` remains the contract/preflight command. Use
`validate_phase.py` for all implementation and handoff checks once a phase is
approved; the old clean-start bypass is not the phase-completion gate.
