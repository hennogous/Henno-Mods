# Stronger Quarter map planning and complementary customer terrain

Henno asks the planner to recognise the enduring value of material clumps,
Base+Spec, useful river/Mill terrain and space for good customer districts.
This extends Problems1.1–1.4/1.8 and2.1. Settling/City Center placement is unchanged.

## Integrated policy

The economic ledger still prices real site yields and ordinary future building
transactions over50 turns. Future customer districts supply no adjacency or
transaction income. A separate spatial preference captures lasting map potential:

| Component | Native utility preference |
|---|---:|
| +2 actual/planned-local-Mill adjacency |48 |
| +3 / +4 / +5 / +6+ |144 /288 /432 /576 |
| Both Base and Spec |64 |
| Additional Base deposits beyond the first |24 each, maximum48 |
| Additional Spec deposits beyond the first |16 each, maximum32 |
| Compatible future customer layout |0–96 |

Fractional2→3 interpolates48→144. No-Base/below2 options remain deferred;
economic losses after protection deductions receive no positive spatial bonus.
The final bid remains capped at4096 utility. Each utility point is256 Q8.

The previous15 November adjustment used48/96/192/... and16 for Spec. The
completed250 used0/96/192/... and16 for Spec. Preserve those treatments when
comparing results. Archived winners range119.79–2537.87, but archived captures
do not retain the full simultaneous losing-site surface. They cannot establish
a median same-city site margin. These stronger bands are initial calibration;
new top-two-per-city/type logs will directly measure that margin.

## Concrete customer footprints

`EconomyFacts.CustomerOptions` shares the loaded all-stage sales/provider registry
with the existing feasibility planner. It enumerates adjacent owned customer
footprints and checks the owning city's radius3, actor/replacement family,
geometry, visibility, resource absence and supplier protection. Customer unlocks
and current population capacity do not erase future geometric potential.

Native `GetDistrictAdjacency` supplies ordinary hypothetical adjacency for the
explicit AI/city/district. This follows loaded Commercial Hub, Holy Site, Harbor,
replacement and optional-mod rules. Private AI yields are excluded. Unavailable reads and snapshots more than
one turn behind Core earn no terrain preference. One-turn UI
phase lag is counted explicitly; Core still supplies current footprint checks.
This is current-map hypothetical
adjacency, not a simulation of every feature removed by a future Quarter or
future customer. No bonus is assigned for an unbuilt Wonder or City Center.

One candidate earns16 plus8 per ordinary adjacency point, capped at four points.
Subtract8 per point it trails the best eligible same-city alternative, capped
at four. Also subtract8 per point by which the Quarter footprint itself would
be a better customer site, capped at four. Clamp the result to0–48.

Keep the best two footprints per family, then compare all singles and compatible
pairs. A pair must use different tiles and families, so layout credit is at most96.
These are alternative plans, not reserved tiles or guaranteed future buildings.

Only each city/Quarter type's leading complete bid can propose customer preparation.
Current native legal targets and population room are checked again. Same-city
offers leave one slot for the proposed Quarter; offered customers consume the
remaining offer budget. A cross-plan pass prevents conflicting customer types
on one tile and avoids leading Quarter footprints. Delayed/unlocked-later
geometry earns potential credit but cannot publish an immediate customer bid.
The old16-point early customer offer is disabled in this complete-value route.
Existing native SQL adjacency continues guiding customers beside built Quarters.

## Performance and evidence

Maps and native adjacency reads are cached once per publication/city/type/plot,
shared by both Quarters. Each city/type scans only radius3. Static actor metadata
uses the existing cache; mutable map/score facts expire each publication.
The pair search keeps two candidates per family; no empire-wide layout search.

Main-mod `CSC_AI_SPATIAL_BID` records the best two Quarter bids per city/type:
economics, adjacency/material/layout preferences, protection deductions, final
value and proposed customer footprints. `CSC_AI_SPATIAL_WORK` records customer
maps, native reads, unavailable inputs, options and economic-pass CPU time when
the Lua clock is available. These record proposals; native receipts and actual
foundations retain their existing separate observers.

Offline qualification:48 economic/SQL/spatial checks plus18 publisher/package/
observer checks pass. Coverage includes native terrain and alternate-site cost,
private-yield exclusion, shared-footprint/family conflicts, protection, current
capacity/legal targets, stale reads, bounded material bonuses, economic-loss gates
and the real Quarter publisher's separate economic/spatial/customer outputs.

## Fresh Continents comparison

Henno emphasises native saving toward valuable paid footprints, especially with
strong starting income. The existing native savings/purchase route remains the
decision owner. The purchase invoice is already deducted by the economic ledger;
no subsidy is added. Frontier offer logs now include starting adjacency, starting
Gold, estimated Quarter readiness and gross adjacency-Gold payback after Quarter
completion. Production and delayed Mill effects are kept separate from treasury
payback. Match offers to the passive native savings/account, payment and foundation
records to see where the route advances or stops. No API change is needed.

Pre-run upstream check15 November: WildW develop remains2986a746b396; master
e59b5aa910c8. Use the unchanged qualified local CE400e6755 binary for our APIs.
No upstream PR is submitted.

Authorised ordinary Small/Prince/Online game through250, using the same selected
map/game seeds18461107/29461107 and CL/R2/Suk stack as the completed comparison.
Main CSC is the only tuning policy. Reuse the accepted frozen gameplay/art base
and unchanged qualified CE; overlay reviewed main AI modules and UI fact bridge.
No external bids, research grants, placed buildings or diagnostic policy modes.
Shared controller owns all game/console actions; check about every15 minutes.

Artifacts: `C:/Users/Shadow/Desktop/Codex/csc-ai-spatial-layout-20261115/`.
Launch/result state is maintained in STATUS and session memory. Compare Quarter
counts, placement-time adjacency, Base/Spec, customer relationships, chains,
ordinary districts and timing with the preceding seven-Quarter/582-chain-turn run.

### Startup correction before the full comparison

`continents250-01` verifies identical initial map, starts and units, and the
25-material/14-provider loaded audit. Spatial work reports every terrain read
unavailable: exact Core/UI turn equality was too strict. The controller's
turn45 phase record shows Core45 while UI44. A supported source-update request
preserves that finite operation and closes the native process with exit0,
verified package/preference restoration and no remaining owners. This startup
is retained as a stopped trial, not a completed250 comparison.

The correction accepts UI clocks equal to Core or one behind and records
`laggedReads`; older/future snapshots still defer. Native construction eligibility
and Core ownership/resource/geometry checks remain authoritative. A regression
executes both the accepted one-turn phase case and the rejected older case.
Initial main-mod `os.clock` readings are constant0; corrected timing diagnostics
report unavailable(-1) rather than measured zero. Controller wall timings and
native read counts remain available. Fractional customer preferences are rounded
to integer Q8 at publication. The corrected full restart uses `frozen02`.

Reusable engine learning is recorded as AI-N132 in the civ6-ai skill,
commit bb470f5 (pushed). CSC policy and calibration stay in this report.
