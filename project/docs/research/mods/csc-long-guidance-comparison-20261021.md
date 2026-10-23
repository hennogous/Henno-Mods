# Longer natural CSC research-guidance comparison

Henno explicitly authorized assembling the demonstrated parts and running a
longer test after reviewing the unresolved restart scenario. This supersedes
the previous decision to end the diagnostic series. It authorizes an experiment,
not deployment of a validated release candidate.

## Design

One sequential OFF/ON pair, natural Medieval start at71 to the turn250 boundary
(179 Online-speed rounds), Prince, Small Continents, vanilla Standard resources,
resource assistance pass4. Map830102/game940104 and the established leader roster.
The five major AI players are the treatment subjects; player0 is a separately
reported autoplay participant. No Quarters, materials, buildings, research
progress or civic choices are injected. No planned resource-loss fixtures.

OFF creates a fresh native world. ON loads the exact archived, unplayed OFF save
before natural play. Actual map, census, preferences and native database parity
gate the comparison. Only twelve CivicModifiers attachments differ in native
tables; only the enabled literal differs in the appended callback. All existing
CSC and vanilla preferences—including the old CSC support-research lists and
ordinary leader civic favorites—remain identical. This differs from the earlier
isolated diagnostic controls that removed those favorites.

Accepted tuning remains Quarter matching-resource presence40, improved-resource
bonus80 owned by ImprovementModifiers, improvement valuation90, Builder50,
native bonus-resource/river/sales guidance12/4/10. Actual Service grants are
unchanged. Installed AI SQL and Lua receive temporary overlays and are restored
after the study; source gameplay files are not changed.

## Six additional Service channels

| Quarter | Stage | Target civic | Potential material condition |
|---|---:|---|---|
| Bakers | 2 | Feudalism | Owned visible Base beside completed, unpillaged Quarter |
| Bakers | 3 | Medieval Faires | Same |
| Bakers | 4 | Urbanization | Base and Specialty at the same Quarter |
| Tailors | 2 | Naval Tradition | Owned visible Base beside completed, unpillaged Quarter |
| Tailors | 3 | Divine Right | Same |
| Tailors | 4 | Opera and Ballet | Base and Specialty at the same Quarter |

Unimproved material sources count. Readiness uses the ordinary CSC scan plus an
explicit check that the individual target civic is not owned. No producer-tech
or building prerequisite is changed. Existing support-research preferences stay
in both arms; the new treatment adds guidance only for these six Service civics.

Each target gets a separate internal yield with DefaultValue1, static bias-100,
an unowned strategy list with+100, and two dormant100-yield CivicModifiers (total
200). Their economic ALL set requires both Has Future Civic and its inverse.
This is the tested inert valuation substrate. Amount200 is a deliberately
unchanged diagnostic weight, not an endorsed balance setting. Applying it to
six targets is a combined treatment, not six independent experiments.

Each strategy has a positive readiness callback and an inverse Forbidden
condition. **Known limitation:** a stopped strategy did not readopt after
temporary material loss in the short probes, despite continued correct callback
returns. The longer trial records eligibility transitions, native Following/
Stopped events and research choices so this limitation remains visible. It may
reduce treatment uptake after pillage or ownership changes. The experiment does
not claim to fix it or validate UI integration.

## Outcomes and preservation

Primary outcomes are first useful eligibility, first target selection and target
completion per player, and active Services at common200/250 checkpoints. Also
report producer/customer building opportunities, source-to-venue relationships,
sales-district links, Quarter/material placement and preservation, mapped
improvements, Builders and charges per city, population, city count and overall
tech/civic progression. Distinguish active links from monetary transactions that
the observers do not instrument. Later differences include cascading world
effects; one paired seed cannot isolate every mechanism or establish robustness.

Primary frozen checkpoints:71,75,100,125,150,175,200,225,250. Builder censuses:
71,100,150,200,250. Research choices/completions are observed naturally each
player turn, with defeat censoring explicit. The native250 hook stops autoplay
at the endpoint; exports retain the actual simulation turn. Diagnostic private
yields must read zero in every recorded city. Endpoint saves and recent native
autosaves are preserved; optional named-save failures do not discard observations.

The hidden supervisor/worker exclusively own FireTuner. The supervisor detects
Civ exit and never restarts it. Failures preserve logs, snapshots and autosaves,
restore temporary files and native preferences where feasible, and stop. Sparse
15-minute follow-ups inspect status files and short logs, not competing native
clients. ON starts after OFF only as the authorized second arm, not as a crash
retry. Exact source and installed files/settings/hashes are archived before each
arm; matching native definitions are independently checked before play.

