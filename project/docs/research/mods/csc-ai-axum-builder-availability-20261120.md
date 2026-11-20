# Axum Builder availability during the Tailors supply delay

Problem 3.2 follow-up, 20 November 2026. Astra recommended tracing the early
failed searches in Axum's 40-turn outage before changing the scheduling of
the final handoff. The earlier replay found that the last handoff cost one
turn. The question here is whether Axum lacked a Builder, lost access to a
nearby Builder at recruitment, or had a viable worker diverted to other work.
[Original outage and handoff](csc-ai-axum-builder-handoff-20261120.md).

## Ordinary replay to turn 143

The shared controller loaded the exact turn-100 save, SHA-256
`b9b16888a17bbe5f42c09da5e34d004216dec9d2244aead1149a14d3e12a3f65`.
All 130 structural census rows matched. The original frozen packages had
been retired. The replay used committed CSC `0d297d77` with the experimental
mod ID from the save, CE `bfbce0b` built with SHA-256
`5cebf2a034c9fa0de30d54630d536af8d22ebbdbc97487e6ff6651f00e86ad0d`,
and the five Workshop packages recorded in the original log. CE reported
Builder request and finishing-only support. The shared controller sampled
Ethiopia's stock Builder roster and both supplier tiles at every inactive
boundary from 113 through 143. The read-only worker observer used no
native callbacks. The session closed with exit code 0 and verified
preferences and package restoration.

The original Flax Farm stayed working throughout the 31 sampled boundaries.
The replay therefore provided a comparison for ordinary recruitment and
additional supply, while the original supply outage still needed a fixture.
Axum logged unsuccessful Builder searches on 24 sampled AI turns. The
failed searches covered ordinary Farms at (52, 23) and (51, 22), and the
Bamboo Sawmill at (53, 26). The Bamboo job submitted contract 2886 at
349 utility on turn 137, continued to report failed searches through 142
and remained unbuilt at the turn-143 boundary.

Builder 7208963 had three charges at (55, 23), four tiles from either
supplier, and logged a skip on every AI turn from 117 through 130.
Axum was trying to recruit for other Farms in much of that interval.
At turn 138's Bamboo search, Builder 8323096 ended the preceding and
following boundaries unassigned at (55, 24) with three charges. The
snapshots establish distance and custody, while entry into the native
recruitment pool and route eligibility require their own evidence.

## Controlled supply loss from turn 120

The controller loaded the ordinary replay's turn-120 autosave, SHA-256
`8f3a831ad94ac880ec96a0547fb6a60ea757d0a6d92d7045332dce11f9199be5`,
with the same packages and matched all seven Builder IDs, positions and charge counts.
The fixture verified Axum's completed Tailors, working Textile Workshop and
working Flax Farm. It pillaged the Farm once. The AI made every subsequent
job, production and unit decision.

| AI turns | Evidence |
| --- | --- |
| 120–127 | Axum kept the existing Farm reservation at (51, 22), worth 492 utility. This job failed to recruit on all eight turns. Its Builder contract 2352 reached completion on 127, then the tree failed its protection check. |
| 128 | Axum reserved a replacement Bamboo Sawmill at (53, 26), worth 230 utility, and failed to recruit. Its native fallback submitted Builder contract 2653 at 230. |
| 129–132 | Four more Bamboo recruitment failures. Builder 7864354 had three charges, remained unassigned at (53, 24) and skipped on 128–131. It moved farther from Bamboo on 132 under a new controller. |
| Turn-133 boundary | The Flax Farm was still pillaged and Bamboo was still unimproved. The controller archived the verified endpoint. |

CE recorded an exact Flax improvement score increase of **4,649 Q8**
(about 18 utility), repeatedly from the turn-128 decision onward. The
material capability remained ready and recorded no separate CSC Builder
request offer or finishing offer for either site. Native Builder
contract 2653 was still open within its eight-turn window when the
observation ended.

This fixture exposed a busy city work slot before recruitment, followed
by unsuccessful recruitment with charged units in the area. It did not
isolate a reachable Builder taken by weaker work. Time the exact
recruitment pools and rejection of Builder 7864354 before trialling an
earlier pass or raising production pressure. The current finishing
scheduler applies once a worker is assigned and on the sole-supplier
repair tile.

The game acknowledged exit after the turn-133 save and preference
restoration, but its process remained alive. The test process was
stopped after its identity and save were verified. The logs and both
temporary packages were archived and no game or Tuner process remained.

## Sawmill gameplay integration

