# Closing the Astra investigation gaps

Henno activated the goal to investigate and fix follow-through (1.6), economic
and relationship coverage (1.1/1.2/2.1), and acquisition (1.5), then run one fresh
Online250 game. Current policy is +2 minimum/+3 preferred, with Base, material
protection and current-customer-only adjacency. No upstream PRs.

## 1.6: Lingapura's first request is an explained production loss

The closed Pangaea archive identifies player4/city393221, founded153. On154,
Bakers42/plot2992 wins the district comparison at28831Q8 (112.62 utility):
4255 economic plus24576 placement preference. The request is admitted and
logged as3171. A Builder request3172 at120 wins the production queue155 and
occupies it through177; the city supplies about2.4 Production each turn.

The behavior tree reports Quarter waiting1..15 of15 turns. It expires before
the Builder completes. A Settler request3552 at212 is selected177. Later City
Lights Rural Community requests quote388/575/764. Keep the native waiting limit
and ordinary production competition intact.

Plot2917 was already owned154: direct adjacency1, prospective Mill total3, no
positive bid. On158 it becomes direct2/total4 and receives61538Q8 (240.38).
This means an improved offer, not a newly purchased site. The archived geometry
does not identify the precise added contribution; a component replay will read
the material/customer, staffing and producer facts. Both sites need a ledger
comparison before increasing their values.

Fresh Ghidra inspection and full-body parity qualify five current-XP2 consumers:

| Function | RVA | Bytes | Role |
|---|---:|---:|---|
| CheckForDistrict |3e0ee0 |610 |A single active district preparation tree gates a new nomination. |
| UnitRequestContract.Update |3fa5e0 |531 |Reads the request's existing site, updates value/ETA; no site retarget. |
| QueueNextBuild |3e8190 |2450 |Returns while production is occupied; validates and updates waiting requests before comparing their stored values at an empty queue. |
| UpdateWorkingContract |3ea990 |293 |Validates and updates the executing request. |
| ReconsiderDistrictConstruction |3e9630 |161 |Cancels pending same-type requests outside executing state5; not called by this investigation. |

Reference SHA324c51e9 and installed SHA092abfbb have identical complete bodies
for all five. Native retained-request traces are sparse because they log changed
values; absence of a trace is not absence of a request. The exact decompilation,
body hashes and native identity are archived below.

Astra's calibration review finds no capital-cost double charge or Q8 mismatch.
The model charges construction time, upkeep and one genuine land invoice.
It does subtract all income of a worked footprint, including terrain, while the
documented native improvement debit excludes plain terrain. It also forecasts
later building construction at unchanged current Production. The next targeted
read captures Site/plan/priced streams and an isolated unimproved-footprint
counterfactual, with unchanged weights, horizon and discount.

## Coverage fixes implemented; live qualification next

- **+2 publication:** an additional pre-screen still required geometry3 after
  the earlier threshold edit. The cheap geometry and final-price checks now
  share `E.MinimumAdjacency`; a full owned/frontier publication test covers2.
- **Same-city future customer:** the scanner uses the central snapshot's fresh
  population/inventory-checked capacity. Two free slots permit its modest pair
  preference; one or unknown slot omits only that extra customer preference.
  Quarter bids and future geometry remain available. Cross-city/exempt cases
  retain their normal path. Tests cover all four cases.
- **Incoming material exchange:** unconditional gameplay SQL at479 derives
  ordinary ImprovementModifiers from loaded Base/Spec tags and valid resource
  improvements. It fills missing R2/CL/Cashmere incoming Food/Culture roots,
  deduplicates existing attachments and preserves Industry/Corporation paths.
  It operates without CE; the model and real transaction can agree.
- **Provider placement:** the frozen loaded CL audit lists seven provider
  districts; none appears in either Quarter's private-yield connector edges.
  SQL now expands the loaded provider tags through the same deduplicated edge
  table, including replacements. Each adjacent existing Quarter supplies one
  private placement step, also when the partner is both customer and provider.
  No future-neighbor yield is added to the Quarter forecast.