## Version and locations

- Code version: `natural-six-service-civic-guidance200-forbidden-v1`.
- Worker: `project/tools/ai_baseline/civic_guidance_long_trial.py`.
- Supervisor: `project/tools/ai_baseline/civic_guidance_long_job.py`.
- Evidence: `C:/Users/Shadow/Desktop/Codex/csc-ai-long-guidance-20261021`.
- Study status: `study/job-status.json`, `study/active-stage.json`, active arm's
  `live-status.json`; supervisor state is `supervisor.json`.
- Launch and short stdout/stderr logs are siblings of the evidence directory.

Offline validation passed Python/Lua5.1 syntax, all six callback target/inverse
mappings, owned-target and missing-material suppression, disabled controls,
native schema, source replay and the exact twelve-attachment table contrast.
The historical schema reference had deliberately removed old CSC lists, so the
offline setup reconstructs accepted source before taking its reference inventory;
that preparation was corrected before any native game was launched. This does
not change the native treatment or clear existing preferences.

The prior evidence and lifecycle caveats remain in
[research-influence findings](csc-research-influence-findings-20261021.md).

Follow-up `csc-longer-guidance-comparison` ACTIVE, creation confirmed by app; saved in evidence-root heartbeat.json. Supervisor18192/worker7724 exclusively own FireTuner.


## Control recovery and ON continuation (21 October, 04:26 UTC)

OFF completed the exact native turn250 endpoint and all895 expected research
observations. An independent offline recovery audit verified55 source,
122 installed,46 read-only RST reference and2 RH-example hashes, nine primary
checkpoints, five Builder checkpoints, zero private yields in all recorded
cities, native database validation, named71/250 save hashes, and restoration
of the original144 native preferences with auto-start false. No OFF replay
occurred.

The original controller rejected16 Database.log LocalizedText duplicate-key
errors at final validation. No gameplay database or Lua runtime errors were
present. The one bounded controller repair retains those localization errors
and excludes only that exact localization error from the gameplay-fatal check;
other errors remain fatal. Original scripts, failure/status and log validation
are preserved in study/controller-recovery-v2. Applied SQL text (normalizing
Windows newlines) and callback bytes match the original OFF archive exactly.
Python/Lua5.1 syntax and frozen-baseline schema/replay preflight pass.

Six concurrent worktree source edits were never installed and are preserved.
Installed non-AI files still match OFF's executed archive. ON uses the archived
original-installed SQL/Lua as its baseline; native/installed parity gates remain
strict. Worktree source equality is reported separately from executed-game
validity. Do not overwrite those edits or install them during this pair.

Controller revision long-pair-v2-scoped-errors-frozen-source resumed ONLY ON
through --continue-study, supervisor4108. Logs are sibling .v2.stdout.log and
.v2.stderr.log; launch .v2.launch.json. OFF is reused offline, never rerun.
No further blind native repair or additional games are authorized by this
recovery. Source gameplay baseline remains untouched; no candidate deployed.


## Completed results — 21 October 2026

Both arms completed exact native turn250, with895 uncensored player-turn observations each. The provisional candidate did **not** improve Service activation in this paired world. Keep the accepted baseline; no candidate deployed and no further games launched.

Unless stated otherwise, all result tables below cover players1–5. Player0 is excluded from these statistics, but a scope defect means it was **not untreated**: native AI_Victories records player0 Following Bakers channels1 and2 at84, then Stopped at90/105. The callback relied on `not IsHuman()` rather than an explicit player-ID exclusion, which did not keep the autoplay slot out. Its readiness telemetry was not recorded because telemetry filtered1–5. This limits the treatment to a combined world comparison, not a clean five-player-only intervention. No replay or corrective extra test was performed.

### Research influence and actual choices

All55 initial native civic score records match. After activation74, target valuation changes are large: at75 Germany Feudalism and Medieval Faires each gained1376 score points; Nubia gained2718 and1812 respectively. These are native valuation observations, not proof that the next choice was forced. Later scores also reflect world divergence.

Naval Tradition completed5/5 OFF and5/5 ON. Its completion turns (OFF→ON) were Germany80→80, Nubia109→103, Phoenicia112→110, Vietnam104→103, Greece102→100. Only Nubia actually became material-eligible for Naval guidance (84); Germany was already researching it at71. Do not attribute every timing difference to direct guidance.

