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

### Clearance commands and Antiquity Sites

The loaded game identified resource index 47 as `RESOURCE_ANTIQUITY_SITE`
with class `RESOURCECLASS_ARTIFACT` and no `Resource_Harvests` rows. The
native plot can therefore become occupied without gaining a clearing job
for a Builder.

In the Windows XP2 reference binary (SHA-256 prefix `324c51e9`),
`ClearPlotNode::Execute` at `55d970` first submits removal if the plot has
an improvement. With no improvement it submits harvest when the bound
Harvest flag is true. Otherwise it submits feature removal. Submission
and execution are separate. `CanPlayerHarvestResource` at `35fba0` rejects
a resource definition with no harvest actions before checking player
eligibility. `CanPlayerRemoveFeature` at `5d9610` checks the feature's
removable flag and the player's prerequisites and restrictions. These
player-level checks are separate from the unit's charges and movement
state in the operation callbacks. Entry fingerprints map the three
routines to `55d9b0`, `35f460` and `5d9650` in Steam build 26595377
(GameCore SHA-256 prefix `4de40abf`).

### Suppressing both known requests without Builder work

An exact turn-128 replay verified that both bare footprints were legal
Rural Community placements. The diagnostic suppressed only the matching
Thessalonica and Gondar clearance recruitments while they were bare or
held only an Antiquity Site. Both cities kept their original city
production choices through turn 132. The guard intercepted nine requests.

Adwa took the same Builder on turns 128–130 and 132. Its turn-128 district
site had an improvement and a resource. The later site had jungle. The
district controller held it at bids from 1,135 to 1,743, and the unit
skipped those turns. On turn 131 a different improvement controller
offered the unit back to Axum's 230 request. The Builder had already
moved and was marked processed. It did not enter the evaluated pool.
Axum still had no working Base supply on turn 133.

This separates three decisions. A site can lack a valid Builder action,
a clearance tree can retain a Builder while skipping its move, and a
released offer can arrive after the unit has acted. The clearance gate
addressed the first for two cities in this fixture. Evaluate sequencing
on a genuine clearance job before changing the bids for working jobs.

### Clearance sequencing with the two-site guard

The same replay combined the two-site guard with the selector span trial.
The loaded database confirmed node 15 ended at 17. The guard again
intercepted nine requests. Adwa recruited Builder 7864354 on turn 128.
The unit moved on turns 128 and 129 and reached the plot at (48, 23).
On turn 130 the district tree reported successful Clear Plot and the unit
submitted Remove Improvement. Adwa continued building its Star Fort and
then queued a Builder. Its Rural Community had not entered the queue by
turn 133. The watched Builder had processed before all five Axum searches.
On turn 131 it was free at the search but had already spent a charge on
other improvement work. Axum still lacked working supply at turn 133.

The sequencing change made the held Builder perform work. The original
five-turn window still had no usable Builder for Axum, so the trial did
not establish earlier supply. The loaded `TreeData` offers another point
to check. `Build City District` node 16 binds Builder Type and Clearing
Builder, with no destination (`DefnId=1`). Node 29 and the corresponding
`Build City Improvement` nodes bind Location. The reference node uses
sentinel coordinates for a missing target. A typed native evaluator
compares equal-priority candidates by distance to its supplied target.
Record the actual destination and chosen unit when testing the missing
binding. The selector trial is in `axum-clearance-sequence-pair-128-133`.

### Binding the district footprint to recruitment

The next matched replay added `TreeData` destination binding 1, `Location`,
to stock Find Available Unit node 16. It kept the same two-site guard and
selector span used in the preceding replay. The loaded table contained the
new binding. Adwa's actual evaluator received (48, 23) on turns 128 and 131,
matching its Rural Community reservation. The turn-128 first pool still
selected Builder 7864354. The unit moved on 128 and 129 and submitted
Remove Improvement on 130, as in the preceding comparison. The unit had
already processed at all five of Axum's searches. Axum still had no
working supply at the turn-133 boundary.

The destination binding works at the recruitment call. In this fixture it
left the relevant choice and supply outcome unchanged. Captured pools,
selections, commands and the end-state check are in
`axum-clearance-location-128-133`. The controller recorded normal exit and
restored preferences.

