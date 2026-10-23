# CSC AI tuning

Experimental Bakers/Tailors tuning. Current source uses broad native bonus-resource and river adjacency, reciprocal sales placement signals and a stronger general improvement preference. The native feature-marker experiment was rejected because it interfered with Builder planning and district legality; its code is unregistered and archived. See [marker experiment](../research/mods/csc-ai-markers-rejected-20261017.md).

| Signal | Coefficient | Mechanism |
|---|---:|---|
| Quarter beside sales district | 10 per neighbour | Native District_Adjacencies |
| Sales district beside Quarter | 10 per neighbour | Reciprocal; excludes City Center placement |
| Quarter beside a bonus-class resource | 12 per neighbour | Native AdjacentResourceClass; includes modded bonus resources |
| Quarter with river access | 4 | Native AdjacentRiver, following the Commercial Hub rule |
| Improvement base valuation | 90 (vanilla 3) | Global PseudoYields.DefaultValue, following RH |
| Builder production priority | 50 (stock has no Builder entry) | Major-civ UnitPriorityBoosts / Units; reduced from RH900 |

These are experimental inputs, not calibrated score equivalents or promised percentage improvements. There is no new Quarter construction or civic preference. The former CSC +50% improvement preference is removed; the base now starts at 90 before other active native biases. The Builder priority is a separate system, not a percentage or a promised unit count. Base materials support stage 2/3 Services; Specialty enables rarer stage 4. Material-free Quarters remain available for sales.

## Native representation

`Data/CSC_AI.sql` generates sales edges from live Bakers/Tailors sales tags, expands direct unique district replacements and deduplicates. Order 3500 follows compatibility producers, including Leu's Garden at 2005. Native adjacency retains its own ownership/completion semantics; it cannot express all CSC transaction conditions. Generic Wonders are excluded. The current official-content setup generates 33 sales edges.

`YIELD_CSC_AI_PLACEMENT` is separate from the six real yields. It has no conversion into real currency, resource/building/citizen/specialist yields or trade-route output. The signal can exist as inert virtual human output; UI filtering hides it. No dummy technology is added. The improvement valuation and Builder priority do not issue specific Builder orders or plan Services.

`Lua_UI/AI/CSC_AI_UIFilter.lua` creates a UI-context facade over the unchanged read-only cache. It filters only CSC's private yield and adjacency rows during enumeration, preserving indexed lookup and other mods' rows. Gameplay sees the full native database. ToolTipHelper/Pedia use include-prefix hooks; existing CSC PlotInfo/PlotToolTip wrappers include the filter. ReportScreen includes the normal GS chain after filtering. Other UI-mod replacements require separate compatibility checks. The marker-specific feature filter and UnitPanel clearing workaround have been removed.

The broad resource rule uses `RESOURCECLASS_BONUS` without exact Quarter material matching or improvement requirements. It can reward an irrelevant bonus resource, including one disabled by the animal-resource setting; the actual CSC Service gates still require the correct mapped, improved Base supplies. It does not guide toward Specialty resources. River guidance uses the same predicate as the native Commercial Hub. These signals do not change district legality, resource improvement rules or the real economy.

Only implemented Bakers/Tailors and their direct district replacements receive these rules. For future Quarters whose Base materials are features, add appropriate native `AdjacentFeature` rules when implementing them, using existing map features rather than synthetic markers. No future Quarter rules are activated now.

There are no marker definitions or automatic map-feature writes in current tuning. Earlier `MOD_CSC_AI_MATERIAL_*` conditional modifiers remain removed.

## Evidence and limits

The [paired Online baseline](../research/mods/csc-ai-paired-standard-20261016.md) has ten untuned turn-250 games. The [v1 matched-seed trial](../research/mods/csc-ai-tuning-v1-20261017.md) combined sales guidance, improvement preference and conditional material modifiers. Sales co-location increased substantially; material choice did not show a convincing improvement, and more supporting deposits were covered. A single combined treatment cannot isolate the contribution of each signal. That trial is not a benchmark of the current bonus/river candidate.

The [marker trial](../research/mods/csc-ai-markers-rejected-20261017.md) confirmed that native feature adjacency enters prospective placement previews, but rejected features as metadata. The [new broad bonus/river matched-seed trial](../research/mods/csc-ai-native-bonus-river-20261017.md) completed through 250: Bakers actual Base choice 24/27 versus baseline 14/25 and v1 16/28; Growth Service source cities 6 versus 1 and 2. Builder follow-through and resource preservation remain weak. Tailors have only five Base-choice opportunities. One seed and the combined treatment do not establish general superiority or isolate each weight.

