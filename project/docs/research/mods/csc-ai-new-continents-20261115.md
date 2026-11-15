# New Continents world for the coherent planner

Henno requests a fresh Continents seed so the current planner encounters new
geography. This runs the qualified main-CSC candidate unchanged. The active
roadmap scope is Problems 1 and 2, especially 1.5 acquisition and 1.6 follow-through.

## Predeclared setup

- Continents, Small, Prince, Online; ordinary start through turn 250.
- Map seed **20851115**; game seed **31051115**, selected before hosting.
- Same City Lights, Resourceful 2 and Sukritact's Resources stack as the preceding
  tests. Stock AI, with CSC's integrated policy; no RHAI5 or external test bids.
- Reuse the immutable `csc-ai-coherence-20261115/frozen02` package containing
  candidate `9f450233`. All 11 overlaid files match the current source hashes.
- XP2 SHA `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`;
  CE SHA `400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f`.
  WildW develop is unchanged at `2986a746` when checked before this launch.

The shared controller owns hosting, bounded autoplay, popup recovery, checkpoints
and preference restoration. A one-shot current-user task owns the worker lifetime,
records a heartbeat/exit status, and removes its registration after the worker
returns. It neither retries nor changes the game policy. Agent check-ins are
about every 15 minutes. The pinned sources remain unchanged during the run.

## What to extract

For Bakers and Tailors, count foundations and their actual starting adjacency,
Base and Spec neighbors, improved suppliers and existing customer districts.
Follow native-selected plans through acquisition, retained request values,
construction or expiry. Use the continuity journal to explain support changes.
Retain material-loss, customer-order, building and Service observations, ordinary
district calibration and native savings/payment evidence from the existing
passive observers. No manually prepared chains or economic subsidies are added.

Artifacts: `C:/Users/Shadow/Desktop/Codex/csc-ai-new-continents-20261115/`;
game output: `continents250-01`. Startup preflight, original seats, loaded mods,
code hashes, commands, native receipts, checkpoints and final closure are recorded
there. Results will be added after the run.


Startup passed the deployed-module, native capability, resource-stack and
main-CSC policy preflights. The game advanced beyond turn11 with no Lua errors;
original AI seats1–5 are recorded. Plan journal reads are active. Native and CE
loaded-file hashes match the declared identities. The controller continues250.


## Completed result

The game reached250, saved, closed with exit0 and restored preferences. All ten
25-turn censuses are complete. The five original AI players survive. The run
lasted about67 minutes including startup and closure. Main CSC policy and the
qualified package stayed unchanged throughout.

**Five Quarters, all with Base and at least+3 at foundation; all five have
working Base suppliers, producer buildings and completed mapped customer
neighbors at250.** Bakers completes its Stage2 chain in all three cities.
Tailors produces two worthwhile placements serving other stages, including one
active Sacristan. Neither Tailors has an adjacent Harbor.

| Quarter / city | Foundation | Placement rating | Base / Spec neighbors | Stage2 result at250 |
|---|---:|---:|---:|---|
| Bakers, Ottawa |12 |+3 |1 /1 |Storekeeper active;142 recorded active turns |
| Bakers, Sheffield |38 |+3 |1 /0 |Storekeeper active;171 recorded active turns |
| Bakers, Nioro |179 |+3 |1 /0 |Storekeeper active;57 recorded active turns |
| Tailors, Meroë |39 |+3 |1 /0 |Workshop working; no adjacent Harbor |
| Tailors, Niani |134 |+4 |1 /0 |Workshop working; no adjacent Harbor |

Placement ratings use loaded rules with a prospective local Mill where relevant,
plus materials, terrain and already-built customers. They exclude future
customers; the conditional Mill portion is potential until its building exists.
These are foundation observations; the material columns above are their actual
foundation neighbors, not hypothetical resource additions.

At250, all five original placements remain held by their founding AI players.
All five have completed mapped customers of some stage. Four distinct City Lights
goods-provider relationships touch three Quarters. Only Ottawa has Spec supply;
its Berries remain unimproved despite its Café. Improving Spec supply is still
an important downstream development task.

## Services and recovery

The three Bakers deliver **370 recorded active Storekeeper chain-turns**:
142 Ottawa,171 Sheffield,57 Nioro. The observer samples all248 turns2–249, with no missing samples;250 has an independent endpoint
census. Ottawa is active69–131, interrupted132–170, then active171–249.
Sheffield is active79–249; Nioro193–249. All three are active at250.

Meroë's Tailors has a working Textile Workshop and Tailor beside a Holy Site
with a working Temple. Its Sacristan hidden building and Stage3 source property
are active at250; they were absent225. This places activation in226–250 without
inventing a precise unsampled turn. The Quarter itself is pillaged44, repaired62,
pillaged again63 and repaired79.