### Letting the supplier recruit from an idle clearance pass

The guarded loan replay used the original stock tree and the ordinary
CSC and CE packages. At the end of the district tree's action dispatch,
the probe recorded the controller and the states of Find Available Unit,
Move Unit and Clear Plot. At Axum's normal recruitment, it qualified only
the exact charged, unprocessed Builder held by a district whose pass had
successfully recruited and left movement and clearing Ready. The district
plot had no feature, improvement or resource a Builder could act on.
The holder allowed native release at the same request priority. The
probe raised the requesting value for that pairwise release call only.

On turn 128, Thessalonica held Builder 7864354 on a bare plot after this
sequence. The native release comparison received 1,509 against the
holder's 1,508. Axum's Sawmill bid stayed at 230. The holder offered
7864354, the native chooser selected it, and the worker moved from
(53, 24) to Bamboo at (53, 26). The later searches did not qualify for
another loan. The worker skipped turns 129 and 130. Axum recruited it
from the ordinary pool on turn 131 and it built the Sawmill that turn.

At the turn-133 boundary the Textile Workshop was present and unpillaged.
The active Tailors Base culture effect named Axum's Quarter and the
production return named the Bamboo improvement at plot 1977. The Flax
Farm remained pillaged. The data are in
`axum-clearance-action-loan-128-133`, including `recruitment.json`,
`UnitOperations.log` and `axum-restored-native-material-effects.txt`.

The passive control loaded the same checkpoint and packages and observed
the same recruitment and action-dispatch boundaries. With its comparison
unchanged, the same Builder skipped turns 128–131 and moved for another
job on 132. Bamboo was unimproved on turn 133 and neither of Axum's Base
transaction effects was active. All 16 production queue records for
Thessalonica, Gondar and Adwa matched the treatment. Thessalonica continued
reserving (51, 18) in both arms without moving a Builder to it or clearing
it. Across player 5, logged Builder improvement construction requests
rose from three to four and feature removal requests stayed at one.
The control is in `axum-clearance-handoff-control-128-133`. Both runs
exited normally and restored preferences.

The reusable intervention should publish a legal, reachable supply
restoration job from the CSC model under the existing per-player offer
budget. Revalidate the current holder's native permission, same-priority
request, completion of its current action pass and lack of an actionable
clearance. Let the stock evaluator choose among the eligible offers.

### Packaged CSC and CE follow-through

The CSC material planner publishes a loan alongside its existing positive
supplier entry when a present buyer lacks that input and a charged Builder
has a verified route. The native worker consumer checks the exact admitted
job, the worker's live position and custody, and the completed district
clearance states before permitting a release comparison. The loan is
limited to one comparison per AI player and packet. The game's evaluator
still selects the candidate. The offer, the released candidate and the
physical job are logged separately.

The first packaged replay used the saved turn-128 opening, the stock tree,
and the new CE DLL with three tracked CSC Lua files. It used ordinary
status and physical observation without the development probe. The planner
published Bamboo at 1977 for Builder 7864354. The turn-129 policy readback
reported one offer from Thessalonica controller 39714833 to Axum controller
39583784 during turn 128, with 179 microseconds in the qualifying release
path. Bamboo had a working Sawmill and both transaction effects were active
at turn 133. Full-turn processing includes more than that single callback.
Evidence is in `axum-integrated-worker-loan-128-133`.

The final pair used the same CE DLL, SHA-256 prefix `93dec610`, and the
same turn-128 checkpoint. The control switched off loan publication.
The enabled arm exposed 7864354 to native recruitment on 128, moved it
to Bamboo on 128 and built the Sawmill on 131. The two native transaction
effects were active on 133. The control had neither effect and Bamboo
was unimproved at 133. The arm directories are
`axum-final-integrated-loan-128-133` and
`axum-final-integrated-control-128-133`.
All 16 observed production queue records for Thessalonica, Gondar and Adwa
matched between arms. Player 5's improvement construction requests rose
from three to four and feature removal requests stayed at one. Both runs
closed normally and restored preferences.

