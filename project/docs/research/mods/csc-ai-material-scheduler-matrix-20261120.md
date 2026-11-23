# Builder scheduler benchmark interrupted by the Steam update

The shared controller was set to run each of three preselected Small Online
maps with CSC gameplay and the same City Lights and resource mods. The
variants were stock AI with CSC guidance disabled, integrated CSC guidance,
and integrated guidance with the finishing-only Builder scheduler. All three
used the same CE binary. The scheduler arm added just one Lua switch. The
untuned arm omitted CSC's native SQL connector action and Lua publisher.

| Map | Map seed | Game seed | Observation |
| --- | ---: | ---: | --- |
| Fractal | 28111120 | 38111120 | All three variants reached the turn-225 census |
| Pangaea | 27111120 | 37111120 | Startup stopped on the updated game before autoplay |
| Continents | 18111120 | 29111120 | Queued behind Pangaea |

Fractal's initial terrain and resource signature, leader starts, starting
units, and loaded binaries matched. The stock arm reached turn 250. In both
tuned arms, the original observer was eliminated after the verified turn-240
boundary. Use turn 225 for the shared endpoint and turns 2–224 for the
Storekeeper effect observations.

## Fractal outcome

| Measure | Stock AI | CSC guidance | CSC guidance with scheduler |
| --- | ---: | ---: | ---: |
| Bakers placed | 13 | 12 | 12 |
| Tailors placed | 12 | 4 | 4 |
| Bakers with a working Mill | 11 | 10 | 10 |
| Tailors with a working Textile Workshop | 9 | 4 | 4 |
| Working owned supplier plots | 3 | 14 | 14 |
| New supplier improvements observed | 2 | 20 | 20 |
| Supplier repairs observed | 0 | 2 | 2 |
| Mature buyers supplied within 15 turns | — | 11/12 | 11/12 |
| Distinct Storekeeper chains with an active native effect | 1 | 5 | 5 |
| Cumulative active Storekeeper turns | 29 | 559 | 559 |
| Dockmaster properties active at the census | 0 | 0 | 0 |
| Worker finishing offers | 0 | 0 | 0 |
| Native scheduler updates | 0 | 0 | 0 |

The finishing rule did not submit a case on this map. Its enabled and disabled
arms had the same counts and effect durations. The known positive Kish replay
still supplies the evidence for what happens when a case meets the rule.

The stock observer's first startup failed its tuning-only preflight. A retry
ran the full game, but its measurement context lacked an initialised adjacency
catalogue. The report reconstructs stock physical material counts from the raw
plot records and the independently exported gameplay tags. Stock buyer-window
timing and placement adjacency require a replay. The control preflight now
initialises the read-only catalogue in that context without starting policy.

## Interruption and retained evidence

Steam upgraded build 26407122 to 26595377 at 00:34 local on 20 November.
Both the DX11 executable and stock XP2 GameCore changed. Pangaea's
turn-one check found that the prior CE supplier-exclusion API was absent.
The next attempt stopped at the executable hash check, before opening a game.
The failed native session closed cleanly and restored the previous mod setup.

The comparison, sources, logs, and checkpoints are in
`Desktop/Codex/csc-ai-problem3-20261118/scheduler-matrix-20261119`.
Open `fractal-partial-comparison.json` for role-level supplier counts,
working producer and customer buildings, Service properties, economic
snapshots, and timing. Resume the three-arm comparison on one verified game
build so a Steam update cannot be mistaken for a tuning effect.
