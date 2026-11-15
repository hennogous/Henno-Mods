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

Started 15 November 2026, 19:23 UTC. Running; completion analysis pending.
