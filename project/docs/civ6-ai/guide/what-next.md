# What we’re investigating

## Current problem 4.1 — unlock the Mill for Boston's Bakers

Boston completed Bakers on our chosen site after one turn-22 score change.
The game began with Craftsmanship locked and Boston's player researched it
normally. The control founded Bakers on a different tile. The chosen Quarter
still has its Base deposit and an adjacent City Center. The next check uses
the completed Quarter save to see which Mill its site can support and whether
the AI unlocks the needed technology. [Matched construction test](../../research/mods/csc-ai-bakers-natural-research-20261106.md).

## Intermediate milestone — one working Bakers Stage 2 chain

The sequence is a completed Quarter with viable Base supply and an adjacent
Granary host (**1**), a working Mill and Granary (**4, 5**), a working Base
improvement and sufficient Builder capacity (**3**), then a functioning
exchange with its supplier retained (**2.2**). Feudalism and Storekeeper
extend the test to a working Service (**6.1**). Existing unlocks and buildings
can satisfy dependencies. Tailors comes next through the same model.

The offline replay has checked synthetic Bakers states, actual gameplay
definitions and a copied Tailors case. Each live decision still needs
evidence that it reached the right native consumer and produced the expected
action. [Stage 2 replay](../topics/csc/site-planner.md#stage-2-decision-replay).

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