The loaded gameplay database maps Bamboo and Sugar Maple to Resourceful 2's
Sawmill. Construction unlocks it, and its only allowed worker is the
ordinary Builder. The City Lights Farmer can build a Farm in this stack.
The Sawmill's Build Unit fallback requests the ordinary Builder.

CSC's Resourceful 2 support tags Bamboo as Tailors Base and Sugar Maple
as Bakers Specialty. The common material host processor joins those tags
to the loaded improvement rules. The replay database contained Sawmill
input hosts and matching improvement modifiers for both the Textile
Workshop and Café transactions. The AI reads the same loaded resource
and worker rules.
[Resource tags](../../../../Civ%20Supply%20Chains/ModSupport/ModSupport_R2.sql) ·
[Material host processor](../../../../Civ%20Supply%20Chains/Data/CSC_Q_ALL_MaterialHosts.sql).

Axum's native Bamboo job passed Check Plot and requested an ordinary
Builder on turn 128. The original run also showed a different ordinary
Builder building the Sawmill on that plot and restoring Tailors supply.
[Original physical completion](csc-ai-axum-builder-handoff-20261120.md#same-builder-resumed-the-bamboo-job).

## Builder custody during the actual recruitment call

The shared controller loaded the controlled run's turn-128 autosave,
SHA-256 `78a30851782f4b5144b38fdd1b05c0736fdda25a749df6b1653a082abdce2237`.
The replay verified the Builder roster and damaged Flax before advancing
to 131. It ran the same CSC and CE packages. The passive trace sampled
the stock recruit call and its candidate evaluator for Axum's target.
It captured three complete requests with zero callback faults and closed
with native exit 0 and restored preferences.

Axum requested a Builder at native priority 2 and 230 utility on all
three turns. Builder 7864354 was two tiles from Bamboo with three charges,
`processed=0` and `departing=0` at each request. It was already under a
different controller, and custody remained with that controller after
each request. The candidate evaluator received zero Builders. The unit
went on to skip each of the observed turns.

| AI turn | Axum controller | Builder 7864354 at recruitment | Free-unit pool size, all types |
| --- | ---: | ---: | ---: |
| 128 | 39583784 | 39714833 | 12 |
| 129 | 39583784 | 40370200 | 13 |
| 130 | 39583784 | 41353222 | 23 |

The same replay with the release trace resolved all three holders to a
Thessalonica Rural Community district tree at (51, 18). The native
destination, city and whole-utility values matched the City Lights
district entries in the behavior log. Every release request ran at
priority 2 and returned an empty list. The holders allowed release but
had present values of 1,508, 1,570 and 1,258, against Axum's 230. The
opening route query found a path through the Tailors Quarter to Bamboo
(1829 → 1902 → 1977).

The district tree used its tile-clearing recruitment branch. The loaded
tree makes Find Available Unit, movement, clearing and reservation
alternatives under a Priority node. That node stops at the first
successful or running child. On the three turns, Find Available Unit
succeeded and movement and clearing remained ready. On the same turn
128, Taiyuan's failed recruitment let the later clearing nodes run with
no Builder. The `Using builder charge` label belongs to the separate
district-hurrying branch. The loaded Rural Community had no
`District_BuildChargeProductions` row.

### One-time borrowing test

The same turn-128 checkpoint reproduced the exact initial comparison.
A local diagnostic passed 1,509 to the holder for that single release
call, one above the holder's 1,508. It checked both controller identities,
priority 2, both sites, and that Builder 7864354 was the only ordinary
Builder held for that job. The native routine offered the Builder,
the receiving evaluator chose it and the control manager transferred
it to Axum. The stock job still held its ordinary 230 utility.

Builder 7864354 moved to Bamboo on 128. Thessalonica temporarily
recaptured it and it skipped 129 and 130. Axum recruited it again
from the ordinary free pool on 131 and the unit built the Sawmill that
turn. It had used one charge by the next recruitment read. At the
turn-133 boundary the Sawmill was working and the Flax Farm was still
pillaged. In the original controlled outage both Base resources were
still out at 133. Thessalonica repeatedly reserved the same district
site in the borrowing replay. It did no observed clearing during the
window. The diagnostic confirms the cost of the worker hold without
establishing a production bid for general play.

### Stock clearance tree experiment

The loaded stock clearance nodes matched Firaxis's
`Base/Assets/Gameplay/Data/BehaviorTrees.xml`. City Lights provided the
Rural Community and its value. The branch that assigned the Builder
came from the stock game. The replay used the same save and packages
with one diagnostic SQL action. It changed the inner clearance Priority
node 15 from `JumpTo=22` to `JumpTo=17`. The loaded database confirmed
that change. The outer plot-check selector stayed the same. Successful
recruitment now advances to movement and clearance in the enclosing
Sequence. The diagnostic kept the native bid comparison in place.

Thessalonica began moving a Builder to (51, 18) on 128 and reported
arrival and successful Clear Plot on 130 with Builder 7208963. Builder
7864354 made movement or improvement-removal requests for other jobs
instead of skipping. At Axum's recruitment it had already processed.
Bamboo stayed bare at 133 and the Flax Farm was still pillaged.
Thessalonica's opening plot reported no resource, feature, improvement
or district. It reported resource index 47 at 133 and still had no district.
The Clear Plot success is a behavior result. It does not by itself
establish a physical clearance.

This isolates a defect in the stock tree's clearance sequence. The
Priority node performs its documented short-circuit, which repeatedly
obtained a Builder while skipping the work that could justify holding it.
The stock release rule separately honored the holder's higher value.
The trial repair of the sequence demonstrated movement and clearance
execution. It also exposed the need to validate that the plot actually
needs clearing before sending a Builder or testing a production change.
The next 3.2 comparison should preserve useful stronger work and measure
physical supply and any competing work affected.

### Opening placement eligibility

A separate zero-turn load of the same turn-128 save checked Thessalonica's
Rural Community footprint before any Builder action. Plot 1383 at (51, 18)
was owned by player 5 and assigned to Thessalonica. It was bare desert, with
no feature, resource, improvement or district. `Plot:CanHaveDistrict` and
the city's native `BUILD` operation both returned true. The plot was one of
eight legal placement targets returned for that district in the city. The
city had zero production invested and the district cost 33.

The stock clearance branch therefore held Builder capacity for a footprint
that could already accept the district through ordinary city production.
The legal placement query establishes eligibility at that boundary. The
actual district production choice still has to be read from the queue and
the city-build log. The snapshot is in
`axum-site-legality-128/district-legality.json`.

### Suppressing recruitment for one bare footprint

The same turn-128 save replayed to turn 133 with a one-site diagnostic.
It intercepted the ordinary Find Available Unit recruitment call for
Thessalonica's district clearance only while the plot held no feature,
resource or improvement. It passed a null evaluator to `RecruitUnits`,
which returns before recruiting in that case. The guard left published
district and material values unchanged.

Thessalonica's recruitment was suppressed on turns 128 and 129. At both
of Axum's searches, Builder 7864354 was still unprocessed with three charges
and had already been taken by another equally prioritized Rural Community
controller, for Gondar at (58, 22). That plot was also bare. The new
holder's whole utility was 1,429 and 1,417 against Axum's 230. On turn 130
Thessalonica's destination held a resource and the guard left its request
alone. Its controller held the Builder again. Axum still had a pillaged
Flax Farm and an unimproved Bamboo tile at the turn-133 boundary.

The immediate follow-on hold explains why removing a single city from
the contention produced no earlier supply. Any reusable test needs to
classify the work available to the competing Builder at the recruitment
or release boundary. An occupied plot may still lack any task the Builder
can perform. Test that case separately from bare footprints.

On the installed Windows Gathering Storm binary, `RecruitUnits` at
`403170` excludes a controlled unit from the initial free pool. It can
consider a held unit if its current controller offers it. REA decompiled
the entry and the chooser at `5535b0` from the same binary
(`ev_141a99218c956ac1ab24c9db1ef3f1cab60ba90c61bc568c063b7c02d2ccf551`).
The held-unit offer routine at `543870` gates release on permission and
native request priority, then on present value at equal priority
(`ev_ae7ac8ac0fab7ce32fd0cbc77c58cdc11ca66e8c3a7f92336c1db9339a5e968e`).
The earlier inactive-boundary read saw the unit after that turn's
controller released it. The recruitment trace identifies the state
that mattered before the skip.

Local evidence on Shadow lives under
`Desktop/Codex/csc-ai-builder-availability-20261120`. The ordinary
replay is `axum-through-143` and the controlled test is
`axum-forced-outage-133`. The case summaries join the native behavior tree,
city contract and unit operation logs to the boundary observations. The
recruitment capture lives in `axum-recruit-128-131/recruitment.json`, with
the route and holder releases in `axum-holder-128-131` and the one-time
borrowing test in `axum-borrow-128-133`. The stock tree change is in
`axum-clearance-128-133` and the one-site recruitment comparison in
`axum-empty-clearance-128-133`. The controller recorded normal game exit
and restored preferences for these replays.
