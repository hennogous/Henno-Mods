# What we’re investigating

## Start with one working Bakers chain

We want the AI to choose a useful Quarter site, preserve the adjacent
materials, build a Mill and a connected Granary, and improve the Base supply
with a Builder that can reach it. Then it can value the Storekeeper unlock
when the chain is otherwise ready. Tailors is the next family to exercise
the same model.

The first offline evaluator reads the active gameplay mappings and replays
these decisions from supplied observations. It reports actions and the
material plots that need protection. It distinguishes the last viable deposit
from the last working supplier. We checked the sequence on synthetic Bakers
states, the definitions against the local gameplay database, and the protection
logic on a copied Tailors case.
[How the replay works](../topics/csc/site-planner.md#stage-2-decision-replay).

## Deliver the right value at each decision

CSC values its supply chains. Civ still compares eligible actions and manages
production, treasury and strategy. Start with bounded preferences, calibrated
against a few real alternatives. A strong native investment should still
be able to win. A change in score matters when it reaches the intended choice
and produces a working, durable result.

On the patched stock game, a one-time bid made Delhi choose Bakers and
reserve the target tile. Its Craftsmanship preparation expired and it
switched to a Campus. The next construction test needs an already unlocked
Bakers candidate. Buying an unowned site, altering a production choice,
getting a job assigned, and changing an unlock priority each need their own
evidence. [Live bid test](../../research/mods/csc-ai-hotfix-live-bid-20261106.md).
We’ll address them in the order that closes the first chain, then extend
the approach to later stages, Wonders and the remaining Quarter families.

## Qualify the CE carrier

The pre-hotfix development fork rejects the new Steam GameCore identity.
The updated target candidate builds, and offline CSC work can proceed.
A packaged CE district write still needs a CE base qualified on the patched
Windows host. [November hotfix comparison](../../research/mods/csc-ai-xp2-november-hotfix-20261106.md).

[Roadmap](../roadmap.md) · [Research library](../library.md)