The user chose broad bonus-resource guidance to avoid feature-marker side effects and the uncertainty around conditional modifier planning. The matched-seed comparison measures Base placement, river access, material retention, improvements, sales co-location and endpoint wrong-material proxy matches. Additional seeds remain necessary before calibration. The improvement preference is a native list input; increasing it from 25 to 50 does not promise twice as many improvements.

## RomanHoliday evidence

Astra reviewed read-only `Desktop/Codex/csc-ai-feasibility/RHAI-reference`, v4.34 Patreon Beta, commit `91584816e88f458461ae132e30d6860adba97eed` from `https://github.com/Roman-Holiday/RHAI.git`. RH was not enabled in CSC trials.

- `core/Strategies/Relic_Strat.sql:112,255,482`: virtual yield/bias.
- `core/Strategies/Internal_Strat2.sql:992–1011`: native placement adjacency.
- `core/Leaders/DLC/Rise_and_Fall.sql:169–190`: native AI-gated Farm/Mine adjacency modifiers carrying the placement yield for Seowon.
- `core/Strategies/Extended_Strat.sql:133`: improvement pseudo-yield preference.
- RH's ReportScreen/tooltip/PlotInfo/Pedia code filters virtual yields explicitly.
- `core/Main/LAI_Main4.sql:976–985` mirrors RH's placement yield into real Science in a separate mechanic. CSC does not copy this.

The shipped adjacency schema matches exact features, improvements, districts and terrain, plus broad resource predicates. It has no arbitrary plot-property or CSC resource-tag predicate. RH's active `Internal_Strat2.sql:1083–1104` scores existing features and broad resources; it does not establish a separate invisible marker layer. The proposed `IMPROVEMENT_RH_PRESERVE_ADJ` is inside the comment block at `core/Leaders/DLC/New_Frontier_Pass2.sql:603–670`. It is not evidence of a deployed marker technique.

## Verification and deployment

`validate_tuning.py` checks the current sales/bonus/river SQL against a read-only native DB memory copy, including repeat application, private-yield rules, exact bonus/river predicates and attachments, absent legacy material modifiers, improvement base 90, Builder priority 50 and removal of the former CSC percentage layer. It discards obsolete experimental adjacency rows in that memory copy to model a fresh load. `test_ai_ui_filter.py` exercises the actual facade against a read-only cache and the shipped ReportScreen worked-tile function.

`deploy_ai.py` uses the focused SDK manifest deployer, backups and an explicit file/action allowlist. It removes the retired marker action/file registration and restores the original CSC UnitPanel. A normal new game rebuilds its DB without marker feature definitions. The bonus/river candidate is recorded at `Desktop/Codex/csc-ai-native-bonus-river-20261017/`: SQL validation passed with 33 sales edges and four resource/river attachments, only the private adjacency tables and own preference changed, and repeated execution was identical. The completed natural retry, comparison and verification are under `retry-01/`; the excluded first attempt native-crashed around 94 and remains under `trial/`. Original preferences were restored and freshly verified; no controller is active.

The marker smoke fixtures are retained as research tools, not ordinary baseline tools. `validate_markers.py` requires explicitly supplied archived SQL. `analyze_markers.py` reads archived outputs and pins the tested deployment rather than current source. `tuning_trial.py` and its historical source pins belong to the v1 experiment; review assumptions before reusing it for a different candidate.


## Improvement valuation versus Builder production

User clarification after the v3 trial: the goal is more Builder production. The
v3 value of 50 was an `AiFavoredItems` preference in the PseudoYields system, not a
replacement for `PseudoYields.DefaultValue`. Infixo's tested-system documentation
reports percentage biases: https://github.com/Infixo/Civ6-Real-Strategy/wiki/PseudoYields.
Under that model, ignoring other active leader/strategy biases, default 3.0 with
+25 means 3.75, and +50 means 4.5: a 20% increase over the previous candidate's
contribution, not twice the effective weight. These calculated equivalents are
not a direct native readback of the complete AI scoring formula.

