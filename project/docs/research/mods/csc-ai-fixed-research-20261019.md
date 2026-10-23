# Fixed Naval Tradition preference — completed19October2026

**The repaired controller completed both ON and OFF arms. The fixed preference produced no observed change in civic choices in this controlled12-round fixture.**

| Metric | OFF | ON |
|---|---:|---:|
| AI players |5|5|
| Player-turn observations analyzed |60|60|
| Selected Naval Tradition |1/5|1/5|
| Completed Naval Tradition |1/5|1/5|
| First completion |78|78|

The complete recorded civic-choice and completion histories for turns71–82 were identical. Germany selected Naval Tradition and completed it at78; Nubia first chose Civil Service; Phoenicia, Vietnam and Greece first chose Feudalism. The latter four did not complete Naval Tradition in the observation window. This result is limited to one seed and a short synthetic opportunity fixture, not proof that fixed civic preferences are universally ineffective.

## Exact treatment and controls

Code version `fixed-naval-favored1-value0-v3-read-retries-on-first`, source tools `fixed_research_trial.py`, `fixed_research_control.sql`, `tuner_read_retry.py`. ON ran first, then OFF, each from a fresh native Medieval start. No historical saved definitions or previously played worlds were reused.

Both arms disconnected all CSC dynamic research Strategy_Priorities. ON added exactly one AiFavoredItems row: `CSC_AI_FIXED_SERVICE_CIVICS / CIVIC_NAVAL_TRADITION / Favored1 / Value0`. Its Civics list was directly attached to TRAIT_LEADER_MAJOR_CIV, following RH Main4's fixed-list route. OFF contained the same list with no item. Native checks proved zero dynamic links, correct fixed rows and identical source+overlay replay. Initial worlds and initial censuses matched exactly. AiFavoredItems was the only changed native table, and a multiset comparison verified exactly this one added row with no removed rows.

Map830102/game940104, original six-leader roster, Online/Prince/Small Continents/vanillaStandard, CSC only. Medieval begins at71. Five AI players received identical disposable Tailors' Quarter/improvedFlax/TextileWorkshop/adjacentHarbor-Lighthouse fixtures. Naval Tradition was available but unowned. The fixture called SetProgressingCivic(-1) identically without choosing the target; clearing was not verified (see20October audit below). Improvement90, Builder50, Quarter resource40/improvement80 and native placement12/4/10 retained. No fixture grant was retained in a natural game.

Native autoplay ran13rounds to actual turn84 in both arms. Comparison uses exactly60 complete player-turn observations: five players at every turn71–82. Raw histories include65rows per arm; the extra turn was excluded identically. Synthetic Quarters/Services are not reported as natural AI performance. No250-turn game or all-six-civic extension was run.

## Controller repair and verification

Read-only calls collect replies for at least3seconds and retry empty/closed/missing-state/incomplete replies up to6attempts within120seconds with bounded backoff. Real Lua errors stop immediately. Hosting, fixture creation, mod changes and autoplay commands are sent once, with longer acknowledgment collection; ambiguous mutations are not blindly resent.

Choice exports use request-specific markers and row counts to reject stale/truncated messages. Incomplete or regressed histories cannot overwrite saved data. History is also written to a native Game property from the observer so autosaves can retain it. No research is granted by the observer.

Fault-injection checks passed for empty/EOF recovery, persistent-failure bounds, no mutation resends, immediate Lua-error handling, truncated-history recovery, unrelated-response rejection and endpoint-independent60-row coverage. The completed native run recorded no further transient read retries and no scoped Lua runtime errors. It proves the controller completed this test; actual timeout recovery was exercised with injected failures, rather than claimed from nonexistent native failures.

Earlier attempts remain preserved: v1 aborted on its strict83 endpoint assertion before exporting OFF data; v2 aborted on one empty one-second FireTuner poll, preserving40OFFrows71–78 and autosaves77–79. Neither reached ON. Those failures were harness failures, not behavioral evidence. The user explicitly reopened the task and authorized v3 repair/completion.

## Archives and cleanup

Each arm has44repository files and122installed gameplay files archived with all hashes verified. Both60-row windows, native database/replay gates and per-arm preference restoration passed. Original142mod preferences/autostartfalse and exact installed SQL restored; source SQL unchanged at SHA256 `d4f565afda2cdec4c8a6b25303b0f54bbd2bffcc094084048397cff7936330a1`. The fixed preference is no longer installed. Latest native autosaves are preserved in endpoint-autosaves with hashes in the audit. Follow-up csc-fixed-civic-control deleted, confirmed by the app. No further runs scheduled.

