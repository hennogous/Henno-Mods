# Integrated CSC Stage 2 trial through turn 200

The 8 November 2026 development batch ran three ordinary Small Ancient
Prince games at Online speed, using the main CSC tuning and one local
CE review package. The shared controller handled setup, autoplay,
passive evidence collection, turn-200 saves and preference restoration.
Stock AI made the decisions. No external AI policy, probe mode, Frida,
or RHAI5 was active. [Readable results](../../civ6-ai/topics/csc/site-planner.md#three-normal-start-games-through-turn-200).

## Reproduction and artifacts

The three measured runs used one frozen package set based on CSC commit
`241490c` and CE review commit `c10a076`. The CE DLL SHA-256 was
`687906d9c62c8a9fdb8ea529818e80c96316f645f825f093d836d3734c630646`.
The local evidence root is `Desktop/Codex/csc-ai-integrated-20261108`.
The `batch-v2.json` manifest identifies the frozen packages, map and game
seeds and main CSC AI actions. The `run-v3-continents`,
`run-v3-pangaea` and `run-v3-fractal` folders contain the archived
`Lua.log`, district censuses, saves, load records and clean closure records.

Two setup attempts stopped before autoplay. The first exposed a stale
GameCore package ID. The second exposed an old controller check that rejected
all private yield rules, including the intended customer adjacency.
All three measured games used the same corrected packages and start check.

## Bakers native effect windows

The parser in `project/tools/native_ai/late_placement/storekeeper_runtime.py`
checked all 198 interior sample turns in each archived log. Each group below
is one player, city and Quarter identity. The ranges include both endpoints.

| Map | Map / game seeds | Active windows by chain | Total chain-turns |
| --- | --- | --- | ---: |
| Continents | 18461107 / 29461107 | 108–127 and 130–199, 144–199, 103–199, 192–199, 198–199, 198–199 | 255 |
| Pangaea | 18461108 / 29461108 | 188–199, 81–199, 120–147 | 159 |
| Fractal | 18461109 / 29461109 | 145, 144–199, 143–199, 161–172 and 194–199 | 132 |

On turn 199 the native effect was active on six, two and three chains
respectively. The turn-200 CSC model reported six, three and three active
chains. A lapse followed by resumption occurred in Continents and Fractal.
The windows alone do not identify why a chain stopped or why it resumed.

## Turn-200 census and native activity

| Map | Bakers completed / with working Base | Tailors completed / with working Base | Tailors active property | CE protected selector rows | CE repair admissions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Continents | 18 / 8 | 13 / 2 | 0 | 241 | 0 |
| Pangaea | 17 / 4 | 15 / 1 | 0 | 165 | 1 |
| Fractal | 20 / 5 | 19 / 3 | 0 | 206 | 0 |

There were 200 CSC publications per map with zero reported publication
faults and zero omitted selector masks. The protected row totals can count
the same plot repeatedly. The Tailors result measures the Service property.
This batch lacked both an independent Tailors effect audit and a matched
untuned arm. The earlier same-seed Continents development run recorded
19, 86 and 11 chain-turns through turn 199. Differences between those
development runs cannot be assigned to an individual tuning change.

## Matched baseline with CSC tuning disabled

The same three setups were replayed from fresh normal starts with the same
frozen CSC gameplay and local CE binary. The only two removed manifest
actions were the CSC Lua publisher and the SQL connectors. Those removals
also removed the private customer adjacency and Builder database preferences.
The controller checked map signatures, leaders, starting plots and units
against each v2 arm. The baseline CE score hook reported no policy entries
or changed scores. All three games closed cleanly with verified turn-200
saves. The baseline folders are `baseline-continents`, `baseline-pangaea`
and `baseline-fractal` under the same evidence root.

| Map | Baseline Bakers chains ever active | V2 chains ever active | Baseline chain-turns | V2 chain-turns | Baseline first Service | V2 first Service |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Continents | 1 | 6 | 39 | 255 | 161 | 103 |
| Pangaea | 0 | 3 | 0 | 159 | — | 81 |
| Fractal | 1 | 4 | 55 | 132 | 145 | 143 |
| Total | 2 | 13 | 94 | 546 | | |

The two baseline windows were Continents turns 161–199 and Fractal turns
145–199. Both arms have native Storekeeper samples on turns 2–199, with no
ambiguous attachment attribution. The comparison measures the integrated
policy as a package on these starts. It cannot assign a gain to one hook,
and it does not generalize the size of the gain to every map or prove the
long-run retention milestone.

### Turn-200 Quarter and customer census

The shared controller reopened each of the six verified saves with its
original arm's packages. It read the state at turn 200 without advancing the
game. The original AI majors were the sample. Materials had to be visible,
player-owned, immediately adjacent and outside a district. An improved
material had a compatible and unpillaged improvement. Each row counts
completed Quarters unless otherwise noted. The Stage 2 customer host is a
City Center for Bakers or a Harbor for Tailors, including applicable
replacements. A host without a building can be under construction. A
working customer requires a completed, healthy host and its healthy
building on that plot.

| Metric | Bakers baseline | Bakers v2 | Tailors baseline | Tailors v2 |
| --- | ---: | ---: | ---: | ---: |
| Quarters placed, including unfinished | 57 | 57 | 56 | 49 |
| Quarters completed | 56 | 55 | 56 | 47 |
| Adjacent Base deposit | 15 | 28 | 11 | 12 |
| Adjacent Specialty deposit | 3 | 10 | 4 | 7 |
| Both material classes adjacent | 0 | 7 | 0 | 1 |
| Base improved | 9 | 17 | 5 | 6 |
| Specialty improved | 3 | 8 | 3 | 6 |
| Both classes improved | 0 | 4 | 0 | 0 |
| Adjacent mapped sales district, any stage | 31 | 35 | 18 | 20 |
| Adjacent Stage 2 customer host, any building state | 26 | 34 | 2 | 5 |
| Adjacent Stage 2 host, no matching customer building | 13 | 14 | 1 | 1 |
| Adjacent Stage 2 host with working customer building | 13 | 20 | 1 | 4 |
| Stage 2 Quarter building present | 39 | 43 | 43 | 41 |
| Stage 2 Quarter building absent | 17 | 12 | 13 | 6 |
| Stage 2 Quarter building unpillaged | 37 | 43 | 42 | 41 |
| Stage 3 Quarter building present | 19 | 12 | 19 | 14 |
| Stage 4 Quarter building present | 7 | 3 | 12 | 3 |
| Working Base, producer and customer together | 2 | 12 | 0 | 0 |
| Active Stage 2 source Service property | 2 | 12 | 0 | 0 |
| Active Stage 3 source Service property | 1 | 0 | 0 | 0 |
| Active Stage 4 source Service property | 0 | 0 | 0 | 0 |

Bakers had virtually the same number of completed Quarters, with more
adjacent materials, developed supply and working Stage 2 customers in v2.
On Pangaea, stock AI actually finished more Bakers Quarters, 21 versus 17,
and assembled zero working chains. Tailors' better Lighthouse adjacency
never coincided with working Base and Workshop in a complete Stage 2 chain.
Later-stage Quarter buildings were less common in v2 for both industries.
The single baseline Stage 3 source property is a snapshot observation.
Only Storekeeper has an independent per-turn effect audit in these runs.

### AI economy at turn 200

Each arm had 15 surviving original AI majors across its three games.
Production is the sum of current city Production yields. Net Gold is the
native treasury's gross per-turn income minus maintenance, matching the
stock top panel. Gold reserves are the balance. Population and city Food
surplus describe the size and growth conditions of the endpoint empires.
These are endpoint readings rather than cumulative flows over 200 turns.

| Metric | Baseline total | V2 total | Baseline per AI | V2 per AI |
| --- | ---: | ---: | ---: | ---: |
| Cities | 126 | 121 | 8.4 | 8.1 |
| Population | 1,234 | 1,151 | 82.3 | 76.7 |
| Production per turn | 3,586.1 | 3,308.7 | 239.1 | 220.6 |
| Gross Gold per turn | 4,710.8 | 4,121.4 | 314.1 | 274.8 |
| Gold maintenance per turn | 2,028.0 | 2,158.0 | 135.2 | 143.9 |
| Net Gold per turn | 2,682.8 | 1,963.4 | 178.9 | 130.9 |
| Gold reserves | 6,445.9 | 6,993.6 | 429.7 | 466.2 |
| Food surplus per turn | 741.4 | 573.9 | 49.4 | 38.3 |

The map totals below show baseline → v2. Continents had higher Production
and net Gold in v2. Pangaea contributed most of the Production, population
and Food-surplus deficits. Fractal contributed the largest net Gold
deficit and ended with more citizens in v2. Across all three, average
Production per city was 28.5 → 27.3 and Food surplus per city was
5.9 → 4.7. The endpoint comparison leaves open which decisions account
for the economy differences.

| Map | Cities | Production / turn | Net Gold / turn | Gold reserves | Population | Food surplus / turn |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Continents | 37.0 → 37.0 | 946.8 → 978.3 | 310.1 → 315.9 | 1,064.1 → 3,219.9 | 372.0 → 345.0 | 226.0 → 218.0 |
| Pangaea | 45.0 → 38.0 | 1,443.5 → 1,157.0 | 883.6 → 549.1 | 2,711.4 → 1,645.9 | 428.0 → 351.0 | 272.5 → 132.9 |
| Fractal | 44.0 → 46.0 | 1,195.9 → 1,173.5 | 1,489.1 → 1,098.4 | 2,670.3 → 2,127.8 | 434.0 → 455.0 | 242.9 → 223.0 |

The `endpoint-detail-baseline` and `endpoint-detail-run-v3` folders contain
checkpoint hashes, raw census rows and clean closure records. The
`endpoint-comparison.ndjson` aggregation preserves the map and AI-player
breakdown. The read-only Lua and its Python controller adapter and aggregation
are archived in `endpoint-census-tools`.
