# CSC AI autoplay baseline 15 October 2026

Follow-up on 16 October: games 1–3 were saved at turn 400; games 4–5 remain at turn 200 at Henno's request. Games 1–2 have complete continuation observations. Game 3's turn-400 endpoint state was recovered from its save, with the missing turn-375–400 event history explicitly marked. The five-game statistics below remain the original turn-200 cohort. The subsequent [material opportunity comparison](csc-map-material-opportunities-20261016.md) measures fifteen fresh Online-speed maps across three resource setups.

Five natural games with CSC and the standard game AI reached turn 200. The endpoints contain **175 major-civilization cities and 188 completed Quarters**: 145 Bakers and 43 Tailors. All 30 civilization starts were automated; 29 civilizations survived to the endpoints.

The main gap is connecting Quarters to useful material supply and developing their customer relationships. Only five completed Quarters have both owned material classes adjacent, and four also have a sales district. Bakers frequently adjoin City Centers, but other sales connections and Tailors building progression are much less common. These observations establish the baseline; they do not determine whether the native AI evaluates CSC's custom adjacency rules.

## What the baseline shows

1. **Material placement needs attention, but geography limits the opportunities.** At turn 200, 79/145 Bakers and 37/43 Tailors have no owned matching material adjacent. During placement, the AI chose a zero-material site in 38/108 Bakers decisions and 8/13 Tailors decisions where the preceding player-turn scan contained a material-bearing alternative. Both owned material classes were available in only nine Bakers comparison sets and no Tailors sets; the AI chose both in three of those nine Bakers cases. These are already-owned, native-plot-legal alternatives, with the eligibility limits below.
2. **City Center adjacency accounts for most Bakers sales connections.** There are 134/145 Bakers beside a sales district, but only 9/145 beside one other than a City Center. Tailors have 8/43 sales adjacency. When a later customer district had an owned native-plot-legal option beside an existing Quarter, the AI chose that adjacency in 9/25 Bakers cases and 3/18 Tailors cases.
3. **Material retention is a separate issue from initial placement.** Twelve distinct owned resource plots that supplied surviving same-owner Bakers at placement were absent under districts by turn 200. Examples include Bananas replaced by a Campus, Preserve or Industrial Zone, Maize replaced by a Thanh, and Cattle replaced by a Commercial Hub. This identifies lost supply connections without establishing why the AI valued the replacements.
4. **Builder outcomes are mixed.** At the endpoints, 38/78 matching owned material plots beside Bakers and 2/6 beside Tailors are improved and unpillaged. Bakers-adjacent materials have a 49% improvement rate versus 43% for other owned matching materials within a city's workable radius; those groups are not matched. Of 71 initially unimproved resource–Bakers relationships, 32 received an improvement from the original owner by turn 200, with a median wait of 27.5 turns among those improved.
5. **Building progression is much stronger for mills than the rest of the chains.** Bakers have 130 mills, 14 Bakeries and no Cafes. Tailors have four Textile Workshops, no Tailor buildings and two Fashion Houses. All 43 completed Tailors had Construction researched; all 145 Bakers had the Bakery research unlock, and 130 had a mill. Zero Cafes were built despite 98 completed Bakers having both the research unlock and a mill. These counts establish progression, not the economic desirability or affordability of every building.
6. **Observed Services were limited to the Storekeeper chain.** Fifteen Storekeeper buildings exist, and twelve supplying-city Growth flags are active. There are no other Service buildings or active Service supply flags in the endpoints. All surviving players lack Naval Tradition, Urbanization and Opera and Ballet at turn 200, so this sample does not test behaviour after those Service unlocks. Bakers' Innkeeper unlock was reached for 141/145 completed Bakers, but the observed chains did not complete its material/building/customer combination.
7. **Victory flags do not establish Service intent.** Ten surviving civilization observations have an active cultural flag and own 59 Bakers and 20 Tailors. The overlapping native strategy groups are reported below. They provide context for Quarter priorities, but do not establish that any Quarter was chosen for a particular Service.

## What to compare in the first optimisation trial

Use the same seeds, settings and recorded leader rosters. Compare material-bearing sites chosen when alternatives exist, preservation of supply resources, later customer adjacency when legal, and useful building progression. Score the lost supply value when placing a district on a material resource. For Services, separate prerequisite research, source buildings, improved materials and customer venues before interpreting an absent activation.

The clearest first experiments are a material-aware placement signal, district-to-district guidance in both build orders, and valuation of the Textile Workshop and later chain buildings at useful sites. Keep the baseline intact and test those changes separately. A controlled adjacency-scoring experiment is still needed to establish what the native AI reads.