The inspected RH revision changes the base to 90 in `core/Main/LAI_Main.sql:9`
(30 times vanilla before other biases), adds era/leader percentage preferences,
and separately sets `UnitPriorityBoosts / UNIT_BUILDER` to 900 in
`core/Ops/Ops.sql:47`. The shipped major-civ `UnitPriorityBoosts` list uses the
`Units` system. CSC had no explicit Builder unit priority adjustment in v3.
These values belong to different systems and must not be compared as 50 vs 90
on one scale or translated into unit counts.

Infixo also distinguishes improvement demand/contracts from how quickly the AI
produces a contracted Builder. A unit-priority boost alone is not proof of more
improvements or greater Builder demand. The next Builder-focused experiment
should distinguish those two levers and record actual Builder creation,
training/purchasing and surviving charges, alongside improvement actions. The
completed trial did not instrument Builder production; its improvement density
cannot identify whether production, allocation or action choice is the bottleneck.
No production tuning or new game was launched during this clarification.

## RH-aligned Builder experiment (v4)

Authorized on 17 October: match RH's improvement base (90) and Builder unit
priority (900), remove CSC's own +50% preference, retain bonus/river/sales
placement guidance unchanged. RH itself stays disabled. This does not import
RH's other leader/era biases, unit grants or Builder movement/charge changes.
The global base also affects minor civilizations, matching RH's scope; the
unit-priority list targets major civilizations.

The new matched seed-1 run targets turn 250. Evidence belongs to
`Desktop/Codex/csc-ai-rh-builders-20261017/`.
`run_builder_job.py` runs `builder_tuning_trial.py` and then the four-way offline
comparison. The unchanged baseline observer remains primary; supplemental
`builder_observer.lua` records Builder additions, training, purchase events when
the native subtype is available, remaining charges and operation starts.
Additions may include captures/grants; operation starts are not completed work.
Historical trials did not instrument Builder production.

The Python controller polls locally every 20 seconds and archives frozen
observations at 50-turn intervals, retaining the primary 25-turn censuses.
It writes `live-status.json`, archives failures, and restores and freshly verifies
preferences after completion. `job-status.json` distinguishes native-run failure
from a later offline-analysis failure. Assistant follow-ups should read those
files about every 15 minutes, without opening a competing debug connection.
A single seed and the combined two-setting change cannot isolate causal effects.

The [v4 Builder test](../research/mods/csc-ai-rh-builders-20261017.md) was
interrupted short of250: log232, latest autosave named234, primary observations
archived through200. The user reports Shadow died; the incomplete run is excluded from
completed turn-250 comparisons. Evidence/autosaves were preserved and the heartbeat
removed. No automatic rerun. The [matched turn-200 analysis](../research/mods/csc-ai-rh-builders-20261017-turn200.md) uses the preserved progress: improvement density5.22 to7.76/city versus v3, Baker Base improvement8/15 to12/16, Services unchanged7Growth/2Housing. One-seed combined treatment; production counts lack a historical control.


## Improvement reduction and Tailor metric clarification —17 October2026

After the latest pass4 map reached250, Henno requested reducing the improvement
base from90 to20. Builder unit priority stays900; native placement12/4/10 is
unchanged. Source and installed CSC SQL updated; no new native game requested.
The existing dedicated90/900 trial preflight is historical and requires updating
before reuse with this setup. Archived trial files remain historical evidence.

Tailor5/9 is conditional placement choice, not final material coverage: of27
recorded first placements,9 had an owned native plot-legal Base option in the
candidate cache;5 chose Base and4 did not. The other18 lacked such an option.
The endpoint had25 completed Tailors, only2 still with owned visible Base.
All five original Base choices completed, but three lost their supporting
resource to later construction: Cologne Sheep became a Holy Site; Kerma Flax
a Wonder; El-Kurru Flax a Theater Square. Meroe and Sai Gon retained Flax.
This separates access at placement from preserving that access afterward.


## Corrected setting choice —17 October2026

Henno clarified the preceding request: restore improvement valuation90 and lower
Builder production priority900 to100. This supersedes the temporary20/900 setup.
Source and installed SQL now use90/100, with native adjacency12/4/10 unchanged.
Current offline SQL validation checks90/100; no new game was launched.