Feudalism, Medieval Faires, Urbanization and Divine Right also completed5/5 in both arms. Opera and Ballet completed0/5 OFF versus2/5 ON (Germany220, Nubia242), but neither completing player ever became eligible for its guidance channel. Vietnam became eligible222 and adopted its channel, yet did not select or complete the target by250. The2-vs0 outcome is not direct evidence of successful material-targeted Opera guidance.

The early civic order was largely unchanged. Observed sequence prefixes match for25 choices Germany,28 Nubia,17 Phoenicia,9 Vietnam and39 Greece; Greece has no observed order divergence in the common sequence. The first observed order differences were Germany Totalitarianism193 vs Space Race182, Nubia Totalitarianism226 vs Globalization214, Phoenicia Mobilization174 vs Colonialism181, Vietnam Humanism123 vs Diplomatic Service118. These later differences are descriptive, affected by ordinary world divergence and potentially different observation of short-lived selections. Earlier completion on the same path is not a different choice.

Full target timing uses **first eligible / first observed selection / natural completion**, native turns. A dash means not observed, not a zero-turn event.

| Player | Target | OFF eligible / select / complete | ON eligible / select / complete |
|---|---|---|---|
| Ludwig / Germany | Feudalism | 74 / 86 / 88 | 74 / 87 / 91 |
| Ludwig / Germany | Medieval Faires | 74 / 94 / 98 | 74 / 98 / 102 |
| Ludwig / Germany | Urbanization | 74 / 143 / 145 | 74 / 146 / 149 |
| Ludwig / Germany | Naval Tradition | — / 71 / 80 | — / 71 / 80 |
| Ludwig / Germany | Divine Right | — / 101 / 104 | — / 105 / 107 |
| Ludwig / Germany | Opera and Ballet | — / — / — | — / 219 / 220 |
| Amanitore / Nubia | Feudalism | 74 / 85 / 90 | 74 / 81 / 86 |
| Amanitore / Nubia | Medieval Faires | 74 / 101 / 107 | 74 / 93 / 101 |
| Amanitore / Nubia | Urbanization | — / 172 / 175 | — / 154 / 159 |
| Amanitore / Nubia | Naval Tradition | 84 / 107 / 109 | 84 / 101 / 103 |
| Amanitore / Nubia | Divine Right | 84 / 109 / 113 | 84 / 103 / 108 |
| Amanitore / Nubia | Opera and Ballet | — / — / — | — / 241 / 242 |
| Dido / Phoenicia | Feudalism | 74 / 71 / 83 | 74 / 71 / 83 |
| Dido / Phoenicia | Medieval Faires | 74 / 103 / 110 | 74 / 102 / 109 |
| Dido / Phoenicia | Urbanization | — / 171 / 174 | — / 176 / 181 |
| Dido / Phoenicia | Naval Tradition | — / 110 / 112 | — / 109 / 110 |
| Dido / Phoenicia | Divine Right | — / 112 / 116 | — / 110 / 115 |
| Dido / Phoenicia | Opera and Ballet | — / — / — | — / — / — |
| Lady Trieu / Vietnam | Feudalism | 74 / 71 / 83 | 74 / 71 / 82 |
| Lady Trieu / Vietnam | Medieval Faires | 74 / 99 / 103 | 74 / 97 / 102 |
| Lady Trieu / Vietnam | Urbanization | — / 159 / 161 | — / 157 / 160 |
| Lady Trieu / Vietnam | Naval Tradition | — / 103 / 104 | — / 102 / 103 |
| Lady Trieu / Vietnam | Divine Right | — / 104 / 109 | — / 103 / 106 |
| Lady Trieu / Vietnam | Opera and Ballet | — / — / — | 222 / — / — |
| Pericles / Greece | Feudalism | 74 / 71 / 81 | 74 / 71 / 81 |
| Pericles / Greece | Medieval Faires | 74 / 96 / 101 | 74 / 93 / 99 |
| Pericles / Greece | Urbanization | — / 149 / 152 | — / 144 / 146 |
| Pericles / Greece | Naval Tradition | — / 101 / 102 | — / 99 / 100 |
| Pericles / Greece | Divine Right | — / 102 / 105 | — / 100 / 102 |
| Pericles / Greece | Opera and Ballet | — / — / — | — / — / — |