Evidence root: `C:/Users/Shadow/Desktop/Codex/csc-ai-fixed-research-20261019/retry-02`.

- `comparison.json`, `result.json`, `post-run-audit.json`, `paired-preflight.json`
- `on/` and `off/`: choices.json, choices-raw.json, observation-validation.json, native-gameplay.sqlite, native-database-validation.json, source-version/, native-logs/, preferences-restored.json, complete.json
- Root installed-restored.json, endpoint-autosaves/, heartbeat.json; parent retry-02.launch.json/stdout.log/stderr.log

This control removes Lua activation as a necessary ingredient, yet still shows no behavioral response here. It does not establish whether the Civic AI consumes/merges this fixed list or how much the preference changes an internal score. No unvalidated weight increase or broader AI change was deployed.

## Visible ON demonstration

The completed extension's [key-stat comparison](csc-ai-fixed-research-20261019-comparison.md) finds1/5Naval adopters (Germany),16active Service-source flags versus21in the preceding natural game, and no Tailor Services from unseeded Quarters. The one Tailor Production and three Tailor Faith flags all come from original fixture Quarters; these were subsequently activated through gameplay, not directly granted. Medieval start and retained fixtures prevent a causal comparison with the Ancient-start natural runs. The short matched OFF/ON control remains the cleaner fixed-preference result and showed no difference.

**Completed at exactly turn250. All3,404tiles were revealed and currently visible to viewer0, and Civ was left open for inspection.**

Henno requested another ON arm to watch actual simulation, then requested the entire map revealed. `project/tools/ai_baseline/fixed_research_visible.py` prepares the same fresh Medieval ON setup and fixture, validates the loaded preference, reveals every plot to viewer0 and waits for a human readiness acknowledgement. Native autoplay advances one round at a time with viewing pauses; camera begins at Germany's starting Settler. Unit/city position censuses and optional native movement events provide evidence beyond research logs. No units are ordered to move by the observer.

Evidence is separate at `C:/Users/Shadow/Desktop/Codex/csc-ai-fixed-research-visible-20261019`. This is a viewing demonstration, not another matched ON/OFF result: viewer0 receives full map knowledge and viewing configuration differs. Native source and installed files are archived before play. The controller leaves the game open at the endpoint; restoration status is recorded explicitly.

Native reveal check confirmed 3,404/3,404 tiles both revealed and currently visible. The original142mod preferences and autostartfalse were restored through the live UI Modding API without unloading the current game. Henno confirmed Civ foregrounded, then requested continuous autoplay with no viewing pauses. The paced worker was stopped alone (Civ retained), and `fixed_research_visible_continue.py` took exclusive control of the same live world. The reveal generated natural-wonder cinematics; their queued processing locks are cleared through the shipped popup handler. That initial controller handoff involved no fresh map, repeated fixture or save reload; subsequent bounded same-save recovery is documented below.

The viewing session then stalled at71 with autoplay active, zero completed AI turns and zero recorded movement. Normal pause and automation pause were false; UI reported no busy GameCore, and all four logged natural-wonder locks had matching unlocks. Henno reported the map without a popup and noted he may have stopped autoplay while dismissing reveal cinematics. Separate stop/start calls, normal Observer and the original No Player mode did not advance it. A normal forced End Turn UI action also failed to release it. These are viewing/control failures, not AI performance observations.

One bounded recovery preserves and reloads `CSC visible ON recovery turn71 20261019.Civ6Save` (761,927bytes) from the normal Single saves directory. `fixed_research_visible_reload.py` and the exact save are archived under `same-save-reload/`. It verifies the existing fixture and ON preference, reattaches only observation hooks and runs continuous autoplay. No new map or repeated fixture grants. Earlier controller source versions remain in `continuous-controller/`, `observer-controller/` and `user-restart-controller/`. If the same-save recovery fails, stop further recovery attempts and report the failure explicitly.

That reload succeeded and native play resumed, including343recorded unit movements by the first turn77 poll. The cause of the earlier stall remains uncertain. Research history contains70unique player-turn rows72–85; turn71 has no observations. The short-report validator expected71–82 and rejected that missing first round, so no complete short-control result is claimed for this viewing run. This was an observation-window failure after real simulation, not a game crash.

Henno then explicitly requested continued autoplay and a full-map reveal again at250. The same native game continued from86 toward250. `fixed_research_visible_250.py` monitors without artificial pauses, requests a native stop at250, then reveals/verifies every plot and archives a native save and endpoint census while leaving Civ open. Current output is `extended-250b/`; the preceding `extended-250/` monitor failed only a cross-context assertion before attaching and did not stop or restart the game. The corrected monitor was confirmed progressing at153 before completing. Original142mod preferences/autostartfalse and installed SQL/source restoration remain verified. The sparse15-minute follow-up verified the endpoint and was deleted, confirmed by the app. No additional games or deferred experiment series are scheduled.

