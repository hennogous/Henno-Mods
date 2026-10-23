# Extreme fixed civic preference — completed19October2026

**A Naval Tradition preference with Favored1/Value10000 produced no observed change in civic choices in the matched short test.** Both native games completed, and independent archive/database/observation/restoration checks passed. The completed evidence is in `C:/Users/Shadow/Desktop/Codex/csc-ai-fixed-extreme-20261019/retry-02`.

| Measurement | OFF: no preference | ON: Value10000 | Previous ON: Value0 |
|---|---:|---:|---:|
| AI players selecting Naval Tradition |1/5|1/5|1/5|
| AI players completing Naval Tradition |1/5|1/5|1/5|
| Germany completion turn |78|78|78|

All60 player-turn civic-choice/completion rows were identical between the new OFF and ON arms. They were also identical to the previous Value0 ON history. Germany initially chose Naval Tradition; Nubia chose Civil Service; Phoenicia, Vietnam and Greece chose Feudalism. Only Germany completed Naval Tradition in the observed window.

## Treatment and design

ON adds exactly one native AiFavoredItems row: `CSC_AI_FIXED_SERVICE_CIVICS / CIVIC_NAVAL_TRADITION / Favored1 / Value10000`. The list is registered in AiListTypes and AiLists, attached directly to TRAIT_LEADER_MAJOR_CIV with System Civics. OFF has the same registered list with no item. Both arms remove all CSC service Strategy_Priorities links, eliminating dynamic strategy activation as a necessary part of this control. No target research was selected or granted by the observer.

Each arm starts a fresh native Medieval game at71, Online/Prince/Small Continents/vanilla Standard, CSC only, map830102/game940104 and the same six-leader roster. Five AI players receive identical disposable Tailors' Quarter/improvedFlax/TextileWorkshop/Harbor/Lighthouse opportunity fixtures. Naval Tradition is unowned and its prerequisite is present; the fixture calls SetProgressingCivic(-1) identically; the20October audit below shows it did not establish an empty civic or reset. Other tuning remains improvement90, Builder50, resourcepresence40/improvement80, native adjacency12/4/10 and material resourcepass4.

Each game ran13 native autoplay rounds to84. Analysis uses exactly five AI players at every completed turn71–82 (60rows/arm), excluding the extra round identically. This is a synthetic research-choice test, not natural Quarter placement or250-turn Service performance. Actual renderer DX12, normal Steam launch.

## Verification and provenance

Code version: `fixed-naval-favored1-value10000-v1-matched-short`; controller `project/tools/ai_baseline/fixed_research_extreme_trial.py`, preserving the previous Value0 controller. Exact source versions were archived before each arm:44repository files and122installed gameplay files per arm, all hashes verified.

Native gates and independent `post-run-audit.json` confirm:

- Correct target row and zero dynamic research links in each arm; source+overlay replay leaves each native database unchanged.
- Initial worlds and initial censuses identical between OFF/ON. Both also match the previous Value0 control's initial world/census.
- AiFavoredItems is the sole changed native table; its exact row multiset differs by the single Value10000 row, with no removed rows.
- Both exact60-row windows complete, unique and retained separately from raw observations; no scoped Gameplay database errors.
- Original142mod preferences/autostartfalse restored in each arm. Exact installed SQL restored; source unchanged at SHA256 `d4f565afda2cdec4c8a6b25303b0f54bbd2bffcc094084048397cff7936330a1`.

Worker26308 exited. Follow-up `csc-extreme-civic-preference-test` deleted, confirmed by the app. No additional games or deferred experiment series scheduled; no high-value tuning deployed.

## Interpretation

The deliberately extreme numeric Value did not change choices in this starting state. Further increasing Value is not supported by this result. We have not established whether the Civics consumer ignores this numeric field, whether this custom list is consumed, or whether other decision logic dominates. Source similarity with RH and a successfully loaded row do not prove internal score application. One seed and a short fixture do not establish universal engine behavior or natural Service uptake.

A useful next diagnostic would compare an existing, applicable stock civic list with our custom list, with an independently demonstrated positive control. Inspect changes in scores where the engine exposes them (technology score logs exist; civic score telemetry has not been found). This is a proposed follow-up, not an authorized or launched extra test.

