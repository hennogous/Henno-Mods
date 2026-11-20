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
The outstanding question concerns Builder 7864354's availability at the
native recruitment check.
[Original physical completion](csc-ai-axum-builder-handoff-20261120.md#same-builder-resumed-the-bamboo-job).

Local evidence on Shadow lives under
`Desktop/Codex/csc-ai-builder-availability-20261120`. The ordinary
replay is `axum-through-143` and the controlled test is
`axum-forced-outage-133`. The case summaries join the native behavior tree,
city contract and unit operation logs to the boundary observations.