Endpoint verification: native stop/reveal and endpoint census all report250, with no turn-boundary overshoot. The census covers6major civilizations and39cities with no observer errors. Research has890unique observations: all five AI players at every completed turn72–249; turn71 remains explicitly absent and250was stopped before completing a full research round. Loaded-native database retains the fixed ON NavalTradition Favored1/Value0 row. This viewing extension remains separate from controlled-effect estimates.

Both the native named save and its archived copy match SHA256 `b9ae6c272cf527711d8bcf58b77322486a46aa01d1f2c446a8e15b436cf936c6`. Save: `CSC visible fixed ON turn250 20261019.Civ6Save`. Source and installed SQL remain identical at the restoredd4f565 hash,142mod flags/autostartfalse verified. Controller26152 exited; CivDX12 process8492 remained open at follow-up. Evidence: `extended-250b/map-revealed.json`, `endpoint-state.json`, `research-choices.json`, `endpoint-save.json`, `loaded-native-gameplay.sqlite`, `post-run-audit.json`; follow-up `csc-visible-game-to-250` deleted.


## Astra independent audit —20October2026

The user requested an independent gpt-6-astra review. This was read-only; no game, fixture, SQL or new schedule was created. Parent independently confirmed the two key archived observations.

1. The fixture calls SetProgressingCivic(-1) but does not assert an empty civic afterward. Extreme ON commands/0017-fixed-choice-fixture.txt immediately prints nonempty14/16/15/15/15, matching the preceding selections. This could be an ignored invalid value or immediate native reselection; no planner reset or fresh decision was verified. Earlier wording that the civic was successfully cleared is superseded.
2. Fixed OFF/ON remove Strategy_Priorities links but both native DBs retain CSC_AI_SERVICE_4_Civics/SystemCivics/noLeader-orAgenda and its NavalTradition Favored1/Value0 row. Parent checked the archived native SQLite directly. Whether unowned/unlinked lists are inert or otherwise consumed is unknown. OFF contamination is a hypothesis, not an established engine rule; zero links alone does not demonstrate that the research consumer receives zero preference.

The observed results remain valid narrow negative evidence: fresh fixed treatment rows were loaded before initial choices, and later real civic switches also matched. Vietnam changed to CivilService76 and Guilds81, Phoenicia/Greece to CivilService78, Nubia to Feudalism80 in fixed/extreme controls. No observed behavioral change does not establish nonconsumption or universal failure. Following proves strategy activation, not civic-list merging or score application. Favored is boolean; Value's integer schema does not define its Civics semantics, so10000 was not an established quantitative dose.

RH has both custom defense and stock Naval strategy precedents. There is no code evidence requiring his entire package or proving stock strategies uniquely effective. Proposed next diagnostic, NOT launched: clean three-arm sham/stockSTRATEGY_NAVAL/customCSC comparison; remove all CSC research items/list registrations from every disposable arm before adding one identical isolated Favored1Value0 target list to neither/stock/custom. Hold strategy activation and unrelated priorities constant. Verify eligibility and observe a natural civic completion and subsequent selection, with activation established before that boundary; do not rely on clearing current research. Add a nonresearch diagnostic through the same tested route only where measurable score telemetry is demonstrated; this would calibrate route activation/merging, not prove civic preference consumption. Success is a target-selection response against sham; differing stock/custom response would support an attachment-path distinction. Any positive control's score availability/effect must be validated before it is called working.

Source references: research_choice_fixture.lua49–50; fixed_research_control.sql3; CSC_AI.sql223 onward. RH core/Strategies/Advanced_Thinking/Strategies/RH_Additional_Strat.sql17,81,111,143–148 and RH_Additional_Naval2.sql59 onward. Preserve all prior archives/hashes/observations.


## 20 October correction: fixed preference did change logged civic valuation
A retrospective audit of retry-02 AI_GovtPolicies Civic rows finds NavalTraditioninitialscores OFF88.4/85.2/90.6/102.6/85.2 -> ON132.6/127.8/135.8/154.0/127.8 (fiveAI, about+50%, CSVprecision). Thus the fixed genericmajortrait preference reached nativevaluation even though these shortwindow choices/completions wereunchanged. Do not use the old identicalchoice result as evidence of no valuationeffect. The later cleanstrategy-onlyscore null is distinct and remainsvalid. See csc-civic-unlock-experiments-20261020.md for controlled ownershipcontrasts. Originalgenerateddata/reports preserved.
