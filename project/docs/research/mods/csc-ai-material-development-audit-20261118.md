# Problem 3: first material-development investigation

18 November2026. Initial research after completing customer placement2.1.
No new game or tuning change. [Machine-readable census screen](csc-ai-material-development-audit-20261118.json).

**Next, trace why an operating producer fails to obtain its first working Base
supplier.** Both Bakers and Tailors already receive supplier guidance. The useful
question is where that guidance stops producing work, before changing its value.
Astra recommends one short, exact job-to-execution investigation.

## What the integrated policy already does

`CSC_AI_QuarterPlacement.lua` reads material tags and resource/improvement mappings
from loaded gameplay definitions. It checks ownership, visibility, district
occupation, native improvement legality and improvement technology/civic unlocks.
A compatible pillaged improvement remains a repair candidate.

For a completed, healthy Quarter without a working Base supplier:

- A working Stage2 producer **or** customer supports a26-utility job preference.
- Having both supports56 utility, capped by the available CE capability.
- One unfinished job per material class/chain is offered: repair first, then
  lowest eligible plot index. Shared plots take the maximum rather than a sum.
- Specialty work uses the same plumbing after its Stage4 buyer operates.

These are Q8 preferences:26×256 or56×256. `MaterialDeductions` associates the
supplier tile with its own purchase city, which can differ from the Quarter's
city. `CSC_AI_DistrictBridge.lua` stages each mapped improvement through
`CE_AIBuilderProtectionBid`. The engine chooses the exact job and assigns or
recruits a Builder. An allow-only protection entry is separate from a scored bid.
The ordinary unowned-supplier acquisition proposal has a separate26-utility cap.

Unlock checks and research-time forecasts already exist. A chain-driven switch
in the AI's technology selection remains the separate3.3 task.

## Current full-game cases

Screen the three treatment turn250 censuses for completed, unpillaged Quarters
with a working Stage2 producer, at least one recorded Base deposit and no working
Base improvement. Seven match:

| Map | Bakers | Tailors | Also has working Stage2 customer |
|---|---:|---:|---:|
|Continents|1|0|0|
|Pangaea|1|1|0|
|Fractal|3|1|3|

Here, working means compatible and unpillaged. The screen identifies missing
suppliers; job legality, technology and Builder availability need the next trace.

**First case: Pangaea treatment, player1/city65536, Tailors1753, Sheep1680.**
The Workshop works and the Sheep lacks a working supplier in every25-turn census
from100 through250. Two neighboring Holy Sites have Stage3 customer buildings;
there is no recorded working Stage2 customer. This is a persistent producer-only
case, directly exercising the existing26-point policy. Fractal's Tailors853 with
Sheep928 is a second case: its producer is damaged at175 and working at200–250,
while the supplier remains non-working.

## One bounded next experiment

Use the retained Pangaea100 checkpoint and the shared controller for at most
12 turns. First inspect Sheep1680's current improvement, unlocks, build legality,
purchase city and reachable Builders. If executable, join the publication to
native job comparison, reservation, worker assignment or Builder recruitment,
then physical improvement and material exchange. Identify the first actual loss
and its competing job/offer. An occupied planning tree or committed Builder is
an availability result; locked work belongs to3.3.

Previous Bakers evidence already shows both outcomes: Alexandria's Pasture
completed and Storekeeper operated (AI-C111); Melbourne's Farm reservation
could stall because nearby Builders worked elsewhere and its recruitment offer
lost stronger queue comparisons (AI-C113/115/116). This next case tests the
current shared policy on Tailors. No global Builder bonus, new API or additional
economic forecasts are justified before finding that boundary.

Sources: current main-CSC `CSC_AI_QuarterPlacement.lua`,
`CSC_AI_DistrictBridge.lua`, retained campaign censuses and the
[native finding register](../../civ6-ai/findings.md#ai-c111). The open Ghidra
program is the historical324c51e9 XP2 binary; this source/data audit introduces
no addresses or runtime claims for the current092abfbb binary.
