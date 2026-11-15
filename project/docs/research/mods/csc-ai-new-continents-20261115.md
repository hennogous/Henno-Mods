# New Continents world for the coherent planner

Henno requests a fresh Continents seed so the current planner encounters new
geography. This runs the qualified main-CSC candidate unchanged. The active
roadmap scope is Problems 1 and 2, especially 1.5 acquisition and 1.6 follow-through.

## Predeclared setup

- Continents, Small, Prince, Online; ordinary start through turn 250.
- Map seed **20851115**; game seed **31051115**, selected before hosting.
- Same City Lights, Resourceful 2 and Sukritact's Resources stack as the preceding
  tests. Stock AI, with CSC's integrated policy; no RHAI5 or external test bids.
- Reuse the immutable `csc-ai-coherence-20261115/frozen02` package containing
  candidate `9f450233`. All 11 overlaid files match the current source hashes.
- XP2 SHA `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`;
  CE SHA `400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f`.
  WildW develop is unchanged at `2986a746` when checked before this launch.

The shared controller owns hosting, bounded autoplay, popup recovery, checkpoints
and preference restoration. A one-shot current-user task owns the worker lifetime,
records a heartbeat/exit status, and removes its registration after the worker
returns. It neither retries nor changes the game policy. Agent check-ins are
about every 15 minutes. The pinned sources remain unchanged during the run.

## What to extract

For Bakers and Tailors, count foundations and their actual starting adjacency,
Base and Spec neighbors, improved suppliers and existing customer districts.
Follow native-selected plans through acquisition, retained request values,
construction or expiry. Use the continuity journal to explain support changes.
Retain material-loss, customer-order, building and Service observations, ordinary
district calibration and native savings/payment evidence from the existing
passive observers. No manually prepared chains or economic subsidies are added.

Artifacts: `C:/Users/Shadow/Desktop/Codex/csc-ai-new-continents-20261115/`;
game output: `continents250-01`. Startup preflight, original seats, loaded mods,
code hashes, commands, native receipts, checkpoints and final closure are recorded
there. Results will be added after the run.


Startup passed the deployed-module, native capability, resource-stack and
main-CSC policy preflights. The game advanced beyond turn11 with no Lua errors;
original AI seats1–5 are recorded. Plan journal reads are active. Native and CE
loaded-file hashes match the declared identities. The controller continues250.