Natural lifecycle evidence: Nubia’s Medieval Faires strategy stopped88 while the target was still missing, real eligibility returned94, and there was no subsequent native Following. This reproduces the restart gap in natural play. Callback `active=true` after94 describes the Lua return, not native strategy adoption. Target-owned transitions correctly return false; many strategies stop at their natural target completion. This does not establish every lifecycle/reload/ownership case.

### Checkpoints and Services

| Turn | Cities OFF→ON | Population OFF→ON | Completed Quarters OFF→ON | Active source/stage Services OFF→ON |
|---|---:|---:|---:|---:|
| 200 | 36→32 | 398→420 | 46→47 | 12→9 |
| 225 | 41→39 | 518→526 | 54→53 | 20→11 |
| 250 | 45→42 | 629→606 | 58→57 | 18→12 |

Service counts are active native source properties per city/stage, not unique cities and not monetary transaction counts. At250:

| Service | OFF | ON |
|---|---:|---:|
| Mill→Granary (Growth) | 11 | 8 |
| Bakery→Market (Housing) | 5 | 3 |
| Café→Zoo/Ferris Wheel | 0 | 0 |
| Workshop→Lighthouse (Production) | 1 | 0 |
| Tailor→Temple (Faith) | 1 | 1 |
| Fashion House→cultural venue | 0 | 0 |

All sampled source-property activations match the summarized civic/source-building/material/improvement/venue gates at200/225/250; no positive-property/false-gate or all-gates-true/inactive mismatch was found in those samples.

At250 every Bakers source Quarter owner has the first three Service civics, and every Tailors owner has Naval Tradition/Divine Right. Research is therefore not the remaining bottleneck for these stages at the endpoint. Most Quarters lack mapped materials; stage4 also needs both classes, improved, at the same Quarter. Gate columns are separate marginal counts, not additive reasons:

| Arm/service | Quarters | Civic | Producer | Owned materials | Improved materials | Adjacent venue | Active |
|---|---:|---:|---:|---:|---:|---:|---:|
| OFF/BAKERS2 | 41 | 41 | 40 | 17 | 15 | 31 | 11 |
| OFF/BAKERS3 | 41 | 41 | 32 | 17 | 15 | 16 | 5 |
| OFF/BAKERS4 | 41 | 41 | 21 | 1 | 0 | 8 | 0 |
| OFF/TAILORS2 | 17 | 17 | 14 | 4 | 3 | 3 | 1 |
| OFF/TAILORS3 | 17 | 17 | 13 | 4 | 3 | 4 | 1 |
| OFF/TAILORS4 | 17 | 0 | 10 | 0 | 0 | 9 | 0 |
| ON/BAKERS2 | 36 | 36 | 34 | 13 | 10 | 28 | 8 |
| ON/BAKERS3 | 36 | 36 | 30 | 13 | 10 | 16 | 3 |
| ON/BAKERS4 | 36 | 36 | 15 | 1 | 0 | 6 | 0 |
| ON/TAILORS2 | 21 | 21 | 20 | 5 | 5 | 3 | 0 |
| ON/TAILORS3 | 21 | 21 | 17 | 5 | 5 | 8 | 1 |
| ON/TAILORS4 | 21 | 10 | 10 | 1 | 1 | 14 | 0 |

In particular, ON has21 Tailors Quarters,5 with improved Base material, and3 with a nearby Lighthouse, but these conditions do not align on an eligible active stage2 source. One ON Tailors Quarter has both improved material classes; its owner Vietnam lacks Opera and Ballet, so stage4 remains inactive. The two players that researched Opera have no corresponding material-ready stage4 Quarter.

Built producer/venue adjacency links at250 (independent of materials/research) are OFF→ON: Mill–Granary30→27, Bakery–Market15→14, Workshop–Lighthouse3→3, Tailor–Temple4→6, Fashion House–Amphitheater5→6. Café–Zoo4→1 and Café–Ferris Wheel2→0. Active source/venue links coincide with the Service table above. These are snapshot links/opportunities, not observed sales transaction frequencies.

### Placement, improvements and preservation

Correct and incorrect here mean owned adjacent resource plots mapped or unmapped to that industry. A shared resource may contribute to more than one Quarter; averages use adjacency incidences per completed Quarter.

