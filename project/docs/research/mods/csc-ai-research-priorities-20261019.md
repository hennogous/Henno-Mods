# CSC research priorities — Medieval-start controlled check,19October2026

**Outcome: no observed research-choice response. Closed at the requested three-attempt limit; no natural250-turn game launched.**

The one completed controlled comparison produced identical civic-choice and completion histories with guidance OFF and ON. This is a narrow negative result, not proof that native civic priorities never influence the AI. Two of the three attempts were our fixture/setup failures; only the third yielded a valid on/off comparison.

## What RH establishes

Installed read-only reference: `Steam/steamapps/workshop/content/289070/3792072489`.

- RH uses `Strategies`, `Call Lua Function`, `Strategy_Priorities` and native `Civics`/`Technologies` lists, with boolean callbacks registered through `GameEvents`.
- `core/Strategies/Advanced_Thinking/DiplomaticVictorySupportingStrategy/RH_DiploVictorySupport.sql` gives Mysticism and Drama/Poetry120, Theology180. `MicroStrategies/RH_Military.sql` also uses explicit civic weights150–500. Other RH lists use Favored1/Value0; our previous zero is not inherently invalid.
- The earlier completed CSC game's native `AI_Victories.csv` already showed Service4 Following for Nubia at19 and Germany at43. Callback wiring was not established as broken.

## Actual test

Variant `medieval-rh-research180-support120-v1c`: primary Service civic180, producer prerequisite research120, Favored1. Material gates, Quarter presence40, improvement-owned80, improvement valuation90, Builder50 and native placement12/4/10 unchanged. Tested SQL SHA256 `3c95255dc8bbdd85252148efd7e75baaadc60095d9535dd6f187eb702244b63e`.

Native Medieval start, Online/Prince/Small Continents, vanilla Standard, CSC only; map830102/game940104 and the original roster. Medieval starts at game turn71. The same pristine native save was reloaded for both arms (SHA256 `aa30b7496e9f979b298792d83a3026c2c27983e69d060508ea8644645b6aede4`).

Each of five AI players received a disposable coastal city with a completed Tailors’ Quarter, adjacent improved Flax, Textile Workshop and adjacent Harbor/Lighthouse. Native building existence and exact district locations were asserted. Naval Tradition was missing and its Defensive Tactics prerequisite known. The fixture called SetProgressingCivic(-1) identically without choosing the target; the20October audit below shows clearing was not verified. OFF returned false from research readiness; ON enabled only actual material readiness for plan4. These synthetic fixture states are not natural-game placement or Service performance data.

Twelve AI rounds per arm produced60 player-turn observations each, covering71–82; simulation stopped at83. Native database/replay preflight passed. Native log differences confirm Service4 entered Following for all five AI players at71 in ON. The control's observation gates remained false.

| Research metric | OFF | ON |
|---|---:|---:|
| Players observed |5|5|
| Selected Naval Tradition |1/5|1/5|
| Completed Naval Tradition |1/5|1/5|
| First completion turn |79|79|
| Changed player civic-choice/completion histories |—|0/5|

First choices in both arms: Germany Naval Tradition; Nubia Civil Service; Phoenicia, Vietnam and Greece Feudalism. After removing the deliberately different gate field, the complete recorded histories are identical.

Thus the strategy was consumed and followed, but180/120 did not change the observed research choices. This does not establish whether the relevant native preference value changed an internal civic score, nor rule out effects in other states or longer horizons. Do not interpret this as a successful calibration or launch a longer game under that claim.

## Attempt ledger and cleanup

1. `mechanism-01`: generic map readiness expected turn1; Medieval actually starts71. Stopped without AI autoplay; retained the same world.
2. `mechanism-01b`: fixture used WorldBuilder’s building-call signature on CityBuildQueue. Building assertion failed before AI autoplay. Preserved evidence and original save.
3. `mechanism-01c`: corrected two-argument CityBuildQueue call plus exact-location assertions; completed both controlled arms. No response, so stopped at the cap.

The full250 test was conditional on establishing the research mechanism. It was not launched, and no new natural-game key metrics are available. The prior completed250 game remains the latest natural baseline. The five additional games remain deferred.

Original142 mod preferences and auto-startfalse were restored and verified. Experimental180/120 values were reverted in source and installed SQL to the previous completed candidate's Favored1/Value0. Restored SQL SHA256 `d4f565afda2cdec4c8a6b25303b0f54bbd2bffcc094084048397cff7936330a1`; offline native-schema/replay validation returned no changed tables. Other AI settings were retained. Follow-up `csc-medieval-research-test` deleted, confirmed by the app.

Exact test archives contain41 repository files and122 installed gameplay files; every archived hash verified. Controller scripts in the live tools directory are experiment-specific; use the full archived package, including its180/120 validator/source, for any explicitly authorized reproduction. No further checks or runs are scheduled.

## Evidence

Desktop root: `C:/Users/Shadow/Desktop/Codex/csc-ai-research-priorities-20261019`.