37 economic/SQL tests, six main-publisher fixtures, ten real-core scanner groups,
and eleven continuation/component-observation tests pass. The new gameplay SQL
is registered independently of CE before connector480. Manifest regeneration
passes. Scoped index patches preserve unrelated existing manifest edits.

## Next live work

Use the original Pangaea150 save to inspect Lingapura at155/160/175/180/200,
retaining the original frozen package as the diagnostic control. The component
probe publishes no policy and issues no game orders. Then isolate a credible
unowned Quarter footprint and an existing-chain supplier under1.5. Qualify the
implemented coverage fixes and any valuation correction before the fresh250.
The full game must use main CSC tuning only and the shared controller, with
manual checks about15 minutes apart. No new game is running at this note's write.

Artifacts: `C:/Users/Shadow/Desktop/Codex/csc-ai-astra-gaps-20261114/`.
Native evidence: `native-followthrough-ghidra.json` and
`native-followthrough-code-parity.json`. Prior source:
`csc-ai-planning-campaign-20261114/pangaea250-01/`, including AI_CityBuild,
City_BuildQueue, AI_Behavior_Trees, native economy journal and Lua events.

Upstream check before replay: WildW develop2986a746b396eb93aad14f9afffb043a09c2c489,
mastere59b5aa910c8a0fcab9b31973ffa477443de0e09. Retain the qualified400e6755
development API build for this investigation; no upstream merge or PR is made.

## Component replay and review: findings before the fresh game

The read-only replay's155/160 records explain the changed site. Both footprints
are unworked, so their displaced-yield debit is zero. Site2917 gains an owned
Base supplier at2916 between these captures, raising direct Production0→1 and
prospective Water-Mill total3→4. The native owner setter requests player4 and
city393221 at157; the physical supply snapshot agrees at160. There is no2916
purchase/debit receipt. The footprint itself was already owned.

At155, current Production1.199 gives Quarter readiness26 and Mill60, beyond the
50-turn horizon. Site2992's economic4255Q8 plus96-unit preference explains its
112.62-unit offer. At160, Production2.398 brings Quarter13/Mill30/Granary44 into
the horizon. Raw economics are13269Q8 for2992 and12386 for2917: the latter's
supplier is unworked, so no worked-tile returns are invented. Its +4 preference
then produces the stronger total61538Q8. Astra reviewed these full ledgers and
recommends retaining the current formula for this coverage package. Production
feedback after Quarter completion remains a separate bounded forecast
enhancement; it is not required to explain this production loss.

For acquisition, Fractal player1/city196610/plot2609 has27 frontier receipts.
The early receipts show native writes, eligible cache reads and city comparisons
with zero site wins. The best443.96-unit offer loses to Lavra and Rural Community
alternatives around600–1300. This target does not reach the purchase stage;
changing savings would not address that loss. All eight new Quarters also start
with owned Base, explaining the absence of Base-scarcity acquisition offers.

Astra's second review retains the accepted representative1.5 closure: AI-C162's
40-Gold footprint payment→ownership→foundation209→completion213, and AI-C163's
45-Gold supplier payment220→offer retirement221→Farm226/physical227–230. The
sealed audits and exact artifacts remain under
`csc-ai-problems-1-2-20261110/nuremberg-{ownership-integrated,ownership-reload,supplier-full,supplier-follow}-01`.
New economics and population slots change which investments win; they do not
erase those qualified purchase boundaries. Current-source qualification adds
modded Spec and shared-Base/Spec supplier cases: six supplier and six publisher
fixtures pass. Rebuilding the clean CEdbfb93b self-test source passes243 district
checks plus four hook-group checks and instruction-call delivery/restoration.
The old prebuilt180-check executable is not the current-source result.

Astra finds no blocking source issue in the coverage SQL or capacity changes.
LoadOrder479 covers the selected CL/R2/Suk mappings, not every optional future
compatibility generator; LGD customer mappings at2005 remain a separate scope.
The fresh-game freezer now explicitly overlays both reviewed SQL files and adds
the unconditional479 runtime action/file registration. Its deployment fixture
checks that unrelated source content is excluded and the CE criterion on the
existing connector action is preserved. Actual new payout delivery and provider
co-location remain live observations to qualify.

