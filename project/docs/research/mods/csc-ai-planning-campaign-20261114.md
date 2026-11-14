# Three-game planning observation campaign

**Status: three full games started, 14 November 2026. Full outcomes pending.**

Henno requests three normal-play tests of Quarter planning, material retention,
tile funding and the surrounding district economy. The older automatic goal
remains paused. These games are separately authorised; no upstream PR is planned.

## Fixed protocol

Three fresh Small/Prince/Online games through turn 250, with normal research and
starting conditions. The seeds are selected before observing outcomes:

| Map | Map seed | Game seed |
|---|---:|---:|
| Continents | 18461107 | 29461107 |
| Pangaea | 18431267 | 28681391 |
| Fractal | 19672039 | 29812257 |

All use City Lights, Resourceful 2 and Sukritact's Resources, alongside main CSC
and our local CE development package. WildW develop remains `2986a746` when
checked before these tests; our required APIs are still local. CE DLL is
`400e6755…`, original XP2 is `092abfbb…`. Exact package/mod hashes are pinned by
each controller run. The accepted previous gameplay/art package is retained;
only current CSC AI modules and its passive UI fact bridge are overlaid, so
unrelated workspace SQL/art changes are not accidentally included.

The candidate fixes Base-only supplier acquisition to consider first missing
Base and Spec independently, with shared-plot deduplication and unchanged bid
bands. Base improvement preparation requires the working Stage 2 buyer; Spec
improvement preparation requires the working Stage 4 buyer. Loaded resource
tags and valid-improvement mappings apply equally to resource origins and both
Quarter families. These are policy changes, distinct from passive recording.

The shared controller owns launch, console, five-turn autoplay boundaries,
checkpoint saves and cleanup. Human/agent observation is about every 15 minutes.
No injected probe treatment, extra production orders, unlocks or subsidies.
Short diagnostic qualification precedes the three full outcome games.

## Measurements and interpretation

| Problem | Record | Limit |
|---|---|---|
| 2.1 | Quarter/customer/provider foundation and completion order, all stages and loaded replacements | Capture and pre-existing/unknown dates remain separate |
| 2.2 | Adjacent resource, improvement, ownership, pillage and working-supplier changes; first/last class counts | Missing map callbacks use per-turn fallback; fog is not harvest |
| 1.5 | Four native category savings accounts, weights, Treasury, targeted affordability, purchase contracts, real debits and ownership | A category budget is not a per-tile savings promise; unknown lineage stays unknown |
| 1.7 | Published no-positive-offer/deferred scopes and later reconsideration, alongside native selector records | Packet state alone is not native decline or a complete successful cycle |
| 1.1–1.2 | Final loaded Base/Spec tags, improvement mappings, provenance and map instances; CL provider tags | SQL loading is separate from consumption and outcomes |
| 1.4 | The planner's actual geometry calls and accepted offers versus placed Bakers/Tailors | Geometry upper bound is not native legality or a guaranteed investment |
| Calibration | All district foundations/completions, UI-event adjacency and matched native district-choice totals | Cached comparison/drain time differs from foundation time; unknown joins are reported |

The passive observers reuse existing planner calls and CE drains, adding no
second economic forecast sweep. Native savings hooks make no game-function
calls or game-data writes, qualify the exact binary and entry bytes, use bounded
journals, and remain installed until controller-owned process exit. Diagnostic
faults, missing observations and capacity limits invalidate the affected evidence
rather than silently becoming zeros. Every failed attempt is retained.

Ordinary adjacency yields and the private AI placement yield are reported
separately. Native forecast totals are Q8 utility, not yields or Gold. Report
the actual last matched native choice and its observable age; do not describe a
cached total as a fresh at-foundation calculation. An additional read-only hook
at the already qualified district-choice return records the exact game turn,
selected type/XY and guarded cached total. It uses the loaded district count
and CE's verified matrix schema, adds no new hook site, and reports unreadable
or unmatched data explicitly. It cannot identify every existing foundation
without calling the engine, so physical chronology remains separate.

The stock UI adjacency API does not include CSC's property-driven Quarter
adjacency. The Quarter's own loaded-rule evaluator supplies its placement
quality; the ordinary API supplies the surrounding vanilla-district comparison.
Private placement yield remains separate from real economic yields.

## Short qualification and corrections

The same-seed short game reaches50 and exits0 with exact preference restoration.
It records104 targeted savings checks,20 actual debit pairs, and UI-event
adjacency for every39 original-AI district foundation:17 City Centers,9 Wonder
footprints,3 Campuses,3 Theaters,2 Holy Sites,4 Bakers and1 CL Rural Community.
The four Bakers are all at least+3 by the CSC loaded-rule evaluator, two at+4.
This is instrumentation evidence, not the result of the three full games.

