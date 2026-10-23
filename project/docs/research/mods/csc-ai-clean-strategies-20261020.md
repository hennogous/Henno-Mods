# Clean stock/custom research strategy comparison —20October2026

Status: COMPLETE. All three research arms finished; the independent post-run audit passed. No research response was observed. Original source, installed SQL/Lua and mod preferences were restored. Monitoring automation deleted and deletion confirmed. Evidence root: `C:/Users/Shadow/Desktop/Codex/csc-ai-clean-strategies-20261020`.


## Completed result

| Arm | Naval selected/completed | Germany completed | Analyzed player-turns |
|---|---:|---:|---:|
| Sham, no experimental target list | 1/5 | 78 | 400 |
| List linked to stock Naval strategy | 1/5 | 78 | 400 |
| List linked to custom CSC strategy | 1/5 | 78 | 400 |

All 400 observed civic-history rows were identical between sham and each treatment, comparing current civic, Naval completion and newly completed civics. Germany alone selected Naval Tradition at71 and completed78. The other four never selected or completed it through150. Each AI had 9-15 natural completion-to-next-selection opportunities after activation: Germany13, Nubia10, Phoenicia9, Vietnam15, Greece12 (59 per arm). Both strategies were Following/true from71 for all five players. Thus no delayed response appeared during 80 analyzed Online rounds; stock versus custom attachment did not change the observed outcome on this fixture/seed.

This narrows the timing, residual-list and stock/custom explanations. It does not establish that the engine cannot consume civic preferences: no working positive control was established, and the consumer/semantics remain unresolved. The planned calibration turn72 Culture weights were unavailable, so response is null/unmeasured rather than an asserted measured zero. Exploratory available71/73 matches (8 per treatment) and full CityBuild CSV comparisons showed no difference, without calibrating what that field measures.

`post-run-audit.json` passed all six cases: exact49source/122installed archived hashes per case, matched initial worlds/censuses/fixtures/preferences, zero residual old CSC research rows, correct target rows/activation, exact observation windows, no observer/scoped database errors, and original142mod flags/autostartfalse restored. Stock/custom native tables differ only at Strategy_Priorities. Installed SQL hash d4f565afda2cdec4c8a6b25303b0f54bbd2bffcc094084048397cff7936330a1 and research Lua b3261682a93ab5a9fb0c5cfcfdceaa321c534df62623a3c25c419cfa92ae6be4 match unchanged repository sources.

Worker14316 has exited. Follow-up csc-clean-strategy-research-comparison was deleted with app confirmation. No further games launched or scheduled. Earlier controller recovery below remains part of provenance: full sham research observations were recovered offline without replay; its endpoint primary census is missing and its turn152 native autosave is retained. V1 supplied calibration/sham; v2 supplied stock/custom, with identical native scripts and only save-handling changes.

Henno authorized the clean comparison proposed after Astra's audit, asking enough time for delayed AI response without a250-turn game. Three fresh matched research worlds use sham/no target list, target list linked to stock STRATEGY_NAVAL, and the same list linked to a new CSC strategy. Each analyzes80 Online rounds71–150 after the Medieval start;81native rounds are requested to allow consistent boundary coverage (expected endpoint152). Natural civic completion events and next selected civics are recorded; there is no research reset, forced selection or research grant.

All former CSC service/fixed research lists and favored items are removed in every disposable arm, including their registrations and strategy links. Both test strategies use the same always-active alive-major-AI condition; other stock Naval priorities remain identical. The stock and custom treatments have identical native tables except the one Strategy_Priorities attachment. Sham contains no target list/item, preventing the earlier unlinked-row ambiguity. Native preflight also rejects any other surviving NavalTradition favored item.

A separate short three-world nonresearch calibration compares SystemYields/Culture1000 through sham/stock/custom. Native AI_CityBuild reports Culture weights; matched turn72 weights are compared. This tests a different AI consumer and cannot establish civic preference consumption. No diagnostic yield preference occurs in the subsequent research worlds. Calibration must report no measurable response or unavailable scores honestly, rather than assume a working control.

Settings: map830102/game940104, original six-leader roster/five AI, Online/Prince/Small Continents/vanilla Standard/CSC only, resource pass4. Five identical Tailor/Flax/Workshop/Harbor/Lighthouse opportunity fixtures isolate research uptake; these are not natural placement performance. Quarter40/improvement80/improvement90/Builder50/native12/4/10 remain fixed.