Installed stock Base/DLC XML/SQL contains no UNIT_BUILDER entry in
UnitPriorityBoosts; Base Gameplay/Data/Leaders.xml:246 supplies only the Settler
boost1. Thus the stock Builder has no additional boost in this list (effectively
0 extra), not a known zero overall production score. AiFavoredItems.Value defaults
to0 in Schema/01_GameplaySchema.sql:99–111. The engine's underlying priority is
separate and is not established by these files.100 is an experimental boost,
not100 times production. Historical90/900 trial controllers need their native
preflight updated before reuse; retain their archived results as historical.


## RH improvement-choice lessons —17 October2026

Read-only inspected reference remains RH commit91584816e88f458461ae132e30d6860adba97eed.
RH separates broad demand (improvement pseudo90), Builder production priority900,
and improvement-type preferences. Ops/Ops.sql:128–166 registers a major-civ
Improvements system list: Mine40, Pasture9, Quarry-8, Fort-75; oil improvements500.
Trait_Leader.sql:1338 favours Farm90 for its growth trait. These are source
examples, not demonstrated percentage effects or guarantees for CSC. Type-wide
preferences cannot express exactly a mapped resource beside a particular Quarter.

LAI_Main2.sql:644 also changes DefaultCityBuilds/CITY_EVENT_IMPROVEMENT Value0=>1;
meaning/effect requires native testing (not an established task throughput fix).
LAI_Main3.sql:437–463 grants AI Builders+2 starting movement in friendly territory,
an actual gameplay advantage, not a smarter planning algorithm. RH_Yields3.sql
attaches virtual food-extension city-yield modifiers to Farms/Fishing Boats;
RH_Yields5.sql similarly attaches end-of-tech modifiers to Mines/etc. These
illustrate valuation shims, not proof conditional CSC supply bonuses will be
forecast by the Builder planner. Prior CSC conditional-material approach remains
inconclusive. The apparent harvest ban in RH_MC_Mode.sql is for custom monopoly
units, not blanket protection of ordinary Builder resources.

No explicit general improved-resource protection rule was located in the searched
RH sources. Improving before later district placement may help, but is unproven.
In latest game's3lost Tailor sources: Sheep1233 got Pasture46 and was pillaged at
checkpoint125 before HolySite135; Flax2451 got Farm60 and was intact at100 before
Wonder113; Flax3056 got Farm122 but was already unimproved225 before Tailor236 /
Theater240. Thus earlier improvement does not establish state at removal. One
intact Farm was still replaced later; these three cases cannot estimate relative
loss risk for improved versus unimproved deposits.

Candidate next experiment: current90/100, a separate Improvements-system bias
for material-relevant Farms/Pastures (resource mappings verified), and measure
material improvement delay/repair, idle/moving units, and improvement state just
before resource loss. All Farms/Pastures would be affected, not only materials.
Test exact tile valuation separately; do not promise preservation from generic
improvement preferences. No gameplay changes made during this review.

Primary general AI reference: https://github.com/Infixo/Civ6-Real-Strategy/wiki/PseudoYields
(distinguishes improvement contracts from Builder production timing).


## Installed RH v5.097 review —18 October2026

The old4.34-based RH90/900 descriptions above are historical. Installed5.097 uses base improvement30, no globalBuilder900 in RH_Ops.sql, +1friendlyBuildermovement, and Lua city-work scoring/scripted purchasing. Current CSC remains90/100; no change during research. See [full review and staged proposals](../research/mods/csc-rh-v5097-ai-review-20261018.md). Henno rejects biasing among improvement types: aim for resource improvement/repair generally, with exact CSC-support relevance where feasible. Native private-yield preservation and marginal improvement value are distinct hypotheses.


## Quarter-owned resource modifier trial — 18 October 2026

Authorized natural autoplay endpoint:250 (updated from the initial200 request).
Builder priority100=>50; general improvement valuation stays90. Existing native
bonus12/river4/sales10 guidance remains. New district-owned modifiers target exact
live Base/Specialty mappings for Bakers/Tailors, including active compatibility
resources:40 private placement yield while present and another80 when improved.
No real yield conversion or per-improvement-type preference is added.

RH v5.097 Supporting_Systems/RH_Pantheons.sql:133–155 is the checked native
example for plot-yield modifiers and improved-resource conditions. CSC's code is
independently authored. It uses standard EFFECT_ADJUST_PLOT_YIELD, the owning
player's plots, an exact resource-type requirement, owner-relative distance1,
resource visibility and an AI owner gate. The native improved-resource-class
predicate supplies the extra layer. Actual scope and pillage behavior must pass
a disposable native fixture (40/120/40 and0 for unrelated supplies); the original
starting save is then reloaded and its initial census verified identical.

