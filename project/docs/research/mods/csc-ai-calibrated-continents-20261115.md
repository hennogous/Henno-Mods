# Calibrated Quarter bids — fresh Continents validation

This run tests the integrated Quarter valuation under ordinary stock AI play.
It follows the native cost/timing and bid calibration qualification in
[the implementation report](csc-ai-native-valuation-20261115.md).
Active roadmap problems: **1.4/1.6/1.8**, observing the remaining placement
capabilities and **2.1/2.2** customer/material outcomes alongside them.

## Protocol selected before results

- Small Continents, Online speed, Prince, through turn 250.
- Map seed **21851115**, game seed **32051115**; five AI players, observer 0.
- City Lights, Resourceful 2 and Sukritact's Resources enabled; stock AI.
- Main CSC AI source **de174092**; experimental CE **2d200ef**.
- Main CSC is the only active AI guidance. Additional observers capture
  decisions and outcomes without injecting policy, unlocks or map edits.
- Frozen packages: `Desktop/Codex/csc-ai-calibrated-continents-20261115/frozen01`.
  The established gameplay package is retained while current AI modules and
  the numerical UI bridge are overlaid; unrelated workspace art/gameplay WIP
  is excluded. Exact package manifests are archived by the controller.
- CE SHA256 `1be0545b94b35adaf582df2d70e827ecdb8014ccf91b59c5cc9f9b72fdc06bfc`.
- Native XP2 SHA256 `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.

The shared controller owns launch, observation, saves, shutdown and preference
restoration. Autonomous checks run every 15 minutes; endpoint censuses are
every 25 turns. The detached scheduled task survives a client interruption.
Runtime-pinned controller and observer files stay unchanged during the game.

## Measurements

Count Bakers/Tailors foundations and their rating at placement, Base/Spec
access and improvements, completed customers, producers, Services and active
chain-turns. Link published bids to native comparisons and foundations. Inspect
ordinary district competition, site purchases/savings, supplier losses and
repair, valuation caps, faults and controller timing. Compare with prior full
runs and the matched short qualification; this fresh seed supplies a new map
challenge rather than a matched treatment/control comparison.

## Run artifacts and status

Root: `C:/Users/Shadow/Desktop/Codex/csc-ai-calibrated-continents-20261115`.
Output: `continents250-01`. Host status: `detached-worker-status.json`;
controller status: `continents250-01/live-status.json`. Task:
`CSC-AI-Calibrated-Continents-20261115`. The machine-readable
`predeclared-plan.json` records the frozen source, seeds and scope.

Started 15 November 2026, 19:23 UTC. The first segment reaches inactive turn100,
but the sole explicit checkpoint request at100 produces no settled native file
within60seconds. All save-permission checks pass and the request is acknowledged;
the cause of the missing file is unresolved. Native observers report zero
faults. The controller closes with native exit0 and restores preferences.
Disk has23GB free. Its verified turn50 checkpoint and recorded censuses25–100
are preserved; the natural turn100 autosave also exists.

Continuation `continents250-resume50-01` loads the verified turn50 checkpoint,
with unchanged frozen packages, through the shared controller. Task:
`CSC-AI-Calibrated-Resume50-20261115`; host status `resume50-worker-status.json`.
The continuation passes its30-row structural equivalence check and writes a
verified100 checkpoint. At108 the original observer civilisation is eliminated;
the shared controller stops rather than activating unbounded AI-only play.
It closes with exit0 and restores preferences. Both segments are partial test
history, not a completed250 run. Their overlapping turns are not added together.

The first segment records15 foundations by100 (11 Bakers/4 Tailors), all with
Base and rating+3+, seven at+4+, five with both material classes. Its42 native
Quarter comparisons all match published bids. It records three material-loss
events to inspect separately. The resumed segment also has exact delivery27/27;
its different post-load history is preserved separately.

## Replacement world

Before observing its results, a replacement Small Continents world is selected:
map **21951115**, game **32151115**, same frozen01 policy and other settings.
The replacement reason is observer elimination. The prior world and its failed
checkpoint remain in the report. Plan `replacement02-plan.json`; output
`continents250-02`; task `CSC-AI-Calibrated-Continents02-20261115`; host status
`game02-worker-status.json`. No gameplay edits or observer protection are added.
The replacement reaches inactive **250**. All ten25-turn censuses verify;
native shutdown exits0 and restores preferences. An extra read-only preflight
then rejects a valid zero-Production city because its guard requires positive
output. The final worker wrapper and explicit250-save step are consequently
absent. Recorded outcomes are complete, and the natural250 autosave is archived
with provenance alongside the verified200 checkpoint. The diagnostic now accepts
zero while rejecting missing/negative output;13 preflight/observation checks
pass. These results require no repeat game.

## Placement and follow-through

| Measure | Bakers | Tailors | Total |
|---|---:|---:|---:|
|Foundations|13|10|23|
|Base adjacent at placement|13|10|23|
|Placement rating+3 or better|13|10|23|
|Placement rating+4 or better|3|7|10|
|Base and Spec at placement|2|3|5|
|Completed at250|12|10|22|
|Completed Quarter with working Base improvement|11|10|21|
|Completed Quarter with both classes improved|2|3|5|
|Completed mapped customer district adjacent|11|8|19|
|Working Base plus completed mapped customer|10|8|18|
|Working Stage2 producer|11|9|20|
|Active Stage2 Service property at250|8|0|8|
|Active Stage3 Service property at250|1|2|3|

Placement ratings include the prospective local Mill's conditional bonus and
existing customers; future customer districts are excluded. They describe site
quality rather than the immediate payout of an unfinished Quarter. No+2 site
is founded despite the permitted+2 floor.

All63 new-Quarter native best comparisons match the published bid/version/write.
All23 foundation identities have a recorded native district choice. Compared
with the preceding different-seed Continents250, foundations rise5→23,
+4-or-better placements1→10, endpoint Storekeepers3→8 and observed Storekeeper
chain-turns370→793. The earlier matched50-turn test separately found4→8
foundations on the same starting world. Keep this calibration while addressing
the remaining spatial/chain gaps. A matched full control is needed for balancing
or economic attribution.

Two selected Tailors footprints are bought and subsequently used: player4 buys
1857 at25 and founds37; player3 buys972 at28 and founds67. This exercises
**1.5/1.6** acquisition and follow-through, including a39-turn delay. All69 tile
payments have matching measured Treasury debits and later ownership confirmation,
spending5546Gold. Category funds still fail332 checks despite sufficient Treasury.

## Services and remaining work

The independent native attachment/growth audit samples every clock2–249 without
internal gaps or ambiguous attribution. Seven sources deliver **793 active
Storekeeper chain-turns**; four exceed100 across three AI players. The250 census
has an eighth active property, outside that cumulative measurement window.

| Player / city ID | Active turns | Active ranges |
|---|---:|---|
|3 /262147|135|93–106;129–249|
|3 /327684|158|92–249|
|3 /458758|53|197–249|
|4 /65536|178|72–249|
|5 /65536|67|67–89;104–119;222–249|
|5 /458756|108|130–136;149–249|
|5 /524294|94|148–197;206–249|

Services resume after22-,14-,102-,12- and8-turn lapses. Player3 Quarter1347 has
a supplier pillaged107 and resumes its Service129; player5 Quarter1970 loses
its working supplier137 and resumes149. Repair latency remains a concrete
follow-up alongside placement.

The12 material-loss events comprise ten pillaged suppliers, one ownership loss
and one removed Cattle deposit at237. The latter is adjacent to Bakers2673,
which began with two Base deposits and retains a working Base supplier at250.
No material-loss row reports a district replacing the deposit. The Cattle-removal
cause remains open; these events should not all be labelled protection failures.

None of the ten Tailors has a Stage2 Harbor customer. Nine have working producers,
eight have a completed mapped customer of another stage, and two operate
Sacristan at250. **2.1** Harbor-aware layouts remain the clearest Dockmaster
bottleneck. **1.1/1.2** material-rich placement also needs attention:5/23 combine
both classes. Target those opportunities and repair delays before increasing
Quarter bids again.

All20 passive native hooks close frozen with29,312 records, zero faults and
no buffered records. There are no recorded Lua runtime or planning faults.
The five AIs finish with53 cities/640 population: total Production2547.4, gross
Gold2269.6, net Gold−161.4 and Food surplus337.3 per turn. Ten economic samples
are retained; the different world prevents attributing these levels to tuning.

[Compact results, per-Quarter facts and economic samples](csc-ai-calibrated-continents-20261115.json).
Current raw records remain in the run directory. Separate disk-cleanup receipts
record asset consolidation and retirement of32 superseded experiment folders;
baselines and current qualification/full-run inputs are retained.
