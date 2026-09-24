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

Quarter contracts own gameplay, localization, core build wiring, UI identifiers,
and the complete Service requirement sets consumed by optional integrations. The
optional CSC Art Pack owns alternate-art property modifiers and attachments, the
Lua property mirror, GamePropertyRanges, selection rules, models, materials,
ArtDefs and XLP entries. Core Quarter validators enforce that ownership boundary;
validate the Art Pack package separately from the gameplay phase gates.

## Wonder-hosted Services

When a Service destination in `design.yaml` declares `placement: wonder_tile`, the
owning implementation requirement must use
`GP.SERVICE.WONDER_HOSTED_EXACT_PLACEMENT` and declare a structured
`wonder_service_binding`. Contract validation then requires one distinct internal
Service building and activation property per Wonder, `DISTRICT_WONDER` placement
with zero Citizen slots, a deterministic exact-plot gameplay reconciler, and UI
outputs for City Breakdown plus the base and Simple UI Adjustments plot tooltips.

## Trade-route city-yield presentation

When a domestic-trade design node declares `origin_yields`, the owning
implementation requirement must use `GP.TRADE.CITY_YIELD_PRESENTATION` and
declare `trade_route_yield_presentation`. Each reclassified modifier gets one
explicit `CSC_TradeRouteYieldPresentation` entry; the UI must consume that
registry rather than infer eligibility from modifier names. The registry schema
and rows live in a dedicated `ModSupport` SQL output, never in core shared or
Quarter SQL. Its `UpdateDatabase` action and the `Suk_YieldTT` replacement are
both gated by `SimpleUIAdjustmentsMod`, with the database action loading first.
Registry entry IDs use the economic tier rather than the implementation building:
`CSC_<QUARTER>_IMPORT_CONSUMER_<YIELD>` for Stage 3 and
`CSC_<QUARTER>_IMPORT_SPECIALTY_<YIELD>` for Stage 4. Modifier and property IDs
remain free to identify the concrete source building.
Contract validation matches the entries' aggregate yield types and amounts to
`origin_yields`, rejects reused entry/modifier/property identities, and enforces
that conditional wiring. Phase assertions then trace each live row through its
modifier arguments and `REQUIREMENT_PLOT_PROPERTY_MATCHES` property gate.

The gameplay path must call
`CityBuildQueue.CreateBuilding(buildingIndex, hostWonderPlotIndex)` and must not use
an SQL building-grant modifier for Wonder variants. SQL grants cannot distinguish
multiple instances of `DISTRICT_WONDER`; they place compatible buildings in the
city's first Wonder district. UI must derive and display each Service's actual
stored plot, never a desired or spoofed host. Conventional destinations such as a
Theater Square with an Amphitheater retain the normal persistent SQL-grant path.

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