- `mechanism-01c/mechanism-results.json`, `choices-off.json`, `choices-on.json`
- `mechanism-01c/native-logs-off/` and `native-logs-on/`, with ON appended native transitions isolated in `post-run-audit.json`
- `mechanism-01c/source-version/`, `native-database-validation.json`, `preferences-restored.json`
- Root `attempts.json`, `post-run-audit.json`, `result.json`, `cleanup-validation.json`, `heartbeat.json`

## Follow-up: fixed civic preferences,19October

The user proposed fixed incentives and another RH comparison. RH Main/RH_LAI_Main4.sql254–280 registers MajorFavorCivics directly on TRAIT_LEADER_MAJOR_CIV with System=Civics. Most civic rows are Favored1/Value0; DivineRight and several others use100. This is a distinct attachment path from CSC's strategy-linked lists with no LeaderType. Native CSC database rows for plan4 were correctly registered and linked, and the native strategy entered Following; no obvious SQL registration defect was identified. That does not establish that the Civic AI consumed dynamically added preferences or refreshed a research plan.

Correction to interpretation:180/120 was an attempted use of RH's nonzero values, not an established quantitative increase in civic valuation. Infixo's primary AI Systems notes (https://github.com/Infixo/Civ6-Real-Strategy/wiki/Systems) explicitly distinguish subsystem handling of table fields; do not extrapolate percentage semantics from Yields to Civics. No proof that Civics ignores Value either.

Recommended next control: fixed NavalTradition Favored1/Value0, attached to TRAIT_LEADER_MAJOR_CIV from fresh native game initialization, with CSC dynamic Strategy_Priorities disconnected. Only one target for calibration; after demonstrating a choice response, extend to all six Service civics. Compare fresh OFF/ON starts, retaining equal seed/era/fixture state. An existing save may retain native definitions or AI planning state, so use fresh initialization to remove that uncertainty; caching remains a hypothesis rather than a demonstrated cause.

Prepared two TEST-ONLY SQL proposals under Desktop/Codex/csc-ai-research-priorities-20261019/fixed-control-proposal/: single-civic-control.sql and all-service-civics.sql. Both passed native-schema application, exact target existence checks and identical replay. They disconnect only CSC dynamic research preference links and define one fixed trait-scoped list. Nothing was applied to source/installed/live game and no additional game or schedule was started. The previous experiment remains closed at its cap. SQL validity is not behavioral validation.


## Astra independent audit —20October2026

The user requested an independent gpt-6-astra review. This was read-only; no game, fixture, SQL or new schedule was created. Parent independently confirmed the two key archived observations.

1. The fixture calls SetProgressingCivic(-1) but does not assert an empty civic afterward. Extreme ON commands/0017-fixed-choice-fixture.txt immediately prints nonempty14/16/15/15/15, matching the preceding selections. This could be an ignored invalid value or immediate native reselection; no planner reset or fresh decision was verified. Earlier wording that the civic was successfully cleared is superseded.
2. Fixed OFF/ON remove Strategy_Priorities links but both native DBs retain CSC_AI_SERVICE_4_Civics/SystemCivics/noLeader-orAgenda and its NavalTradition Favored1/Value0 row. Parent checked the archived native SQLite directly. Whether unowned/unlinked lists are inert or otherwise consumed is unknown. OFF contamination is a hypothesis, not an established engine rule; zero links alone does not demonstrate that the research consumer receives zero preference.

The observed results remain valid narrow negative evidence: fresh fixed treatment rows were loaded before initial choices, and later real civic switches also matched. Vietnam changed to CivilService76 and Guilds81, Phoenicia/Greece to CivilService78, Nubia to Feudalism80 in fixed/extreme controls. No observed behavioral change does not establish nonconsumption or universal failure. Following proves strategy activation, not civic-list merging or score application. Favored is boolean; Value's integer schema does not define its Civics semantics, so10000 was not an established quantitative dose.

RH has both custom defense and stock Naval strategy precedents. There is no code evidence requiring his entire package or proving stock strategies uniquely effective. Proposed next diagnostic, NOT launched: clean three-arm sham/stockSTRATEGY_NAVAL/customCSC comparison; remove all CSC research items/list registrations from every disposable arm before adding one identical isolated Favored1Value0 target list to neither/stock/custom. Hold strategy activation and unrelated priorities constant. Verify eligibility and observe a natural civic completion and subsequent selection, with activation established before that boundary; do not rely on clearing current research. Add a nonresearch diagnostic through the same tested route only where measurable score telemetry is demonstrated; this would calibrate route activation/merging, not prove civic preference consumption. Success is a target-selection response against sham; differing stock/custom response would support an attachment-path distinction. Any positive control's score availability/effect must be validated before it is called working.

Source references: research_choice_fixture.lua49–50; fixed_research_control.sql3; CSC_AI.sql223 onward. RH core/Strategies/Advanced_Thinking/Strategies/RH_Additional_Strat.sql17,81,111,143–148 and RH_Additional_Naval2.sql59 onward. Preserve all prior archives/hashes/observations.