| Quarter metric at250 | OFF | ON |
|---|---:|---:|
| BAKERS completed | 41 | 36 |
| BAKERS with Base | 17 | 13 |
| BAKERS with Base+Spec | 1 | 1 |
| BAKERS with no owned mapped material | 22 | 22 |
| BAKERS mean correct adjacent resources | 0.71 | 0.56 |
| BAKERS mean incorrect adjacent resources | 0.93 | 1.06 |
| BAKERS unique adjacent mapped plots improved | 18/27 | 14/19 |
| TAILORS completed | 17 | 21 |
| TAILORS with Base | 4 | 5 |
| TAILORS with Base+Spec | 0 | 1 |
| TAILORS with no owned mapped material | 13 | 16 |
| TAILORS mean correct adjacent resources | 0.24 | 0.29 |
| TAILORS mean incorrect adjacent resources | 1.47 | 1.19 |
| TAILORS unique adjacent mapped plots improved | 3/4 | 6/6 |

At250 the pooled industry-plot improvement fraction is21/31 OFF and20/25 ON. This combines per-industry unique plot records, so Flax mapped to two industries can appear twice. Total unpillaged improvements across players1–5 are294→326 (6.53→7.76 per city), despite fewer ON cities. There is no evidence here that research guidance solved selective Quarter placement.

Preservation tracks mapped material adjacent when each Quarter was originally placed. OFF has41 such incidences and11 resource losses (10 unique plots),9 losses ending under a district. ON has36 incidences and11 losses (9 unique plots), all11 ending under a district. Incidences can repeat shared resource plots. No lost resource was improved at the original Quarter-placement observation. In ON,2 unique lost plots have an observed resource improvement before a later district appeared there; this supports that improved resources can subsequently be replaced. Removal immediately before district placement is not instrumented, so do not claim exact improvement state at that instant or call every other loss unimproved.

### Per-player endpoint and harm checks

| Player | Cities | Population | Bakers/Tailors | Improvements | Builders (charges) | Builders/city | Techs/civics |
|---|---:|---:|---|---:|---|---:|---|
| Ludwig / Germany | 10→6 | 136→103 | 9/2→6/4 | 58→60 | 4 (8)→5 (14) | 0.40→0.83 | 69/56→71/60 |
| Amanitore / Nubia | 12→10 | 169→155 | 12/5→10/6 | 101→83 | 7 (21)→3 (10) | 0.58→0.30 | 68/53→70/58 |
| Dido / Phoenicia | 7→4 | 118→68 | 5/2→2/2 | 39→30 | 1 (3)→0 (0) | 0.14→0.00 | 55/45→51/41 |
| Lady Trieu / Vietnam | 6→10 | 78→130 | 6/3→8/3 | 30→82 | 5 (12)→4 (12) | 0.83→0.40 | 60/45→66/52 |
| Pericles / Greece | 10→12 | 128→150 | 9/5→10/6 | 66→71 | 2 (7)→7 (19) | 0.20→0.58 | 60/53→58/52 |

Builder totals are19→19, with51→55 charges; pooled Builders/city0.42→0.45. These are surviving unit censuses, not an estimate of all Builders produced or a diagnosis of Builder overspending. The baseline Builder incentive50 did not change. Tech totals312→316 and civic totals252→263 rise while total population629→606 and cities45→42 fall. Different wars/ownership/settlement and ordinary world divergence prevent attributing these aggregate changes to a specific research choice. Phoenicia ends with zero Builders ON and substantial city/population loss; that is a harm observation, not proof the unchanged Builder incentive caused it.

Highest unlocked era (not full completion of that era):

| Player | Tech era OFF→ON | Civic era OFF→ON |
|---|---|---|
| Ludwig / Germany | Information→Future | Future→Future |
| Amanitore / Nubia | Future→Future | Information→Future |
| Dido / Phoenicia | Information→Information | Information→Atomic |
| Lady Trieu / Vietnam | Information→Information | Information→Information |
| Pericles / Greece | Information→Information | Future→Information |

### Evidence audit, deviations and disposition

Independent read-only audit: `project/tools/ai_baseline/civic_guidance_long_audit.py`; postprocessor: `civic_guidance_long_results.py`. Evidence: `study/post-run-audit.json`, `compact-results.json`, native snapshots/logs and version archives. Structural/data audit passes. Intended five-player-only treatment scope fails because player0 also adopted two strategies; this is explicitly recorded, not repaired by replay.