Output: Desktop/Codex/csc-ai-quarter-resources-20261018. New controller and
watchdog: project/tools/ai_baseline/quarter_resource_trial.py and
quarter_resource_job.py. Primary observer unchanged;25-turn snapshots,50-turn
Builder and live-signal checks. Same Online/Prince/Standard seed830102/940104,
resource pass4; RH/TAR disabled. Native smoke verifies effects, not AI forecasting.
Compare with previous resource4 run at200 and250. Source pins prevent unnoticed
edits while running. A final named-save warning is separate from snapshot validity;
autosaves are archived. Original mod flags and auto-start restored on exit.

The improvement-owned version is a possible subsequent experiment if this fails;
it must not be substituted automatically. Follow-up schedule is15min, quiet during
healthy progress, notify on final result/failure. No repeated model polling.


## Improvement-owned signal and dynamic Service research —19 October2026

Authorized next single natural game, target250, same map830102/game940104, Online/Prince/Small Continents/vanilla Standard/material pass4. Builder50/improvement90 and native12/4/10 remain fixed. Quarter-owned40 presence stays; marginal80 now attaches through ImprovementModifiers to each valid improvement/resource/industry combination, filtered to the mapped resource, visible to its AI owner, and a same-owner matching Quarter at distance1. One marginal80 per industry/resource even beside multiple matching Quarters; presence40 still stacks per Quarter. The improvement bonus may apply while the neighboring district is under construction; research readiness requires a completed, unpillaged Quarter.

Six independently authored Lua-gated native strategies use RH's Call Lua Function/GameEvents pattern, Favored1/Value0 Civics/Technologies lists. Base materials enable stage2/3 research; both classes at the SAME Quarter enable stage4. Owned, visible unimproved materials count as potential supplies. Targets include the Service civic and prerequisite producer-building techs/civics through that stage (Wheel/Construction/Guilds/Humanism as applicable). No customer-building research, forced research selection/progress, free units/improvements, improvement-type bias or real-yield grant. Readiness turns off after unlocks finish or qualifying materials/Quarter disappear. The new script is registered in canonical action JSON/project and installed manifest.

SQL schema/replay checks pass21presence modifiers/21improvement attachments and6research plans. Native fixture gates must pass before autoplay:40/120/pillaged40, improved wrong/distant negative controls, Base-only vs both, resource-loss and research-completion deactivation, native engine invocation of the callback, then identical pristine reload. Endpoint code exports frozen250 primary/Builder/research observations before evaluating actual autoplay stopping turn; an overshot named save records its actual turn.

Evidence root Desktop/Codex/csc-ai-improvement-research-20261019. Initial controller was interrupted by the assistant after wrongly treating relaunch PID10808 exit as a failed game launch; Steam had spawned DX11 PID8104, which finished the same map. No natural autoplay had begun. Original preferences142 are preserved. trial-v1b recovers that same initial world, with exact source/installed archives before continuation. Actual rendererDX11 differs from previous Quarter-resource DX12 and is a comparison limit. Initial trial/archive remain intact; controller-only v1b recovery/negative-control refinements do not change gameplay. No assertion that native forecast has improved follows from fixture application.


19October follow-up COMPLETE at exact250, all11censuses/no gap/nativegates/pins/prefs passed. [Result](../research/mods/csc-ai-improvement-research-20261019.md) Atcommon225 BBaseimproved9/17→16/19,T2/4→3/3; Growth6→13,Housing4→5; salescoverage48/70→34/56. Final17/20BBase,5/5TBase improved; Services15Growth/5Housing/1Faith,25Builders49cities72charges. NoNavalTraditionby225 despiteactivegates; Germany/Vietnamacquireonly226–250,Nubianot. All5BaseTailorslackadjLighthouse,so0stage2Services. Improvedcandidatepromising,researchnotearlyconvincing,salesweaker,war/rendererconfounds.38source/122installed archivehashesverified; namedfinalsaveunconfirmed but248–250autosaveshashed. Finalprobe2mismatchesexplainedby80stackcap+pillagedQuarter; earliernoncontemporaneousauditretained. MonitorDELETEDconfirmed,nofurthergames.