The Release x64 build passed 265 native district-score checks, four
hook-group checks and the instruction delivery check. CSC passed 198
Lua policy, supplier and economy checks. The integration is published
on [CE csc-dev](https://github.com/hennogous/CivilizationVI_CommunityExtension/commit/f9dbcda709f690b5aee1e240ef21683a56ee6150).

### Edinburgh in ordinary play

The first fresh validation uses Small Continents on Online speed, map seed
`793412556` and game seed `1390346751`, with the packaged CSC and CE code and
stock AI. The shared controller started a normal game without changing
gameplay state. Its turn-186 check found the first native loan in the run.

On turn 167, CE offered Builder 7667722 to Edinburgh's admitted Pasture
job at plot 2250, with native improvement value 179. The same job had
asked for a Builder through contract 3713. It canceled that contract after
finding the existing worker. The unit moved and built the Pasture on 167.
The material observer independently recorded the improvement on Cattle
2250, next to Bakers 2323. The buyer had zero working Base suppliers at
the turn-167 survey and one at turn 168. The native guard measured 0.177 ms
at the successful release callback.

In the completed log, the buyer first had one legal Base site and no
working Base at turn 104. The same state appeared at every survey through
167. Edinburgh first reserved Cattle on turn 166, 62 turns after that
first survey. The city had logged thirteen reservations for other
improvements in the interval. Nine cities evaluated the same fallback
Builder contract, which was still waiting when the loan supplied an
existing worker one turn after the reservation. This case separates the
pre-reservation delay from the recruitment delay. The handoff starts at
recruitment, after the native job has its site.

The enabled game exited normally at turn 250 with complete supplier buyer
surveys. It published 92 loan offers for nine distinct jobs. The one
released Builder produced the Edinburgh Pasture. Across the AI empires
there were 17 new supplier improvements and four repairs, and 16 of 21
eligible supplier plots were working at the endpoint. Eight of thirteen
buyers received supply within 15 turns. Whole CSC publication averaged
1.415 seconds per turn and peaked at 3.242 seconds. Controller wall time
from autoplay start to the last boundary was 3,097 seconds including
observer handoffs. The same-seed control is running. Its CSC Lua differs
only by the switch that disables loan publication. Evidence is under
`ordinary-continent-worker-loan/loan-on`.

### Other supplier delays in the enabled game

Of thirteen buyers with at least 15 turns to obtain legal supply, three
were supplied after a longer wait and two were still missing supply at
turn 250. The stock city trees show several ways this happened.

| City | First legal supplier survey with no working supply | First reservation | What the city tree did |
| --- | ---: | ---: | --- |
| Edinburgh | 104 | 166 | Recruited and built the Cattle Pasture on 167 using the loan. |
| Cumae | 137 | 139 | Reserved the Barley on 139 and 149. Each job went ten searches without a Builder. The 159 job recruited on the same turn and built a Farm on 166. |
| Ostia | 146 | 152 | Recruited for the Flax Farm on 157, then failed protection on 162. Reserved again on 163, recruited on 168 and built that turn. |
| Mashhad | 168 | 168 | Reserved Sheep twelve times. Ten reservations logged recruitment. On three attempts the tree logged a completed move and later failed at Build Improvement. |
| Angkor Thom | 192 | 203 | Reserved the pillaged Maize Farm four times and recorded three successful recruitments. The last observed attempt failed protection a turn after recruitment. |

Mashhad is the clearest follow-through check. For the Sheep at (61, 8),
its city tree reported Move Unit Success and Build Improvement Running
on turn 200, then Build Improvement Failure on 201. On 201, the unit log
records Builder 8323118 first issuing Remove Feature, then a Build
Improvement order that could not start. It is the only ordinary Builder
with a build operation logged for that player on 201. The log has no
destination or improvement parameter, so the unit and request still
need to be joined to Mashhad's tree. The stock operation eligibility and
the actual request payload can be compared from the unchanged turn-200
checkpoint (SHA-256 `2e458967018772a905fc253e73bfa4a455ce4e79a5b24b2b3c316402c9b14cf3`).

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
`axum-empty-clearance-128-133`. The two-site comparison is in
`axum-clearance-pair-128-133`. The controller recorded normal game exit
and restored preferences for these comparisons. Two earlier launches
of the two-site probe stopped before advancing because the opening
readback used an unavailable Lua function and then the wrong UI context.