Each arm has55 source,122 installed,46 read-only RST-reference and2 RH-example files hash-verified. Only native CivicModifiers differs, with exactly12 intended additions. The two installed pair differences are AI SQL and Lua; all other installed files match. Callback bytes differ only in enabled literal, and SQL overlays only in attachment lines. Actual initial map/census/preferences match. Both arms have895/895 observations, exact250 endpoints, nine primary/five Builder checkpoints, and zero private city yield readbacks. Impossible FutureCivic AND NOT FutureCivic requirements are confirmed in native ALL sets; actual Service mechanics were not migrated or duplicated.

OFF was recovered offline after a final validator treated16 exact LocalizedText duplicate errors as fatal. Original scripts/status/failure remain under controller-recovery-v2, and no OFF replay occurred. ON used the single bounded controller repair; no further native repairs or games. Localization duplicates are retained separately rather than described as clean localization. Executed OFF pins were checked before repair; ON executable pins pass. Six concurrent uninstalled worktree changes remain preserved. Installed AI SQL/Lua were restored exactly to archived original baseline, original144 native preferences restored with auto-start false; source_unchanged=false correctly describes the independent source edits, while baseline_reference_unchanged=true.

All legacy supply-signal warnings at100/150/200/250 are explained on offline rule review: the old probe multiplies improvement80 per Quarter rather than once per industry and counts presence40 from incomplete/pillaged Quarter sources. No flagged warning remains unexplained under the actual rules; this is a review of flagged samples, not an exhaustive new plot-level validation. Raw warnings were preserved. Service gate/property cross-checks have zero mismatches at200/225/250.

Named save hashes:

| Arm | Initial71 SHA256 | Endpoint250 SHA256 |
|---|---|---|
| OFF | `004422590cbeae8e82cf1ee4a200403be212fca3b7daa148e06075dfd71e6de3` | `953a7411616dedc033926e684a5e00488e1552ecf0c58751a85e40cd52d7932c` |
| ON | `3866aacd08cc9a07c1915d2010ad88c77c7cc2692d2365a8a601dd82c45bc025` | `3ff9e351b242014febb85f2e6460488c20ec6cf280f0f5571db299453f355830` |

Each arm retains hash-manifested autosaves named248/249/250. Their turn source is the filename; they were not independently reloaded. Named endpoint actual250 is natively confirmed. OFF’s initial save is the ON loaded origin; ON’s own newly written initial save can have a different binary hash despite identical actual world/census.

One paired saved origin, one seed, six combined guidance channels, unintended autoplay0 exposure and the known restart failure limit inference. Diagnostic Amount200/Value100 remains provisional; UI/human recommendation behavior and release integration remain unvalidated. The result demonstrates selective research valuation and some timing/path divergence, but does not establish better research choices or more Services. Keep the accepted baseline. No silent candidate deployment, extra seed, deferred game series or QA-framework work.

Follow-up `csc-longer-guidance-comparison` DELETED after completion and user notification; app returned deleteStatus=deleted. Confirmation saved in evidence-root heartbeat.json. No additional games scheduled.


## Follow-up: residual Naval Tradition incentives

Checked OFF’s archived native database after Henno questioned the5/5 Naval result. No always-on/trait-owned Naval favorite or CSC fixed-list registration remains. There is exactly one Naval AiFavoredItems row: CSC_AI_SERVICE_4_Civics / CIVIC_NAVAL_TRADITION / Favored1 / Value0. It is UNOWNED (LeaderType/AgendaTypeNULL), SystemCivics, linked to legacy STRATEGY_CSC_AI_SERVICE_4 via CallLua CSC_AI_ServiceResearchReady(plan4). Native OFF logs show only Nubia/player2 Following84 and Stopped109 among players1–5; the other four never followed that old Naval strategy. The only Naval CivicModifiers attachment is ordinary CIVIC_AWARD_ONE_INFLUENCE_TOKEN, with no experimental private-yield attachment in OFF.

Correction of shorthand: OFF is **without the NEW six private-yield guidance channels**, not a fully guidance-free/vanilla control. Existing old CSC support/research lists were intentionally preserved identically botharms. Earlier isolated tests did not establish strategy-owned Civics valuation consumption, so the row/Following alone cannot be credited for Nubia’s choice. At native71 allfive already own DefensiveTactics, Naval’s direct prerequisite; Germany is already researching Naval. This Medieval-start context differs from earlier Ancient-start runs. Evidence study/naval-residual-guidance-audit.json. No source/game edits or new tests.
