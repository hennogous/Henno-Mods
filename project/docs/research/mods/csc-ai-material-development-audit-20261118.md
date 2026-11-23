# Problem 3: first material-development investigation

18 November 2026. Initial research and matched replay after completing customer
placement 2.1. [Machine-readable census screen](csc-ai-material-development-audit-20261118.json).

**First case: the native scorer accepts the Pasture bid, and Angkor Thom opens
a Mine job even at the current CE bid ceiling.** Both Bakers and Tailors already
receive supplier guidance. The next question is how much late job preference
is justified by the work that becomes possible once the exact supplier is ready.

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

## What the other AI mods contribute

Read-only review of the installed Workshop files. The replay uses stock game
AI with CSC and its recorded CE package.

| Mod | Source pattern | Application to Problem 3 |
|---|---|---|
| AI+ | `behaviortrees.xml` sets Required City to `-1` on both Build Unit nodes in Build City Improvement. | CSC already uses this pattern in `CSC_Q_ALL_AI_Connectors.sql`. An admitted job can recruit production from other eligible cities. The game still performs its own unit selection and queue comparisons. |
| Real Strategy | `base/RealStrategy_Main.sql` has a base improvement pseudo-yield of 4. Peace, military defense and war apply different biases. | Treat the appetite for improvement work and ability to staff a selected job as separate decisions. CSC already has a distinct +10 Builder request-priority default. |
| RHAI5 | `core/Strategies/m01/m03/m07/RH_m023.lua` scores eligible resource work, useful ordinary plots and existing improvements before considering Builder acquisition. | Count valuable work against available capacity. CSC can do this over its much smaller set of mapped jobs, counting a pillaged supplier as unfinished work. |

For 3.3, RHAI5 also provides examples of conditional technology and civic
strategies. Our earlier civic replay confirmed activation of the strategy and
identical research choices in both arms. Qualify a specific missing material
prerequisite at the native research comparison before using that design.
[Earlier mod audit](csc-ai-material-preservation-and-repair-review-20261023.md).
[Research replay](csc-ai-research-priorities-20261019.md).

## Matched Pangaea replay

The original Pangaea run recorded 145 exact Pasture writes of 6,656 Q8 across
the turn 99–249 offer window. A Builder moved through (52,22) on turns 174–178
while Hariharalaya was pursuing a Ski Resort at (53,22). Count that as movement
for the Ski Resort, based on the tree's decoded improvement and reservation.

Both replay arms load the same retained turn-100 save, unmodified packages and
stock setup. Angkor Thom owns the bare Sheep at (52,22). Its Tailors Quarter has
a functioning Textile Workshop. The Pasture is unlocked and native placement
legality is true. Two Khmer Builders have a combined four charges at hex
distances six and nine. A unit census measures nearby charges. The behavior
tree measures eligibility and assignment for a specific job.

The ordinary arm forwards the original 6,656 Q8 (+26 utility). The treatment
raises only the exact city, Sheep plot and Pasture entry to 16,384 Q8 (+64
utility), the tested CE capability's ceiling. The first interval uses the
policy published during save loading. The adjusted publication begins on
turn 101. The receipt for turn 102 is 22,023 → 28,679 Q8 in ordinary and
22,023 → 38,407 Q8 at the ceiling. Zero-turn setup observes the world and
wraps publication in memory. Civ plays both arms through turn 112 and makes
its own construction and Builder decisions.

In both arms the existing Mine tree finds a Builder on turn 100. Angkor Thom
opens a new Mine job on turn 102 at (50,28), with a native job value of 265.
A three-charge Builder is one hex from the Sheep on turn 109 while other
improvement jobs proceed. The Sheep remains bare at the turn-112 boundary.
The first observed barrier for this Pasture is getting an ordinary job slot
and winning admission. Changing empire-wide Builder production or researching
another technology would leave the observed job choice in place.

The comparison audit verified 12 exact receipts per arm, including 11 at the
ceiling, and zero Builder hook faults. Both sessions closed at exit code 0,
restored preferences and preserved the matching source save. The archived
`comparison.json` includes the score changes, turn-109 Builder and digests
for the source and raw evidence. The retained frozen packages matched all
duplicates before 0.76 GiB was removed.

## Follow-through

The subsequent [implementation and Fractal replay](csc-ai-material-job-followthrough-20261118.md)
prices the exact native job from the shared economic model and verifies working
Tailors Base supply. It also follows the separate Farm case through Builder
recruitment.

Measure the native margin at an open improvement admission for a chain whose
first Base or Specialty improvement delivers a substantial immediate benefit.
Use the gameplay-defined transaction data to price the contribution. If the
existing score hook reaches an economically justified win, keep that simpler
route. If the timing or native gate defeats a sound bid, prototype an exact
offer at ordinary job admission and retain the game's existing reservation,
recruitment and build checks. Follow the chosen job through physical work and
its working supply link. For 3.2, count available capacity only when a valuable
admitted job waits. For 3.3, use a separate case with a missing prerequisite.

Previous Bakers evidence already shows both outcomes: Alexandria's Pasture
completed and Storekeeper operated (AI-C111); Melbourne's Farm reservation
could stall because nearby Builders worked elsewhere and its recruitment offer
lost stronger queue comparisons (AI-C113/115/116). This next case tests the
current shared policy on Tailors. No global Builder bonus, new API or additional
economic forecasts are justified before finding that boundary.

Sources include current main CSC `CSC_AI_QuarterPlacement.lua`,
`CSC_AI_DistrictBridge.lua`, the campaign censuses and the
[native finding register](../../civ6-ai/findings.md#ai-c111). The replay is in
`Desktop/Codex/csc-ai-material-development-20261118`. The native-trace check
matched the relevant sections of ordinary admission, location selection and
improvement score storage in Ghidra's reference `324c51e9` to the live XP2
binary `092abfbb`. The previously qualified REA score record is documented
in the [native research log](csc-ai-bakers-natural-research-20261106.md#ce-score-producer-and-execution-limits).