## Setup and validity

- Gathering Storm ruleset, Small Continents maps (verified 74×46), six major civilizations, nine city states, Standard speed and Prince difficulty; normal victory conditions.
- CSC plus official content, with other community mods disabled for the runs. No RomanHoliday virtual yields are present in the loaded database. No AI priorities, game content, terrain, resources, districts or buildings were changed by the recorder.
- **Five exact turn-200 endpoints, 45 labelled snapshots, five verified save checksums, zero recorder errors and zero gameplay SQL errors.** The same observer script was used throughout, and all 111 recorded installed gameplay/configuration files remained unchanged.
- Game 5's intermediate turn-125 checkpoint was captured at its actual turn 126 after the original return player was eliminated. The original event history remained intact; the game then paused correctly on a surviving return player. The final endpoint is exactly turn 200.
- Primary statistics cover major civilizations. City-state events remain in the raw history. Placement statistics exclude repeated district-added events caused by capture; final ownership statistics include captured districts.
- Civ is back at the main menu. Original mod preferences and native auto-start were restored and verified. The previously active turn-1 game was saved separately before the batch.

| Game | Map seed | Game seed |
|---|---:|---:|
| 1 | 830102 | 940104 |
| 2 | 830203 | 940207 |
| 3 | 830304 | 940310 |
| 4 | 830405 | 940413 |
| 5 | 830506 | 940516 |

The [baseline tools](../../../tools/ai_baseline/README.md) document collection, resumption and interpretation. Exact research/building metadata, stock AI weights and mod file hashes are retained in the raw archive.

## Games

| Game | Cities | Completed Bakers | Completed Tailors | Active supply stages |
|---|---:|---:|---:|---:|
| game-01 | 36 | 30 | 9 | 3 |
| game-02 | 36 | 27 | 8 | 3 |
| game-03 | 41 | 34 | 10 | 2 |
| game-04 | 29 | 24 | 6 | 3 |
| game-05 | 33 | 30 | 10 | 1 |

## Quarter placement and development

Metrics below use completed Quarters at turn 200. Materials must be visible and player-owned. Improvement counts deduplicate plots within each Quarter type and player.

| Metric | Bakers | Tailors |
|---|---:|---:|
| Completed Quarters | 145 | 43 |
| Adjacent base material | 51/145 (35%) | 4/43 (9%) |
| Adjacent specialty material | 20/145 (14%) | 2/43 (5%) |
| Both material classes | 5/145 (3%) | 0/43 (0%) |
| Sales district adjacent | 134/145 (92%) | 8/43 (19%) |
| Sales district other than City Center | 9/145 (6%) | 8/43 (19%) |
| Both materials and sales district | 4/145 (3%) | 0/43 (0%) |
| No material adjacency | 79/145 (54%) | 37/43 (86%) |
| Both classes improved | 2/145 (1%) | 0/43 (0%) |
| Stage 2 building present | 130/145 (90%) | 4/43 (9%) |
| Stage 3 building present | 14/145 (10%) | 0/43 (0%) |
| Stage 4 building present | 0/145 (0%) | 2/43 (5%) |
| Adjacent owned material plots improved | 38/78 (49%) | 2/6 (33%) |
| Both classes chosen when available at player-turn start | 3/9 (33%) | 0/0 |
| Both classes and sales chosen when available | 1/7 (14%) | 0/0 |
| Maximum material count chosen when a material site existed | 55/108 (51%) | 4/13 (31%) |
| Unlocked cities without Quarter with a current both-material site | 1/14 (7%) | 0/125 (0%) |

## Customer district follow-up

| Quarter | Later customer placements | Adjacent placements | Adjacent chosen when an owned legal option existed |
|---|---:|---:|---:|
| Bakers | 30 | 9 | 9/25 (36%) |
| Tailors | 68 | 3 | 3/18 (17%) |

A later customer placement means its owner had already placed that Quarter in an earlier turn. City Centers are excluded. These are descriptive choices, not proof of AI intent.

## Material improvement follow-up

| Quarter | Initially unimproved owned materials beside new Quarters | Improved later by turn 200 | Median wait among improved |
|---|---:|---:|---:|
| Bakers | 71 | 32/71 (45%) | 27.5 |
| Tailors | 3 | 0/3 (0%) | n/a |

This follow-up is counted per resourceâ€“Quarter relationship; late placements have less time to receive improvements. It is not a matched test of builder priorities.