The component replay completes150–200 with verified checkpoint200, normal exit0,
owners absent and exact preference/package restoration. The passive observer
drains6266 records with zero faults/active callbacks. Its final snapshot is
`e76beddd58789d80dbb17a58174a7ee5f6ac055b3199573992c26b7d696eab97`.
Reusable request/cadence evidence is published in skill AI-N131, commit6aef0be.

The real old-game DB exposes ten missing ordinary material hosts out of25 and
all14 missing provider edges. Applying only the reviewed SQL to an offline clone
produces exactly one attachment per expected host and one edge per provider pair.
The clone uses synthetic trigger hashes for row-generation verification; the
fresh game must pass the same read-only audit using its own loader and hashes.
That once-per-game preflight is now part of the passive full-game observer when
the new gameplay SQL is present. Historical packages bypass the new gate.

The selected fresh comparison is Continents/Small, Online, seeds18461107 and
29461107, through250, with the same CL/R2/Suk stack and accepted gameplay/art
base. `frozen01/freeze.json` records every reviewed AI/UI/SQL overlay; no unrelated
workspace content is included. Only main CSC policy runs. The passive native
observer now includes qualified pre-foundation cached values, matching controls.
Twelve continuation/component/deployment and19 observation/native-reader tests
pass before launch. Candidate outcome directory: `fresh250-01` under this goal's
artifact root. New physical payout/provider evidence and game comparison remain
required after this launch.

### Fresh startup caught a real load-order gap

`fresh250-01` fails the new coverage gate at turn1, before autoplay, then exits0
with owners absent and exact restoration. All14 provider links are present.
Eight incoming hosts remain absent: R2 Sawmill and CL Craftsmen/Trading Post.
Modding.log confirms our479 pass ran before R2's Sawmill creation799990/optional
edit800000 and CL's extra valid-resource links9999. Existing resource tags at
479 were not sufficient. The final resource DB made the offline clone pass,
which is why the actual loader audit mattered.

The unconditional material action now loads at800010. Main ModBuddy JSON,
generated project and fresh-package registration agree;37 economic/SQL tests
and the package-deployment fixture pass. The frozen01/failed startup artifacts
are preserved. Replacement frozen02/fresh250-02 retains the same selected seed,
policy and content, with only this ordering correction. The25-host/14-provider
loaded audit must pass before the controller advances the new game.

`fresh250-02` passes that real loader audit:25 material hosts and14 provider
edges, every count exactly1. The ordinary fresh game advances through6 and
continues toward250. Native observation installs20 qualified hooks without
faults, including the pre-placement cache reader. Protocol records main policy
only, no external policy/gameplay interventions,15-minute controller windows.
Outcome comparison and new physical transaction qualification remain pending.

## Separate physical payout qualification

The ordinary game must finish, save and close before this diagnostic can load
its exact250 save. `material_coverage_replay.py` checks that closure and save/
package identities, then uses the shared controller for a disposable session.
It advances no AI turn and never saves its fixture grants into the source.

A human city without either Quarter receives two declared Quarter footprints,
Wind Mill/Café/Textile Workshop and three adjacent material plots. The fixture
cycles healthy Wheat/Farm, Maple/R2 Sawmill and Bamboo/R2 Sawmill, plus an explicit
unmapped Stone/Sawmill negative control and final removal. Actual UI building
yields must change by exactly +1 Wind-Mill Food, +1 Café Food and +1 Workshop
Culture respectively; unrelated recipients stay at their baseline. Physical
supplier readback accompanies the settled yield samples. Final removal restores
the tested improvements/increments; the grants disappear when this unsaved
disposable world closes.

Astra reviewed the API/lifecycle approach and requested the known queued-district
guard: completed-district creation can PopFront an unrelated district order.
The planner excludes such cities; setup rechecks and preserves queue item,
population and Treasury. All resource classes, improvement mappings and producer
definitions are checked before the first grant, including the negative control's
absence from relevant classes. Three observation-validator tests and Lua5.1
parsing pass. The live incomplete source was rejected before any session or
output directory was created. This is prepared tooling; native payout results
are still required after the250 game closes.
