# Quarter bids miss growth inside the player turn

**Confirmed:** the global CSC publication can run before per-player city growth.
A city then gains a district slot while its packet still contains the managed
negative default. The preceding capacity gate therefore excludes useful Quarter
bids from a real same-turn decision window. This is a timing failure, not a case
for increasing every bid. A matched correction replay verifies timely positive
delivery below; it does not produce new major-AI Quarter construction.

## What the completed 250-turn archive did and did not show

The capacity run has 11,767 city/Quarter snapshots across 98 scopes: 5,711 ready,
5,963 full and 93 stale. There are no duplicate scope/turns or internal missing
turns. Its 193 full→ready scope transitions represent 99 distinct city/turns in
34 cities, not 193 different slots or investments. Of those 99, 83 reach a new
observed allowance high; 16 recover earlier bands after population oscillation.

No consecutive known full→full pair increases occupied count, even across stale
gaps. This **does not rule out missed planning windows**: a request can be accepted
before its district foundation physically occupies a slot. Snapshot59 can still
show room even though a native plan was selected on58. Overcapacity recovery also
exists: 334 full rows have used>allowed, and 34 scope transitions increase allowed
while remaining full, without increasing used. These are not newly free slots.

All 26 scopes that end before250 are accounted for: four same-turn guided Quarter
foundations whose last readiness is ready, and 22 scopes in 11 holder cities absent
from the next25-turn census. No unexplained logging disappearance is treated as a
rejected investment. Stale93 rows correspond to47 city/turns, maximum streak3.

Hobart: original publication58 is full (population3, used1, allowed1) and Bakers1345
has the negative default. Native Theater plan/request is accepted58; our positive
Bakers packet arrives59. Theater queues62 and completes70. Canberra's publication67
is full; Campus is accepted67, Tailors1124 becomes positive68, Campus queues69.

The archive alone does **not** establish native population at admission. The initial
description "the AI chooses/adopts the plan while still full" was too strong: full
was observed at publication. Native admission may occur after growth in that turn.
The phase replay below resolves this gap. Existing AI-N127 rejects actual full
unfinished construction requests; no exception to that mechanism is inferred here.

## Unchanged-policy phase replay, turns50–70

The shared controller loads the exact archived turn50 save and packages from the
completed capacity run. No scores, game properties, queues, gold or research are
changed by the observer. It transparently wraps Publish and reads city facts at
population, player-activation and district-foundation events. A monotonically
numbered diagnostic sequence preserves within-turn ordering. Unknown pre-install
offers stay unknown. UI and Gameplay population/inventory are recorded separately.