| Quarter | Adjacent materials within workable radius | Adjacent with relevant source building | Non-adjacent materials within workable radius |
|---|---:|---:|---:|
| Bakers | 38/78 (49%) | 21/50 (42%) | 57/134 (43%) |
| Tailors | 2/6 (33%) | 0/1 (0%) | 29/51 (57%) |

These are descriptive final-state comparisons within three tiles of an owner city. They are not matched for city age, terrain, resource type or time exposed to a Quarter. The relevant building is stage 2 for base materials and stage 4 for specialty materials.

## Material retention

| Quarter | Initially owned material relationships for surviving same-owner Quarters | Resource still present | Resource replaced by district |
|---|---:|---:|---:|
| Bakers | 72 | 57 | 12 |
| Tailors | 4 | 4 | 0 |

These comparisons establish that a resource was present at Quarter placement and absent under a district at turn 200. They do not identify the AI reasoning behind clearing it.

## Building progression

| Quarter and stage | Research unlocked | Stage 2 prerequisite also present | Building present among those candidates |
|---|---:|---:|---:|
| Bakers stage 2 | 145/145 | 145 | 130 |
| Bakers stage 3 | 145/145 | 130 | 14 |
| Bakers stage 4 | 108/145 | 98 | 0 |
| Tailors stage 2 | 43/43 | 43 | 4 |
| Tailors stage 3 | 43/43 | 4 | 0 |
| Tailors stage 4 | 31/43 | 4 | 2 |

Research unlocks come from the captured runtime gameplay database. These counts do not test affordability or every production restriction.

## Services

| Supply activation property | City observations at turn 200 |
|---|---:|
| `CSC_BAKERS_STAGE_2_EFFECT_GROWTH` | 12 |

| Quarter and stage | Civic unlocked | Source building also present | Improved material gate also met | Required venue also adjacent |
|---|---:|---:|---:|---:|
| Bakers stage 2 | 145/145 | 130 | 20 | 12 |
| Bakers stage 3 | 141/145 | 14 | 2 | 0 |
| Bakers stage 4 | 0/145 | 0 | 0 | 0 |
| Tailors stage 2 | 0/43 | 0 | 0 | 0 |
| Tailors stage 3 | 10/43 | 0 | 0 | 0 |
| Tailors stage 4 | 0/43 | 0 | 0 | 0 |

The endpoints contain 15 Storekeeper buildings and no other hidden Service building types. Twelve city observations have the Bakers stage 2 Growth supply flag active. Building presence and supplying-city flags are different counts and are not a one-to-one count of active beneficiaries. Neither measure proves deliberate Service planning.

## Quarter ownership and native victory strategy flags

| Active native flag at turn 200 | Civilization observations | Completed Bakers owned | Completed Tailors owned |
|---|---:|---:|---:|
| Cultural | 10 | 59 | 20 |
| Religious | 19 | 98 | 29 |
| Science | 21 | 113 | 31 |
| Military | 4 | 21 | 8 |
| Diplomatic | 6 | 36 | 11 |

Flags come from the final game segment in AI_Victories.csv, using the latest status for each strategy. A civilization can follow several flags simultaneously. These are overlapping descriptive groups, not exclusive victory commitments or evidence of CSC-specific intent.

## Interpretation limits

- The sample covers the implemented Bakers and Tailors Quarters. Five games are a descriptive baseline, not a causal experiment.
- Candidate comparisons use the most recent player-turn-start scan, at most one turn old, and native plot placement checks on already owned tiles. They do not include future tile purchases, tile swaps, affordability, or full production eligibility. Ownership or occupied plots can change during a turn.
- The final snapshot is at the beginning of turn 200, following 199 advances from turn 1. District events include placement before completion; final placement statistics use completed districts.
- Capture, pillage, resource discovery and border expansion can change final adjacency. Placement-time choices are recorded separately.
- Setup pilots are excluded. Game 5 lost its original return player; its intermediate snapshot is correctly recorded at turn 126 instead of 125. The runner then returned to a surviving player. All five final snapshots and saves are at turn 200.

Raw evidence on Shadow: `C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/`. The archive includes turn snapshots, district/improvement events, five completed saves, per-game logs, installed gameplay hashes, seed settings and command transcripts. [Validation](C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/validation.json), [aggregate data](C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/analysis.json), [Quarter observations](C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/details.csv), [placement choices](C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/choices.csv), [customer choices](C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/customer_choices.csv), [strategy profiles and leader rosters](C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/strategy_profiles.csv).