All four material groups and seven existing CL provider aliases validate in the
actual loaded database. Resource provenance resolves from producer declarations.
The active Suk Gold has Tailors Spec and Mine support. An obsolete Resourceful
`GOLD2` tag is retained as a warning and ignored by resource iteration.

Two qualification attempts stop before autoplay, close and restore: the first
overly strict unused-alias check, then passive enumeration of vacant player
seats whose city collection is nil. The observer now uses the alive roster.
The successful short game has no policy/planning/native-observer fault. After
its verified exit, a host handle check incorrectly polled the already released
handle; log/package archiving and summary generation were completed offline.
The asynchronous Frida-message archive is missing for that short attempt and
is not fabricated. Native frozen counters, full journals and clean exit remain
available. The driver now detaches through the controller's existing
`after_native_exit` callback while the held handle is still valid. Full runs use
this correction. Exact-turn selected-score rows are an additional diagnostic
added after the short run and will be qualified in their full-run data.

The final focused offline suite passes60 tests: policy parity, transparent
wrappers, material/order histories, native layout/funds/payment guards, database
qualification, timing boundaries and evidence joins. These do not substitute
for native purchases, Builder execution or the full-game outcomes.

## Evidence location

Campaign root: `C:/Users/Shadow/Desktop/Codex/csc-ai-planning-campaign-20261114/`.
Each run archives source identities, optional-mod manifests, SQLite qualification,
map-resource census, Lua/native journals, five checkpoint saves, controller
receipts, terminal census, errors and restoration verification.

Results and qualifications will be appended after the games.

## Early audit: resource mapping is not complete transaction registration

The first full game's first scheduled check reaches130 with healthy recording.
An additional journal read through134 has398 exact-turn district selections,
all398 guarded cached totals readable, and42 actual negative debit pairs with
measured deltas matching the requested charges. This qualifies the added
choice-score recorder; it is not a completed outcome game.

The completed short game contains two different material incidents:

| Turn / identity | Change | Interpretation |
|---|---|---|
|34, player1, Bakers1059, material1060|Flax remains; Farm removed; working Base1→0|Last working improvement lost; actor unknown. Quarter was pillaged on32, which does not identify who removed the Farm.|
|40, player4, Bakers1383, material1308|Wheat removed under a new Wonder; Base2→1|A physical resource loss, while Flax1457 remains. City-build log selects Etemenanki that turn; the plot event itself names only the Wonder district.|

Neither loses the last physical Base/Spec deposit. A `lastSpec=true` field means
zero remaining Spec; without a previous positive count it is not a loss event.
The raw per-turn totals and before/after fields retain that distinction.

The loaded mappings include R2 Barley/Sorghum→Farm, Bamboo/Maple→R2 Sawmill,
Cashmere→Pasture, modded Plantation materials→CL Trading Post alternatives,
and Gold→Mine/CL Craftsmen. The generic AI readers recognise these. The short
game directly observes working Barley/Farm and CSC Flax/Farm.

An independent SQL and **read-only loaded-database** audit finds a separate
gameplay-compatibility gap. Some incoming supplier→producer building yields
are registered by literal improvement lists rather than all loaded mappings:

| Improvement | Missing incoming +1 building yield |
|---|---|
|R2 Sawmill|Bamboo→Tailors Workshop Culture; Maple→Bakers Café Food|
|CL Trading Post|Base→Bakers Mills and Tailors Workshop; Spec→Tailors Fashion House|
|CL Craftsmen|Spec→Bakers Café and Tailors Fashion House|
|Pasture|Cashmere Spec→Tailors Fashion House|

CL Trading Post→Bakers Café is registered. Reverse producer→material
Production/Gold and Service supply gates use generic collections/class checks;
the missing incoming roots do **not** show those other effects are absent.
The central ledger's expected incoming Food/Culture can therefore be optimistic
for these combinations. Resource adjacency and generic AI eligibility remain
distinct from delivered transactions. Do not claim complete economic parity.

Evidence: loaded DB SHA256
`617d48affa3c6c7b76c722a42fb66854270628a2a1053dc7272cb030d14d9354`, matching
Continents preflight, with stable hash across the read-only query. Sawmill has
only its ordinary river-Production root; Craftsmen has no improvement roots;
Trading Post has Bakers Spec's root only. Connected CSC leaves identify the
missing incoming Food/Culture. Relevant frozen and current compatibility/Quarter
SQL is byte-identical. This is loaded attachment evidence, not an isolated
realised-payout test. The full campaign keeps its frozen content; a separate
compatibility fix should generate duplicate-safe ordinary incoming wrappers
from loaded classes/mappings, preserving Industry/Corporation's special roots.