Scope: patched Windows Steam XP2 SHA256
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`;
unchanged CE DLL `400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f`.
This is ordinary replay, not a fresh game or an experimental external AI policy.

| Case | Publication | Growth in the same turn | Next publication |
|---|---|---|---|
| Hobart, player4/city262147 |58, sequence492: pop3, used1/allowed1, packet9, no positive Bakers bid|58, sequence521: pop4, used1/allowed2, **same packet9, still no bid**; activation525 agrees|59, sequence555: packet10 has one positive Bakers offer|
| Canberra, player4/city65536 |67, sequence1088: pop3, used1/allowed1, packet18, no positive Tailors bid|67, sequence1125: pop4, used1/allowed2, **same packet18, still no bid**; activation1127 agrees|68, sequence1162: packet19 has one positive Tailors offer|

UI and Gameplay agree in these witness rows. The problem is not merely a lagging
UI getter: real city state changes after a previously accurate publication.
Both old and new states share the same global game-turn number.

Native city records reproduce Theater submission58/queue62 and Campus submission67/
queue69. Replay contract IDs are765/936 versus original764/935; do not join native
IDs blindly across fresh play and reload. The exact instruction time of native
submission is not independently timestamped by this Lua observer. Its same-turn
CSV admission and the phase records establish the omitted positive-bid window,
not a counterfactual Quarter victory.

Twenty observed publications plus the initial on-load packet, 1,326 phase records,
no observer/policy faults. All three event bindings
and their callbacks are exercised. Endpoint70 saves and native exit0/restoration
verify. Artifact root: `Desktop/Codex/csc-ai-capacity-timing-20261113/`;
`replay50-70/`, `control-audit.json`. The three offline observer tests verify
argument/return transparency, stale-cache separation and failure isolation.

## Smallest correction and matched replay

Keep capacity facts and known/full/unknown diagnostics, but do not use a global
current-capacity snapshot to erase worthwhile future Quarter bids. Preserve the
economic formula, quality threshold, material protection, ownership rules and
native CanZone admission. Do not invent a growth forecast or increase bid premiums.
Missing capacity is unknown, not a promised slot. Existing foundations/repairs retain
their independent handling.

Source tests30 and placement-observer tests10 pass; Astra finds no blocker. Forecast
work returns toward the pre-gate workload, so the gated run's lower timing is not
carried forward as a candidate performance claim. Candidate01 changes only the
three main-mod files (adapter, publication diagnostics, UI comments) on the exact
old archive; CE is unchanged. The later finalQ8 bookkeeping fix is also present.

### Matched candidate result

The candidate replay completes70 with the same source save hash and loaded
binary identities. Independently hashing both archived input trees confirms no
CE difference and exactly the three intended CSC Lua overlays. Economic pricing
and placement premiums are unchanged; formerly suppressed bids return to native
competition. Thirty central tests, ten placement-observer tests and three phase
observer tests pass. Astra reviews source and independently audits both arms.

**Hobart's timing defect is removed:** publication58 sequence493 carries one
Bakers offer at84,211 Q8 while population is still3. Growth58 sequence524 opens
the second slot with that same packet9 and bid still present; activation528
agrees. The exact native write for player4/city262147/district36/plot1345/version9
is84,211, versus−262,144 in control. This is328.95 native utility points versus
the old−1024 default, not Gold or a new premium.

Canberra also retains a Tailors offer before its earlier59 population3→4 event:
46,745 Q8 under packet10. At67 its native write for Tailors1124 is77,030 versus
control−262,144. However its population trajectory diverges after64; candidate
publication67 already sees population4. Do not claim an exact matched67 growth
sequence. Hobart58 supplies the clean paired timing witness.

Two new-site Quarter Best results consume exact bid/prior write/version and
preceding native ordinal, compared with zero in control:

| Candidate native winner | Packet | Exact Q8 value | Publication readiness |
|---|---:|---:|---|
| Hobart Bakers1345 |7|76,792|Full (one used/one allowed)|
| Antioch Bakers912 |13|62,750|Full (one used/one allowed)|

These are nominations, not admitted construction. Their record drain turns are
not exact native instruction timestamps. A published-full record also does not
prove the native city remained full later at comparison/admission.

**No new guided-major Quarter foundation or completion occurs in either arm.**
The raw lifecycle stream does include player6's Tailors1726 foundation55 in each
arm; do not mistake it for guided placement. Berlin's existing Quarter contract
still submits51, queues58 and cancels60 in both arms; it is not a new foundation.
Theater363 submits58/queues62 in both Hobart arms. Canberra Campus submits67 at
808 in control and806 in candidate, then queues69 versus68. Those numbers are
logged values, not contract IDs. Native admission population is not independently
hooked in these replays; this is not new proof of CanZone rejection/acceptance flags.

Both arms publish21 times over50–70 inclusive: the initial on-load packet precedes
observer installation, followed by20 observed publications. There are no packet
omissions, trims, native/policy/observer faults or incomplete diagnostics. Candidate
packet maximum124 entries versus118. Twenty measured matrix rounds have median/max
13.3295/18.365 ms versus8.803/12.275 ms. Coarse publication totals4 s versus2 s.
Removing the computational shortcut costs more forecast work, but this short and
instrumented window is not a general performance or economic benchmark.

Both endpoint archive hashes match completed saves; native exit0, owners absent,
preferences restored and package checks verify. No game remains. Artifacts:
`candidate50-70/`, `candidate01.json`, `matched-audit.json`, `matched_audit.py`.
The first audit incorrectly counted20 total publications instead of excluding the
initial on-load packet; the correction and explicit distinction are retained.

The demonstrated timing defect is closed at this boundary. Broader construction
and Service follow-through remain separate. No higher bid, growth estimator,
per-population full-model refresh, new DLL or upstream PR is introduced.

## Skill boundary

Reusable timing is AI-N128 in the `civ6-ai` skill, alongside refreshed existing
findings. CSC policy and outcome tables remain here. A global turn stamp is not
proof of state freshness at a per-player consumer; a positive bid, accepted
request and physical slot occupation are different observations.
