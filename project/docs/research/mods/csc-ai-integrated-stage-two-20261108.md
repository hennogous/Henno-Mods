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
