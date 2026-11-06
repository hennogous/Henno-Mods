# What we’re investigating

## Milestone reached — Boston's working Bakers chain

Boston completed Bakers on our chosen site after one turn-22 score change.
The game began with Craftsmanship locked and Boston's player researched it
normally. The control founded Bakers on a different tile. The chosen Quarter
had its Base deposit and an adjacent City Center at completion. A second
matched test lowered the Campus score on the only Base tile. Boston placed
Campus elsewhere and built a Pasture, Granary and Water Mill through its
ordinary plans. We then protected the Pasture from two independent Farm
decisions, one for the Feudalism boost and one from ordinary city planning.
Boston researched Feudalism and had a working Storekeeper at turns 63 and 66.
The Granary produced 2 Food against its base of 1, and the Water Mill produced
1 Production and 1 Gold at both observations. The controller saved the
complete chain on turn 66.
[Construction, supplier protection and actual yields](../../research/mods/csc-ai-bakers-natural-research-20261106.md).

## Intermediate milestone — one working Bakers Stage 2 chain

The sequence is a completed Quarter with viable Base supply and an adjacent
Granary host (**1**), a working Mill and Granary (**4, 5**), a working Base
improvement and sufficient Builder capacity (**3**), then a functioning
exchange with its supplier retained (**2.2**). Feudalism and Storekeeper
extend the test to a working Service (**6.1**). Existing unlocks and buildings
can satisfy dependencies. Tailors comes next through the same model.

The live Boston replay establishes this sequence for one Bakers chain. The
offline planner separately covers actual gameplay definitions and a copied
Tailors case. A reusable policy still needs broader tests of the same native
decisions. [Stage 2 replay](../topics/csc/site-planner.md#stage-2-decision-replay).

## Tools for this milestone

The shared controller and guarded stock score hook support matched live tests.
Dev-CE 0.8.1 is an optional research tool for a specific
extra Lua getter or debugging need. Packaged CE delivery is a separate
qualification on the patched Windows host.
[Dev-CE release](https://github.com/cru121/civ6-dev-ce/releases/tag/v0.8.1-experimental) ·
[CE hotfix notes](../../research/mods/csc-ai-xp2-november-hotfix-20261106.md).

For each problem, we trace the decision in the game files and native code
with REA and Ghidra, then use a focused runtime trace to check what the AI
actually does. The handbook records the mechanism and the limits of the
evidence. [Research workflow](../roadmap.md#reverse-engineering-each-decision).

The [numbered roadmap](../roadmap.md#numbered-problems-to-solve) tracks the
decisions and the [current problem](../roadmap.md#current-milestone-and-active-problem).
