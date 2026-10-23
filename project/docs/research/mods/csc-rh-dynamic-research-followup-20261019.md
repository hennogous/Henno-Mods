# RH dynamic research preferences: exact wiring and next diagnostics

Henno deferred material placement and requested RH's actual dynamic tech/civic preference code. Existing accepted tuning remains unchanged. No game, fixture, SQL overlay or new schedule was started for this investigation.

Read-only source: installed RH5.097 at `C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/3792072489`. These files are registered in its manifest; some advanced-thinking actions are conditional on RH's multiplayer-compatibility option. Checking code registration does not establish live efficacy on the CSC test host.

## Complete example across two source files

`core/Strategies/Advanced_Thinking/Strategies/RH_Additional_Strat.sql` registers RH_STRATEGY_DEFENSE as KIND_VICTORY_STRATEGY, defines NumConditionsNeeded1, disqualifies non-majors, and uses Call Lua Function / ActiveStrategyDefense / threshold70. Its RHDefenseTechs and RHDefenseCivics lists have Systems Technologies and Civics, respectively, and both appear in Strategy_Priorities for that strategy.

The favored items are Masonry, Castles, Siege Tactics; Defensive Tactics, Nationalism, Mobilization. All six use Favored1/Value0. Other linked lists change military operations, yields, buildings and pseudo-yields as part of the same strategy; isolate the research lists when testing them rather than treating the whole defense package as a single research signal.

`core/Strategies/Advanced_Thinking/Core/RH_Setup_Functions.lua:3445–3460` implements ActiveStrategyDefense(playerID, threshold). It reads live war/opponent military power, returns false outside war, and otherwise activates when ownPower*100 < combinedOpponentPower*threshold. It registers the callback through GameEvents.ActiveStrategyDefense.Add. The threshold is an argument to this particular callback. This routine does not edit AiFavoredItems every turn or choose research directly.

Directly relevant Naval example: `Strategies/RH_Additional_Naval2.sql:23–27` replaces stock STRATEGY_NAVAL's conditions with Call Lua Function / ActiveStrategyNaval / threshold2. RHNavalCivics is registered as System Civics and attached to STRATEGY_NAVAL; its target rows include Foreign Trade and Naval Tradition, both Favored1/Value0. `Core/RH_Setup_Functions.lua:3790–3797` refreshes geography classification and returns whether ActiveNaval equals the requested classification. This is a second independent example of dynamic civic-list activation.

Other magnitudes exist: `DiplomaticVictorySupportingStrategy/RH_DiploVictorySupport.sql:52–54` uses Mysticim120, DramaPoetry120, Theology180, all Favored1, under its Lua-gated strategy. Its callback gates non-human DIPLO strategy players without a Temple and stops after its world conditions. Numeric Value semantics must not be assumed to be percentage priority or compared across systems.

For technologies, `Strategies/RH_Early_Explorer_Push.sql:42–73` enables RH_MICRO_EARLY_NAVAL_PUSH via ActiveStrategyEarlyNavalPush; RHEarlyNavalPushTechs/System Technologies contains Sailing Favored1/Value0. The Lua callback in `MicroStrategies/RH_MicroStrategies.lua:404–481` has additional coastal, naval-force, era, trait and Immortal-or-higher gates. Our Prince setup would not activate that RH micro-strategy unmodified. Do not mistake that gate for a failed research preference.

## What matches CSC already

CSC uses the same Types → Strategies → StrategyConditions/CallLuaFunction → GameEvents callback → Strategy_Priorities → AiLists/System → AiFavoredItems structure. CSC's one callback accepts a plan ID through ThresholdValue, whereas RH often gives each strategy a dedicated callback. Native records already establish CSC's callback receives plan4, returns the readiness condition, and the strategy enters Following. Matching RH's dedicated-callback/threshold0 shape is a useful simplification, not an identified fix.

The completed short native OFF/ON dynamic test already used180/120 and showed identical choices; the fixed startup test also showed identical choices. Do not repeat those as if untried or infer that raising Value alone will work.

## Tests to localize the missing behavior

