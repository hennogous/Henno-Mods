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