Controller and native overlays are versioned under project/tools/ai_baseline/strategy_research*. Each native run archives exact source and installed SQL/Lua/XML/modinfo hashes BEFORE launch. Native source+overlay replay, old-list absence, exact treatment rows, paired fresh worlds/censuses/fixtures, callback and Following evidence, complete observation windows and original mod-preference restoration gate interpretation. Native saves are archived periodically; intermediate save names reflect approximate request checkpoints, while inactive endpoint turn is verified. Short calibration and80-round research observations remain separate.

Offline native-schema/replay checks passed for all6phase/arm combinations. Framed-export tests reject truncated/wrong-count/wrong-request responses; decision-boundary classification and no-setter fixture checks passed. A first offline preflight lacked SQLite Make_Hash registration; repaired locally before any native launch, retained separately as preflight output. No native test was consumed by that offline setup error.

Initial worker9372 exclusively owns FireTuner. Normal Steam hidden launch requested. No FireTuner GUI or other controller was active. Sparse follow-up will inspect local status only; no competing client while the worker runs. No automatic crash rerun or unrelated multi-game series.


## First sparse check: calibration complete, research/sham setup

All three short calibration native runs completed and restored their original preferences. Worker9372 and DX12Civ14424 verified alive; research/sham reached initial71 at06:16:45local and is preparing its fixture. No competing client or pinned source edits.

Calibration limitation: the preregistered turn72 AI_CityBuild Culture-weight sample had zero matching rows in every arm. Thus calibration-result.json measurable_response=false is NOT an established positive control or a measured turn72 null response. Bounded offline inspection found weights at71 and73 instead. A separately labeled exploratory audit matched8rows per treatment across71/73, with no nonzero Culture-weight differences. Results saved as calibration-exploratory-audit.json; keep distinct from the missing planned sample. This does not prove list nonconsumption; the displayed CityBuild field's relationship to strategy valuation is itself uncalibrated. Research tests continue as authorized with80rounds and natural boundaries. No games rerun or instrument changed.


## Controller save failure and recovery —20October2026,06:37local

V1 research/sham completed all80 analyzed rounds through150 and stopped natively at152. The controller then aborted when its optional checkpoint named save was not confirmed; the mutation itself acknowledged success, but the expected file did not appear. This was a controller archival failure, not a demonstrated Civ crash, stalled game or incomplete80-round simulation.

Independent completed-sham-recovery-audit.json verifies exact400 unique observations71–150 (405raw through151),59 CivicCompleted events inside the analysis window, no observer errors, both strategies Following from71 for allfive,49source/122installed archive hashes and v1 source pins matching before repair. The endpoint native database was independently read from DebugGameplay.sqlite and matched preflight table multisets exactly; its snapshot is preserved. Native autosaves150/151/152 were archived with hashes. No game replay or reload was needed.

Recovered observations/observation-validation/strategy-activation-validation/complete files label this offline recovery. A final primary world census was not exported before the IO abort; it remains explicitly missing. The turn152 native autosave replaces the failed named endpoint save; metadata for the previously confirmed128checkpoint is retained separately. All original installed SQL/researchLua and142mod preferences/autostartfalse had already been restored and verified by the failed worker.

The original controller and trace/status/restoration files are preserved under controller-recovery-v2. New controller clean-strategies-natural80-v2-save-tolerant changes only Python orchestration: optional save failures produce warnings and autosave fallback; mandatory initial save remains required. Fault injection verified one mutation attempt, nonfatal optional failure and fatal initial failure. It also labels missing calibration samples as unavailable. Native SQL, Lua callbacks, observer and fixture scripts are byte-identical to v1; this was independently checked against v1 archived source hashes. Offline native-schema/replay preflight passed again.

V2 worker14316 reuses completed calibration and sham data, starting ONLY the remaining stock/custom research worlds in the same existing DX12 Civ14424. --continue-study validates all reused completion/preflight/observation/activation/preference gates and original-world parity. Exact source versions remain recorded per native case; no old source archive is overwritten. Native gameplay/settings unchanged. Follow-up csc-clean-strategy-research-comparison updated with new worker/logs/recovery provenance and remains active until the authorized comparison finishes.

Additional bounded calibration audit: full AI_CityBuild CSV contents matched sham in both treatments after removing only the repeated header. Thus no construction-contract valuation difference was observed in these short diagnostics either; this remains an exploratory nonresearch null, not an established working control or proof of nonconsumption. Saved in calibration-exploratory-audit.json.
