# Timing a Bakers bid against natural civic research

Problem **1.6** tests whether a later district bid can survive native
preparation and reach construction. In the earlier isolated Delhi replay, the
AI reserved the intended tile, but its Craftsmanship request reached eight of
eight waiting turns and the district plan failed. The new world starts in the
Ancient Era with Craftsmanship locked. No civic, research boost, district or
building is granted. [Earlier bid and expiry](csc-ai-hotfix-live-bid-20261106.md).

## Read-only Online pilot

The shared controller hosted Small Continents at Prince and Online speed,
with the isolated CSC rules package and patched stock Gathering Storm. It used
the fixed Mill study leaders and seeds, with no diagnostic world setup or
instrumented writes. It recorded the original major AIs at turn 1 and each turn
from 5 through 25. Craftsmanship was locked for all five at turn 1.

| Original AI player | First observed researching Craftsmanship | First observed unlocked |
| --- | ---: | ---: |
| 1 | 8 | 14 |
| 2 | 8 | 12 |
| 3 | 9 | 15 |
| 4 | 7 | 11 |
| 5 | 9 | 19 |

The gameplay console exposed civic selection and unlock state. The initial
probe got no usable values there from the UI methods `GetCulturalProgress`
and `GetTurnsToProgressCivic`. The pilot stopped at turn 25 with zero writes,
no saved candidate, and verified restoration. These turn numbers describe the
natural world created for this pilot.

## What the game measures

On the fingerprinted Gathering Storm binary, `GetTurnsToProgressCivic` in
the UI cache binding at RVA `6ad720` forwards to the cached culture object's
indexed `GetTurnsLeft` at `0b3410`. The gameplay binding
`GetTurnsLeftOnCurrentCivic` at `6f0f40` forwards to the live player culture
method at `280770`. That method reads the active civic, calculates the current
culture yield, then passes both to `GetTurnsLeft` at `2806c0`. The latter uses
the civic cost and accumulated progress with the player's carried culture.
This result estimates turns at the current yield. Actual completion can
change with yield, boosts, or a different research selection.

`CultureAi::EstimatedTimeToResearch` at `414b20` reads a separate AI planning
row for the requested civic. It may add time remaining on the active civic
when the active civic matches neither of the planning row's two civic fields.
This is a distinct decision input. A short current-civic ETA establishes a
timing opportunity while the district tree's acceptance and persistence still
need their own runtime evidence.

The Ghidra reference is XP2 SHA `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The loaded stock hotfix is SHA `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`,
with the same code section. [Binary comparison](csc-ai-xp2-november-hotfix-20261106.md).

## Qualified turn-8 checkpoint

The second scout confirmed the UI cache returns numerical research data for
the original AI players. A Lua city iterator error stopped the run when the
first AI began Craftsmanship. The controller restored preferences and exited
normally. The corrected scout used the gameplay getter for turns remaining
and a same-turn UI query for accumulated progress.

On turn 8, player 4 had completed Code of Laws, was researching
Craftsmanship, and still had it locked. Both getters estimated four turns
remaining. The UI reported 7.6875 Culture accumulated toward that civic.
The two surveyed sites in city 65536 had spare district capacity. Both were
owned, revealed, legal by the plot query, adjacent to the City Center, and
adjacent to an owned mapped Bakers Base deposit. Plot 2420 had no feature
and Base plot 2421. Plot 2568 had a feature and Base plot 2642. This verifies
the scout geometry and timing. Native candidate scoring, the Granary's
presence, and material improvement readiness are separate checks.

The shared controller saved one exact inactive turn-8 boundary. The saved
world hash is `95a26a1976400ef0d8232fc3a0d2b857f0cbc277b6e07ff2f66195f7df1310bc`.
It is the single input for the control and diagnostic-bid arms.

## A fresh score while London's district plan was busy

The turn-8 control reloaded the exact save, matched the scout's source facts
and observed one turn. The Bakers cell at plot 2568 had a fresh score of
11,930 Q8 before and after aggregation. Plot 2420 was reserved. London made
no `GetBestDistrict` call in the observed window, so the run made zero writes
and did not open a treatment arm.

The native tree log separates the competing commitments. London's
improvement tree reserved plot 2420 at (52, 32). Its outstanding Holy Site
tree reserved plot 2421 at (53, 32), which was the mapped Base deposit next
to the first Bakers site. Holy Site preparation was still waiting on
Astrology under contract 34. Meanwhile the production log recorded Great
Bath at 11 of 90 Production. The Base reservation establishes a risk to the
proposed supply chain. This control did not observe the deposit being lost.

`CheckForDistrict` at RVA `3e0ee0` requires the city's outstanding district
tree ID to equal −1 before it calls `GetBestDistrict`. It also requires a
configured district tree. London's active Holy Site tree explains why the
fresh Bakers score had no selection opportunity. The queue's Great Bath is
a separate commitment. The next read-only pass searches for the first
qualified selection window in the same naturally advancing world. It can
admit a city whose Craftsmanship has unlocked through normal research.

## Evidence locator

The evidence root is `Desktop/Codex/csc-bakers-natural-20261106`. The first
pilot is `scout-01`. Its `scans/` contain the per-turn records, and
`source-version/` retains the exact executed Lua and Python. Pilot
`scout-result.json` SHA-256 is
`a4b8424ccc55c2478554bc32c5b4246d2c7a52eea9628461f2be39c5eaecdb27`.
The failed candidate scan is `scout-02`. The qualified source is `scout-03`,
whose `scans/08.json` SHA-256 is
`0089de5f3be73a5a530c69139e079265c21786395e854aa54feea781c5250049`.
The first control is `matched-01/control`. It closed normally and restored
preferences and the temporary package. The SHA-256 of `trace-frozen.json`
is `7db19defd41e4961ccaeb59d974e4e1e8321547b9432ddbfdfce997821a82375`.
The London tree records are `AI_Behavior_Trees.csv` lines 836–870 and
923–927. The Great Bath production row is `City_BuildQueue.csv` line 5.