## Completed Continents arm

Turn250 completes with exit0, exact restoration, all ten censuses and five
archived saves. Native observer freezes with zero faults/active calls and an
empty asynchronous-message archive. Pangaea starts automatically afterward.

| Measurement | Bakers | Tailors |
|---|---:|---:|
|Original-AI foundations|5|1|
|At least+3 at foundation|5|1|
|At least+4 at foundation|2|1|
|Owned Base at foundation|5|1|
|Both owned classes at foundation|2|0|
|Distinct positively offered sites over the game|54|23|
|Distinct geometry-qualified alternatives over the game|124|70|

All six founded sites tie the best offered geometry for their city/type packet
at foundation. Alternatives overlap in time, need native admission/funding and
are not expected construction counts. Forty out of forty recorded new-site
Quarter comparisons read the exact positive bid, preceding write, version and
ordinal. This is delivery, separate from six physical constructions.

Ten distinct mapped physical neighbours comprise seven neighbour-first pairs
(five Bakers City Centers, Tailors Commercial Hub/Theater) and three
Quarter-first pairs (two sales hosts and Broadway). Forty-five CL rural provider
foundations produce no adjacent-provider pair for the treatment cohort. A
separate player0 Tailors→rural-provider pair is observed; that proves the
recording path, not our guidance. No guided Quarter capture occurs.

There are42 packet reconsiderations across21 scopes; one later builds its
Quarter. Managed nonpositive-cell masks operate43,533 times across226 turns.
Typed-decline count0 does not mean no deferral: this candidate uses the managed
column path. These are repeated operations, not43,533 distinct district choices.

The material audit finds six mapped incidents: one nonlast Wheat overwrite by a
Wonder, one Farm removal, one ownership loss and three pillages. Five exhaust
the Quarter's working Base/Spec class; four subsequently recover. No last
physical mapped deposit is destroyed. At250 all six Quarters retain owned Base,
five have working Base; both owned Spec holdings work. One Banana Plantation
remains pillaged. The raw observer also flags an unrelated Potato Farm: its
generic compatible-improvement flag is not a Tailors-material role. Offline
analysis now checks the **previous** resource against loaded class membership,
retains raw observations and excludes that false supplier loss.

The115 measured payments spend11,189 Gold, with all actual debit deltas matching.
Strictly later map contexts confirm all115 owners. None is a dedicated Quarter
purchase or a mapped-material purchase adjacent to an already-existing Quarter.
Two incidental purchases later support a Bakers in a different city. Seven
frontier Quarter offers are published; none is selected while unowned. All45
Quarter choice receipts target owned tiles. Neither class produces a supplier
acquisition offer. Natural exercise of that path remains unshown.

Of520 targeted affordability checks,469 fail;276 fail category-fund gates despite
sufficient actual Treasury. Thirty-four ordinary non-Quarter plans later pay as
funds accumulate. This demonstrates generic waiting/funding, not earmarking for
our Quarter plans. All1619 exact-turn district-choice totals are readable.
For vanilla district types,201/206 foundations excluding City Centers/Wonder
footprints match a preceding pair's total; all308 native-type foundations have
UI-event adjacency. Overall381 cohort foundations include additional CSC/CL
types; keep those categories separate. Choice ages are1–19 turns (median3), so
these remain choice-time quotes, not fresh foundation-time forecasts.

### Native-owner correction

The optional SetOwner receiver `+0x1c` readings (`ownerBefore`, `ownerAfter`,
`ownerMatchesRequest`) are **invalid ownership measurements**. The offset was
qualified on a different resolved plot-data representation (AI-N113), and the
receiver readings do not track AI player IDs. Ignore those fields in all campaign
arms; do not infer their actual field meaning. Independent debit pairs and
strictly later Lua ownership remain valid. Nineteen earliest same-clock Lua
contexts precede payment despite sharing its turn number, so same-clock snapshots
also cannot serve as after-payment proof. The running observer sources stay
frozen; remove the unqualified optional reads after the campaign. This does not
affect CSC policy, scores or game data.

Ghidra now independently confirms the distinction: PurchasePlotContract Update
RVA3fa260 resolves the wrapper's virtual slot+0x30 before reading data+0x1c.
SetOwner RVA616a0 also reads through slot+0x30 and edits through slot+0x38;
coordinates+0x28/+0x2a remain on the wrapper. Complete function bodies of53 and
1391 bytes match reference324c51e9 and current092abfbb exactly. Raw decompiles
and code hashes are retained in `owner-representation-ghidra.json` and
`owner-representation-code-parity.json`. The installed skill records AI-N129;
AI-N113's correctly scoped resolved-data predicate remains valid.

