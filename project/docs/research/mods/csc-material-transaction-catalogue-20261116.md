# Directional material transactions: implementation and native qualification

16 November2026, ordinary-economy goal G2, roadmap1.4/2.2. Qualified slice.

## Implementation

Five producer/material relationships now declare their native payout legs in
gameplay SQL: Water Mill/Base, Wind Mill/Base, Café/Spec, Workshop/Base and Fashion
House/Spec. Gold companions and M&C append legs. The45 Gold+M&C legs preserve
ordinary inputs1, Industry inputs2 and Corporation inputs3. Returns remain the
ordinary1 plus Industry1 or Corporation2 increments.

The material processor generates payout/link/gate arguments from those terms.
Native parent/owner registrations remain early to satisfy database foreign keys;
stable updates preserve shared identities and unrelated dependents. Missing
bindings, conflicting shared leaves, unsupported exact-input host migrations and
unexpected members in owned finite requirement sets are rejected. The late800010
pass derives ordinary input roots and an actual input-host read-model after
CL/R2 definitions. No AI-maintained root/rate list remains.

The facts adapter selects actual native input hosts independently of ordinary
plot-return eligibility. A current nonstandard improvement can have a return
without an input; a future Builder job must be legal and unlocked. Native M&C
legs replace the previous name-based multiplier. The model credits plot returns
only with an observed worker and receiving city, using working-city identity
instead of purchase-city identity. Canonical missing legs earn no default+1.
Protection unions structural material plots with actual central-ledger suppliers,
quoting a shared Base/Spec plot once because the counterfactual removes all its
legs. This preserves actual return-only relationships absent from Builder lists.
An already-working producer also remains in the ledger when its yield's price is
zero; a hypothetical absent producer cannot erase physical transactions.

## Gameplay change list

No intended change to native payouts, attachments, material classes, ownership
or adjacency gates. Economic arguments move from native row literals into the
shared declarations. Existing gates are generated as positive AND templates;
other graph shapes require an explicit compatibility decision. Native flags and
unrelated sets remain. Arbitrary changes to native owner/host identities are not
supported migration instructions: change and verify those bindings explicitly.

## Verified evidence

-Material native graph equals the source at60b51107 with Gold off/on and M&C
  off/on; the graph includes the legacy improvement attachments as well as the
  root/leaf/requirement closure.
-Amount-mutation, missing/shared binding, positive gate normalization and foreign
  key tests pass. End-to-end tests execute the production late host pass, then
  `Facts.New→Site→Model`: late CL/R2 hosts, unregistered return-only host, Gold
  off/Industry, unworked plots and stale working-city observations.
-`material250-01` runs the migrated production SQL on the original turn250 world.
  All10,954 rows in the eight native effect tables equal the fresh original
  package;137 fixed rows and67-city population refresh also match. Isolated
  current model processes22 actual Quarter chains,32 material records and150
  eligible leg records without changing active policy or publishing bids.
  Session closes/restores, native exit0.
-Final `material250-02` uses the hardened Facts/Model and current UI fact bridge.
  The full10,954-row graph,137 fixed rows and67-city population refresh match.
  It processes22 chains/32 suppliers,30 observed worked suppliers,32 known
  receiving cities,27 input streams and52 worked-return streams. This isolated
  zero-price smoke publishes no bids.35 transaction,102 economy,20 Stage3/4,
  four material-diagnostic and26 shared-session regressions pass.

## Native lifecycle qualification and fixture corrections

`lifecycle250-01` uses the original frozen gameplay, zero AI turns, on disposable
human fixture city720900: Bakers955, Tailors1030, Wheat/Farm956, Maple/Sawmill1029,
Bamboo/Sawmill1031. Producer placement is asserted at each Quarter. Each isolated
supplier, producer and district pillage/repair cycle restores its starting payout
vector. Original save, packages and preferences are preserved; exit0.

Incoming Food/Culture falls by1 when its supplier is pillaged. Other observations
are asymmetric: the Café's plot returns appear on Maple, while the Mill/Workshop
returns are absent from the chosen Farm/Bamboo footprints; Maple also retains
Production/Gold while its improvement is absent. Pillaging the Bakers district
reduces observed material input while the Tailors district sample does not.
These are diagnostic observations to explain, not authored Quarter-specific rules.

The second probe records actual modifier owners/subjects and Quarter/CityCenter
distances. Its material roots correctly select the Farm, but the Farm child has
zero yield subjects; Maple's corresponding child has one. Native reinspection
finds a fixture initialization gap: WorldBuilder ownership607190 calls the low
plot-city setter directly, whereas native CityPlots ownership4c5f0 additionally
creates a PlotYields object through943260. SinglePlotYields collection8a3330/
8a2690 selects those registered yield objects, not merely physical improvements.
Thus a newly WorldBuilder-owned plot can accept the attachment and still lack
its payout target. The corrected fixture requires already-owned city land.
`lifecycle250-03` finds no suitable five vacant plots and exits before modifying
the world. `lifecycle250-04` explicitly clears improvements on five declared
already-owned plots, preserving their native yield targets. Earlier samples remain diagnostic
history, not evidence that the gameplay wrappers intentionally omit returns.
Private trace: `material-worldbuilder-native-evidence.json` in the artifact root.

The corrected owned-land run04 completes24 observations, restores every repair
cycle and closes/restores exit0. All three material return families now pay their
Production/Gold. Supplier or producer pillage removes the relevant exchanges.
District-only damage leaves intact building-owned plot returns active. The model
now preserves those returns at readiness0 while receiving-building input uses
functioning-host readiness; retained income gets no future-building premium.

Native PlotDistrictTypeMatches initialize8e5180 defaults `MustBeFunctioning` to1,
even though the authored argument is absent. Its TestPlot8e5ce0 calls native
IsFunctioning36f050, which checks completion/removal/pillage. This resolves the
intended input gate. The later incoming-effect capture resolves the apparent
Tailors exception: the parent loses its subject and the incoming child disappears
when the district is pillaged. The cached UI building yield can still show the
previous input. Recreating the supplier under damage produces no child; repair
restores the child even when that UI cache still shows zero.

`lifecycle250-07` completes30 measurements, qualifying each repair against
physical flags, normalized native modifier owners/subjects and live Gameplay
`city:GetYield`. The Bamboo Culture sequence is9 intact,8 district-damaged,
8 fresh input under damage,9 repaired. Its cached UI building Culture instead
retains1 on the first damage and0 after the fresh repair. One cached-UI mismatch
is recorded explicitly; it does not alter the recovered native graph/live yield.
Farm/Maple Food likewise recover19→18→19. The fixture advances no AI turns and
does not overwrite the source save. Cleanup initially encounters an unavailable
state list; the controller now retries read-only discovery for the same held
owner before reserving any exit operation.

The native UI getter68a890 reaches CacheCity::GetBuildingYield075c10, reading
the precomputed building-yield vector. Cache fill075360 reads live building
yields through132850/131670. Gameplay `city:GetYield`6c9420 reaches live city
yield1332f0/12ff20. These observations qualify the fixture's payout lifecycle;
they do not require a new district-update hook. Native district pillage11f610
already emits the relevant updates. Protection consumes actual central suppliers
as well as structural policy lists; end-to-end regressions also cover damaged
customer hosts and the owner-direction differences of fixed exchanges.

Artifact root:
`C:/Users/Shadow/Desktop/Codex/csc-ai-ordinary-economy-20261116`.
Native XP2 SHA256
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
CE source2d200ef. WildW develop2986a746/mastere59b5aa unchanged at preflight.
SQL private placement preference remains1; Services remain deferred.