## Startup history and correction

The parent output records a pre-menu timeout with no native commands or test turns, installed overlay restored and preferences untouched. Henno explicitly requested restart. Retry-01 used a normal Steam DX12 restart, but the waiting controller still could not obtain MainMenu. The actual4318 socket was held by FireTuner2.exe; querying secondary4319 returned no usable state list.

Henno requested killing FireTuner. Closing that GUI immediately exposed MainMenu on4318. Retry-02 then ran both fresh native test games in that SAME restarted Civ session. No additional game restart was needed. The observed connection conflict establishes the retry-01 blocker; the original DX11 failure may share the cause but its socket owner was not recorded. A FiraxisBugReporter process alone was misleading and does not establish a game crash; earlier uncertainty is preserved in the archived evidence rather than converted into a crash claim.

## Evidence

`comparison.json`, `comparison-to-value0.json`, `report.md`, `post-run-audit.json`, `paired-preflight.json`, `installed-restored.json`, `test-plan.json`, `heartbeat.json`; each arm includes `choices.json`, `choices-raw.json`, `observation-validation.json`, `native-gameplay.sqlite`, `native-database-validation.json`, `source-version/`, `native-logs/`, `preferences-restored.json` and `complete.json`. Earlier startup outputs remain separate and are excluded from behavioral comparisons.


## Astra independent audit —20October2026

The user requested an independent gpt-6-astra review. This was read-only; no game, fixture, SQL or new schedule was created. Parent independently confirmed the two key archived observations.

1. The fixture calls SetProgressingCivic(-1) but does not assert an empty civic afterward. Extreme ON commands/0017-fixed-choice-fixture.txt immediately prints nonempty14/16/15/15/15, matching the preceding selections. This could be an ignored invalid value or immediate native reselection; no planner reset or fresh decision was verified. Earlier wording that the civic was successfully cleared is superseded.
2. Fixed OFF/ON remove Strategy_Priorities links but both native DBs retain CSC_AI_SERVICE_4_Civics/SystemCivics/noLeader-orAgenda and its NavalTradition Favored1/Value0 row. Parent checked the archived native SQLite directly. Whether unowned/unlinked lists are inert or otherwise consumed is unknown. OFF contamination is a hypothesis, not an established engine rule; zero links alone does not demonstrate that the research consumer receives zero preference.

The observed results remain valid narrow negative evidence: fresh fixed treatment rows were loaded before initial choices, and later real civic switches also matched. Vietnam changed to CivilService76 and Guilds81, Phoenicia/Greece to CivilService78, Nubia to Feudalism80 in fixed/extreme controls. No observed behavioral change does not establish nonconsumption or universal failure. Following proves strategy activation, not civic-list merging or score application. Favored is boolean; Value's integer schema does not define its Civics semantics, so10000 was not an established quantitative dose.

RH has both custom defense and stock Naval strategy precedents. There is no code evidence requiring his entire package or proving stock strategies uniquely effective. Proposed next diagnostic, NOT launched: clean three-arm sham/stockSTRATEGY_NAVAL/customCSC comparison; remove all CSC research items/list registrations from every disposable arm before adding one identical isolated Favored1Value0 target list to neither/stock/custom. Hold strategy activation and unrelated priorities constant. Verify eligibility and observe a natural civic completion and subsequent selection, with activation established before that boundary; do not rely on clearing current research. Add a nonresearch diagnostic through the same tested route only where measurable score telemetry is demonstrated; this would calibrate route activation/merging, not prove civic preference consumption. Success is a target-selection response against sham; differing stock/custom response would support an attachment-path distinction. Any positive control's score availability/effect must be validated before it is called working.

Source references: research_choice_fixture.lua49–50; fixed_research_control.sql3; CSC_AI.sql223 onward. RH core/Strategies/Advanced_Thinking/Strategies/RH_Additional_Strat.sql17,81,111,143–148 and RH_Additional_Naval2.sql59 onward. Preserve all prior archives/hashes/observations.