Detailed independent audits are archived as `planning-independent-audit.*` and
`economy-savings-audit.*` in the completed arm. The campaign root also retains
`incoming-exchange-loaded-audit.json` with the qualified loaded modifier graph.

## Pangaea interruption and shared-controller hardening

The original Pangaea session reached205, then finite autoplay stopped advancing
with an open, hidden `DiplomacyActionView` session from AI4 to observer0. The
archived `DiplomacyManager.csv` identifies
`WARNING_STOP_SPYING_ON_ME/NONE/INITIAL/Processing Immediately`. Congress was
hidden too but was not the blocking conversation. The game closed with exit0
and restored preferences; the turn200 checkpoint remains the recovery source.

The shared controller now handles that specific choice-bearing warning through
a separate cancellation path, rather than classifying it as a passive message.
It verifies active finite Core autoplay, observer control, the current/latest
same-participant CSV statement and phase, loaded statement/selection definitions,
and the exact open session's participants. It calls `CloseSession` once, following
the stock Escape cancellation primitive, without selecting a response, promise,
refusal, deal or war. Cancellation can have implicit diplomatic consequences;
receipts record that limitation. Changed state fails closed, and ambiguous sends
or pending cancellation cannot replay. See the
[controller documentation](../../../tools/ai_baseline/full_game_controller/README.md#observer-spy-warning-cancellation-14-november2026).

The24 focused controller fixtures pass, including real Lua51 guard execution,
newer-deal precedence, human-control exclusion, changed session/definition checks
and no resend after an uncertain transmission. A successful continuation past205
does **not** itself establish live exercise of the handler; require the explicit
cancellation receipt. No such receipt was observed in the Pangaea continuation.

Recovery attempt01 loaded200 with44/44 structural rows matching, then stopped
before autoplay because the preflight incorrectly required turn1. Recovery02
uses an explicit start boundary, verifies the same44 rows, reaches250, archives
225/250 censuses and closes with exit0, restored preferences and no asynchronous
native observer messages. Fractal follows as the third fresh seed.

`pangaea250-combined` is a labelled offline derivative, **not an uninterrupted
raw session**. It cuts original Lua at the exact completed turn200 save marker,
excludes abandoned205 evidence, qualifies versions/ordinals by segment, and keeps
an explicit native coverage gap for original pre-save turn200 events whose
ordering against the save is unknown. All ten census boundaries are present.
The raw segments, save hash and merge provenance remain available; Service
evidence must be read from raw segments with the same cutoff.

### Pangaea result and one explained withdrawal

The selected segments contain no original-AI Quarter foundations through250.
Across the game,125 Bakers/43 Tailors geometry-qualified identities include36/6
positive-offered identities. These are changing alternative sites, not42
expected constructions. All four new-site native Quarter BEST comparisons
consume the exact positive bid/write/version with the preceding native ordinal.
There are31 reconsiderations across20 city/type scopes and49,289 managed masks
on223 turns. The1604 district-choice total reads all succeed. Actual plot
payments number71, spending5300 Gold; all measured debits match and all owners
are confirmed in strictly later map contexts. None has Quarter-site lineage;
there are no supplier-acquisition offers or frontier Quarter selections.

London is a useful counterexample to treating every unbuilt offer as inadequate
bid strength. Bakers site783 is offered at prospective adjacency+3 on2–7,
then drops to+2 and is withdrawn from8. The original native choice is on3.
`AI_CityBuild.csv` records contract202 submitted on16 at104 utility and accepted
on25 at−1024; no Quarter foundation follows. A nearby Wonder footprint appears
on7 at708, but the recording lacks that site's pre-Quarter resource snapshots,
so it does not prove which geometric contribution disappeared or that the
Wonder destroyed a specific supplier. The quality withdrawal and negative
later contract value are direct observations; a precise causal native guard
is not. Do not blindly raise bids to force this expired opportunity through.

Lingapura also submits a Bakers contract3171 on154 at112 utility without a
recorded acceptance or foundation. Two later Quarter comparisons occur with
capacity metadata marked full. These cases still require follow-through
diagnosis; the capacity annotation alone is not proof of a native rejection.
There are no built-Quarter customer/provider pairs or supplier-retention cases
for Problems2.1/2.2 in this seed. Zero exercise is not successful protection.
