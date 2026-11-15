# Calibrated Continents250 — 15 November 2026

User requested a new test game after native valuation/calibration qualification.
Launch approved in scope. MainCSC sole policy, passive observation only.

Root Desktop/Codex/csc-ai-calibrated-continents-20261115; frozen01; output
continents250-01. SmallContinentsOnline250Prince; map21851115/game32051115;
AI1–5/observer0; CL/R2/Suk. CSC de174092; CE branch2d200ef, DLL1be0545b…
Detached scheduled task CSC-AI-Calibrated-Continents-20261115; initial host15944,
worker10844. Check detached-worker-status.json and live-status.json for current
state. Worker logs stdout to worker-console.txt. Shared controller owns all
launch/save/exit/restore; no desktop/CUA. Do not mutate pinned source tools.

Started19:23UTC; next scheduled check around19:40–19:43UTC. Maintain standing
15-minute monitoring and complete analysis after250. Do not end at launch.
No new goal/PR/subagent. Docs protocol csc-ai-calibrated-continents-20261115.md.
Qualification docs/protocol committed/pushed1d8d3831; maincode de174092, CE2d200ef
and skill e387d5b already pushed. Preserve unrelated WIP; memory/MEMORY.md has
shared dirty sections so stage only our prefixes using index blob from HEAD.

19:41 check: original stops100 on explicitcheckpoint SaveGame acknowledged but
file neverappears60s; no hook faults, exit0/prefsrestored,23GBfree. Censuses25/50/
75/100 archived fromsourceLua.log. Verified50saveSHA6fc4f96676f6059fe933beab2c7b07ec04f4636f0a1d5b1fe89cb519c8af747f.
Continuation preparedunchanged and launched19:46 via taskCSC-AI-Calibrated-Resume50-20261115.
Outputcontinents250-resume50-01, statusresume50-worker-status.json, console
resume50-worker-console.txt. Finaltrajectory usesoriginal<=50 +continuation>50;
abandoned51–100diagnostic only. No tuningchanges.

19:56 check: resumed50passes30structure rows and saves100, then observer0dies108.
Sharedcontrollerstops/closes0/restores. Partialworldnot250. Originalthrough100
15Q11B4T allBase/+3+,7+4,5both;42/42exactnativebids,3materiallossevents. Resume
27/27exact but separate divergedpostloadworld. No mixof overlapping histories.
Newfreshreplacement02 launched19:57 (approx), seeds21951115/32151115, samefrozen01.
TaskCSC-AI-Calibrated-Continents02-20261115, game02-worker-status.json,
game02-worker-console.txt; continents250-02. Nextcheck~20:12UTC. No gameplay/
observerprotection edits. Analysis-only planning_segments now acceptsverified50/
100/150/200 with exactsaveprefix;13tests pass; committed/pushed0c45a89a.

Replacement02 completes250 at21:00UTC (hostwrap21:01). All10censuses verified
by offline finish(); mainpolicy/runtime/planningfaults0;20nativehooks frozen,
29312records/0faults/0buffered. Sessioncloses0/prefsrestored. Extraeconomy
preflight production>0assert fails validcity0, so noresult.json/finalexplicit
checkpoint250. Fixguard>=0 withcomments;13preflight/observerchecks PASS. No rerun.
Natural250autosave archived final-autosave/source-250.Civ6Save, SHA9ce30d40…
sourceprovenance receipt; verified200 checkpoint remains. No activegame/task.

23foundations13B10T, allBase/+3+,10+4,5both.63/63exactnativebest;23/23priornative
choicejoins. At25022complete/21workingBase/19completedmappedcustomers/20working
Stage2producers/8Storekeeperproperties/2Sacristans. Nativeaudit2–249 confirms
793chain-turns7sources,4over100; property8at250outofcumulativewindow. Dock0,
all10TailorslackHarbor. 2nativeTailorsfootprintpurchases25/28→found37/67.
69paidtiles5546Gold69matchingdebits/laterowners.12materiallosses10pillages/
1ownership/1Cattle237atB2673whichretainsalternativeBase. No districtovermaterial
inlossrows. SeveralServiceresumptions but102turnlapse; repairlatencyopen.
Next2.1Harbor/customerlayouts,1.1/1.2bothmaterials,repair; don'traisebidsagain.
AI-C192, report csc-ai-calibrated-continents-20261115.md/json;analysis02.jsonDesktop.

Henno requestedfocusedartifactretention. Assetdedup24.4GiB, then32oldOct/earlyNov
AIexperimentfolderspurged18.254GiBnet,63.616GiBfree. Baselines/currentNov10–15/
CE/REAtoolingsourcesretained. See session_disk_cleanup_20261115.md. Need scoped
commit/push finaldocs+diagnosticfix; preserveunrelatedworkspacechanges.