1. Use one dedicated, always-true callback with threshold0 and one research target, then an always-false sibling control. Remove Quarter scans, material conditions, caches and competing CSC service plans from that disposable treatment. Confirm native callback/Following before the next research decision. This isolates list consumption from readiness logic, although the latter was already validated.
2. Compare research-list attachment through an existing stock strategy, such as STRATEGY_NAVAL, against a newly registered CSC strategy. Keep the same favored row, callback result, start and other strategy lists. This tests whether there is an unexposed distinction in how research priorities are merged from strategies.
3. Include positive controls: a familiar civic target with a known vanilla leader preference as well as Naval Tradition; a technology target whose scoring can be inspected; and a nonresearch favored item using the same strategy activation route. No claim that RH's preference examples are working controls until they demonstrably move a score or choice on this host.
4. Inspect actual scores where available. Archived AI_Research.csv exists and records individual technology scores, status and turns, but the inspected files contain Tech records, not NavalTradition/civic scores. Thus compare technology scores OFF/ON even if the winning tech stays unchanged. For civics, capture actual selected civics at completed-player-turn boundaries and repeat a small fixed set of starting states; do not invent unavailable civic-score telemetry.
5. Verify timing: the list/strategy must be active before a fresh research decision. Do not repeatedly override research choice to manufacture a response. Preserve exact native DB rows, logs, eligibility and start-world parity for each arm. Changing saved native modifier definitions by editing disk SQL is not a valid A/B; use an unchanged native fixture with a callback toggle or separate fresh native starts where definitions differ.

A strategy containing both a Unit/Building positive control and a research preference can reveal whether activation influences other consumers while research ignores its list. If positive controls and stock-strategy paths still fail for research, then a native engine/version limitation becomes more plausible. Source similarity alone cannot establish that RH's research preferences succeed. Direct selection remains a separate fallback, not the current next step.


## Astra independent audit —20October2026

The user requested an independent gpt-6-astra review. This was read-only; no game, fixture, SQL or new schedule was created. Parent independently confirmed the two key archived observations.

1. The fixture calls SetProgressingCivic(-1) but does not assert an empty civic afterward. Extreme ON commands/0017-fixed-choice-fixture.txt immediately prints nonempty14/16/15/15/15, matching the preceding selections. This could be an ignored invalid value or immediate native reselection; no planner reset or fresh decision was verified. Earlier wording that the civic was successfully cleared is superseded.
2. Fixed OFF/ON remove Strategy_Priorities links but both native DBs retain CSC_AI_SERVICE_4_Civics/SystemCivics/noLeader-orAgenda and its NavalTradition Favored1/Value0 row. Parent checked the archived native SQLite directly. Whether unowned/unlinked lists are inert or otherwise consumed is unknown. OFF contamination is a hypothesis, not an established engine rule; zero links alone does not demonstrate that the research consumer receives zero preference.

The observed results remain valid narrow negative evidence: fresh fixed treatment rows were loaded before initial choices, and later real civic switches also matched. Vietnam changed to CivilService76 and Guilds81, Phoenicia/Greece to CivilService78, Nubia to Feudalism80 in fixed/extreme controls. No observed behavioral change does not establish nonconsumption or universal failure. Following proves strategy activation, not civic-list merging or score application. Favored is boolean; Value's integer schema does not define its Civics semantics, so10000 was not an established quantitative dose.

RH has both custom defense and stock Naval strategy precedents. There is no code evidence requiring his entire package or proving stock strategies uniquely effective. Proposed next diagnostic, NOT launched: clean three-arm sham/stockSTRATEGY_NAVAL/customCSC comparison; remove all CSC research items/list registrations from every disposable arm before adding one identical isolated Favored1Value0 target list to neither/stock/custom. Hold strategy activation and unrelated priorities constant. Verify eligibility and observe a natural civic completion and subsequent selection, with activation established before that boundary; do not rely on clearing current research. Add a nonresearch diagnostic through the same tested route only where measurable score telemetry is demonstrated; this would calibrate route activation/merging, not prove civic preference consumption. Success is a target-selection response against sham; differing stock/custom response would support an attachment-path distinction. Any positive control's score availability/effect must be validated before it is called working.

Source references: research_choice_fixture.lua49–50; fixed_research_control.sql3; CSC_AI.sql223 onward. RH core/Strategies/Advanced_Thinking/Strategies/RH_Additional_Strat.sql17,81,111,143–148 and RH_Additional_Naval2.sql59 onward. Preserve all prior archives/hashes/observations.