Two working material suppliers are pillaged and subsequently restored:

- Ottawa's Maize Farm: pillaged132, restored170; Storekeeper resumes171.
- Niani's Flax Farm: pillaged138, restored161. The same Flax later supplies the
  neighboring Bakers in Nioro as well as Tailors.

No adjacent mapped Base/Spec resource is physically destroyed. Recovery occurs,
but the38-turn and23-turn repair delays leave useful room for improvement.

Dockmaster has a more specific spatial requirement than Storekeeper: an adjacent
legal Harbor footprint must lead to a Harbor/Lighthouse chain. These Tailors
instead serve a Holy Site and Theater Square. Their missing Dockmasters should
not erase the value of those other customer chains. Future coastal opportunities
can exercise Dockmaster guidance without imposing Harbor access on every Tailors.

## Guidance over time and follow-through

All **16/16 recorded new-Quarter native best comparisons** consume the exact
published score, version and preceding write. The continuity journal records ten
confirmed best-site memory episodes: five release at foundation, five expire at
their bounded lifetime. One actual improvement change resets its old baseline.
There are63 owned-site baseline quotes and no active-memory support withdrawals.
None of those63 quotes needed to exclude newly assigned workers in this seed;
the earlier Pella test remains the direct staffing/acquisition-transition case.

The five memory expiries are not five native construction failures. They include
best-site opportunities that fail admission, native waiting contracts, and sites
later selected successfully:

| Site / early opportunity | What the existing records show |
|---|---|
| Winnipeg Bakers3049 |Native construction184 waits14/15 on27 and15/15 on28, still accepted at240; fails29. The queue builds a Builder through21, then a Settler. |
| Niani Tailors1131 |First nomination99 finds district capacity2/2 and no build contract. At134 capacity is3/4; the same site is founded. |
| Kerma Bakers2742 |Repeated nominations126/130/134 occur with capacity3/3 and return Not Building/No contract. No Quarter foundation by250. |
| Niani Bakers1130 |Early152 nomination has capacity4/4 and no build contract. Later Nioro can use this footprint with0/1 capacity; it founds179. |
| Iken Tailors3115 |Native construction4693 remains accepted at210.6 on214–215 and waits14/15,15/15, then fails216. A Monument occupies production until214, followed by Send Aid valued312.5. |

This makes capacity and queue timing concrete priorities for1.6. Raising every
Quarter score would not create district slots, and it would change sensible
competition with projects. Keep the current values while targeting admission
and reconsideration of still-useful opportunities after a waiting tree expires.
The publication-time full status remains valuable future planning: Meroë's
Tailors nomination also has a full snapshot before later construction.

## Purchases, economy and diagnostics

The original five AIs buy114 tiles for9280 Gold. All114 measured Treasury debits
match their requested amounts and have later ownership confirmation. There is
no Quarter-footprint purchase in this seed; the established Pella payment route
is not exercised again. Generic savings records include156 category-fund failures
despite sufficient total Treasury.

At250, the five AIs hold49 cities and657 population:

| Per-turn measure | Total | Average per original AI |
|---|---:|---:|
| Production |2533.0 |506.6 |
| Gross Gold |5527.3 |1105.5 |
| Net Gold |2508.3 |501.7 |
| Food surplus |348.4 |69.7 |

These describe the new world. Its different seed supplies no matched untuned
balance comparison. Ten25-turn economic samples are retained for later analysis.

All20 passive native hooks finish frozen with zero faults, active calls or
buffered records;23981 native records are retained. There are no Lua runtime
errors. No Civ process, console owner or test task remains running. Standing
15-minute monitoring and completed-run analysis are recorded in both the CSC
skill and project feedback.

[Compact results, identities and native excerpts](csc-ai-new-continents-20261115.json).
Full derived planning/economic records are in `analysis.json` at the artifact
root. Source logs, selected checkpoints and final closure receipts remain under
`continents250-01`.


## Follow-up: why the+2 floor produces few additional Quarters

The subsequent [bid-funnel analysis](csc-ai-quarter-bid-funnel-20261115.md)
changes the priority above: many+2 bids never reach a native Quarter win.
99 distinct+2 identities receive positive bids, but only three+2 native best
comparisons occur, all for full-capacity Niani. In918 same-city/round observations
with owned+2 offers and ready Quarter capacity, the other native selection has
higher utility every time (medians2539 versus397). Whole-Quarter calibration now
needs review alongside admission and request lifetime. This does not establish
that every lower bid should win, or justify a universal multiplier.

A passive-label correction also surfaced: raw `qualified` flags use the old+3
observer constant. Numeric geometry and actual outgoing+2 bids are intact. The
follow-up recomputes bands at2; the old distinct-qualified summary fields retain
their+3 meaning. The maintained observer now labels the active policy minimum.
