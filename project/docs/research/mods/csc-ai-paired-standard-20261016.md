# CSC AI baseline: five vanilla and five TAR Standard games

**Complete — 17 October 2026.** All ten real Civ games reached exactly turn 250 on Online speed. The five vanilla worlds reproduce the earlier Standard captures; the other five use Truly Abundant Resources with the same Standard resource setting, seeds and leaders. No AI tuning was applied.

This is the current baseline for improving AI use of the implemented Bakers’ and Tailors’ Quarters. Material access is especially relevant to Services; Quarters can still earn through goods sales without adjacent materials.

## Endpoint at turn 250

| Setup | Major cities | Completed Bakers | Bakers Base-only / Both | Completed Tailors | Tailors Base-only / Both |
|---|---:|---:|---:|---:|---:|
| Vanilla Standard | 296 | 259 | 55 / 1 | 132 | 7 / 1 |
| TAR + Standard | 302 | 252 | 48 / 4 | 133 | 11 / 0 |

Base-only and Both are exclusive. Counts require adjacent revealed materials owned by the same player. They describe completed Quarters at the endpoint, not every placement event or every geographic opportunity. There are 776 completed Quarters across 598 major-city observations; six retain both owned material classes.

## Placement decisions when materials were available

| Setup | Quarter | Chose Base when Base was available | Chose Both when Both was available | Chose Base + Sales when that combination was available |
|---|---|---:|---:|---:|
| Vanilla Standard | Bakers | 80/144 (56%) | 4/16 (25%) | 60/125 (48%) |
| Vanilla Standard | Tailors | 11/28 (39%) | 1/3 (33%) | 1/10 (10%) |
| TAR + Standard | Bakers | 73/143 (51%) | 4/19 (21%) | 59/138 (43%) |
| TAR + Standard | Tailors | 13/34 (38%) | 0/1 (0%) | 0/9 (0%) |

These alternatives were already owned and passed native plot placement checks in the most recent player-turn-start scan, at most one turn old. They do not include future purchases, affordability or every city production restriction. Tile yield, removal costs and other city plans can justify a different choice; these counts expose available material access rather than proving the best overall site.

Across both setups, the AI chose Base access in 153/287 Bakers placements (53%) and 24/62 Tailors placements (39%) when a Base-bearing alternative was recorded. Both-class Tailor choices had only four such observed opportunities across ten games, so that tiny denominator should not drive tuning.

## Material improvements and later sales districts

| Setup | Quarter | Improved adjacent Base plots | Improved adjacent Specialty plots | Later sales district chose Quarter adjacency when available |
|---|---|---:|---:|---:|
| Vanilla Standard | Bakers | 18/61 (30%) | 25/27 (93%) | 47/151 (31%) |
| Vanilla Standard | Tailors | 2/8 (25%) | 2/3 (67%) | 47/125 (38%) |
| TAR + Standard | Bakers | 14/54 (26%) | 9/13 (69%) | 36/129 (28%) |
| TAR + Standard | Tailors | 2/11 (18%) | 4/5 (80%) | 42/111 (38%) |

Improvement counts deduplicate material plots within each Quarter/player sample and exclude pillaged improvements. A material plot can support several Quarters. Specialty plots were improved much more frequently than Base plots. Some Base plots can also lie outside a city’s workable radius; the CSV retains that distinction and whether the relevant source building existed.

61 distinct originally owned adjacent material plots were later absent beneath a district for surviving same-owner Quarter relationships. The raw ledger distinguishes resource loss, ownership changes and the final district; it does not identify the AI’s reason for clearing the deposit.

The sales comparison excludes City Centers and requires a previous Quarter plus a fresh native plot-legal adjacency alternative. Repeated capture-related appearances of the same district plot/type are excluded from placement counts.

## Buildings and Services

| Setup | Quarter | Stage 2 / 3 / 4 buildings in completed Quarters |
|---|---|---:|
| Vanilla Standard | Bakers | 239 / 105 / 52 |
| Vanilla Standard | Tailors | 114 / 68 / 40 |
| TAR + Standard | Bakers | 237 / 96 / 31 |
| TAR + Standard | Tailors | 102 / 55 / 29 |

Native supply activation properties at the endpoint show:

| Setup | Bakers Growth sources | Bakers Housing sources | Bakers Tourism sources | Tailors supply sources, all stages |
|---|---:|---:|---:|---:|
| Vanilla Standard | 6 | 1 | 0 | 0 |
| TAR + Standard | 8 | 1 | 0 | 0 |

These are source-city/stage activations at turn 250, not recipient hidden-building counts or a claim that a Service never activated earlier. Snapshot histories retain the intermediate properties. Native flags are authoritative; the service-opportunity CSV is a diagnostic model of civic, source-building, material and venue exposure, rather than a complete native requirement evaluator.

Base materials alone can support stage 2 and 3 Services. Specialty material and both-class placement are needed for stage 4, whose rarity remains an intentional part of the design. The baseline therefore supports examining Base placement, Base improvements and customer adjacency before trying to make Both-class sites ubiquitous.

## Individual maps

| Setup | Seed pair | Major cities | Bakers complete / Base-only / Both | Tailors complete / Base-only / Both |
|---|---:|---:|---:|---:|
| Vanilla Standard | 1 | 48 | 45 / 8 / 0 | 22 / 1 / 0 |
| Vanilla Standard | 2 | 58 | 50 / 11 / 0 | 29 / 1 / 0 |
| Vanilla Standard | 3 | 64 | 56 / 10 / 0 | 29 / 3 / 1 |
| Vanilla Standard | 4 | 64 | 58 / 16 / 0 | 29 / 1 / 0 |
| Vanilla Standard | 5 | 62 | 50 / 10 / 1 | 23 / 1 / 0 |
| TAR + Standard | 1 | 58 | 50 / 12 / 0 | 22 / 0 / 0 |
| TAR + Standard | 2 | 61 | 49 / 8 / 0 | 30 / 2 / 0 |
| TAR + Standard | 3 | 68 | 52 / 6 / 1 | 34 / 2 / 0 |
| TAR + Standard | 4 | 60 | 53 / 13 / 3 | 25 / 2 / 0 |
| TAR + Standard | 5 | 55 | 48 / 9 / 0 | 22 / 5 / 0 |

## Reproduction and evidence

- Continents.lua, Small 74×46, six majors and nine city states, Gathering Storm, Online, Prince, ordinary victory conditions.
- CSC production material pass v3, Bakers/Tailors scope, direct Tailor assistance; animals enabled, unused modded resource cleanup enabled, M&C disabled.
- Vanilla Standard (2) in both groups; TAR enabled only in the second. Its separate Truly Abundant preset was not selected. TAR’s resource validity and harvest rules also apply during that group’s games.
- Map seeds: 830102, 830203, 830304, 830405, 830506. Game seeds: 940104, 940207, 940310, 940413, 940516. Leader rosters repeat across the paired setups.
- All five vanilla initial maps match the earlier captures across 13 fields on every one of their 3,404 tiles. TAR comparisons retain per-field differences; resources and resulting start locations may differ.
- Read-only observer v3, complete district/improvement history and owned candidate scans. Continuous autoplay avoids returning human control at intermediate checkpoints.
- Turn 1 plus frozen snapshots every 25 turns through 250: 110 snapshots. Endpoint means the beginning of turn 250 after 249 advances; intermediate snapshots are captured at the first major-player activation.
- Ten initial and ten final native saves have verified SHA-256 checksums. Event prefixes, material counts, zero observer/Gameplay SQL errors and all 115 installed gameplay files passed verification.
- The same observer v3 and installed gameplay were used for all valid games. Controller reconnect, return-player and save-preparation revisions are explicitly retained in controller-revisions.json; exact native commands are archived.
- A fresh native read confirms Civ at its background main menu, all 141 original unique mod preference flags restored and auto-start false. The native API returns one duplicate mod entry, which is accounted for.

The interrupted first controller trial, which returned human control every 25 turns and stalled on a diplomacy session at 50, is excluded entirely. Game 1 was regenerated from the same exact initial map and rerun continuously. No diplomatic response was submitted by the controller.

Game 6’s final save was initially blocked by a disaster animation opened on return at 250. Closing that playback completed one capital’s automatic growth from 10 to 11 within the same turn. Quarter, plot, research, Service and event data were unchanged. The standardized benchmark census is retained; a separate settled census describes the saved state. Later final saves also clear visible playback and retain a separate save-state census. No extra turn or AI decision was requested.

Raw evidence: `C:/Users/Shadow/Desktop/Codex/csc-ai-paired-standard-20261016/`. Key files are analysis.json, validation.json, preferences-restored.json, per-map-quarter-stats.csv, base_placement_choices.csv, choices.csv, customer_choices.csv, improvement_comparison.csv, improvement_timing.csv, material_retention.csv, service_opportunities.csv and the per-game turn snapshots, saves and logs.

Source tools: [runner](../../../tools/ai_baseline/paired_standard.py), [observer](../../../tools/ai_baseline/paired_observer.lua), [analysis](../../../tools/ai_baseline/paired_analysis.py), [verification/reproduction instructions](../../../tools/ai_baseline/README.md).

Five games per setup are a descriptive baseline. They do not establish causal AI understanding of CSC adjacency or statistical superiority of either resource setup. The earlier Standard-speed study used a different setup and boundary-neighbour enumeration and is retained as historical evidence. No AI optimisation has been applied yet.


## Sales transaction prevalence — retrospective19October2026

### Sales relationships

Functioning same-owner adjacent building-pair relationships at250, reconstructed from checkpoints; not individually logged payments or cumulative transaction counts. No material or Service-civic gate for ordinary sales. Stage4 requires customer population>=5. CityCenter defense pillage flag ignored for Granary; building pillage respected. One-level native district/building replacements included.

Ten baseline games (five vanillaStandard, fiveTARStandard), plus three completed250-turn tuning games. AllOnline. Earlier400-turn maps and incomplete runs excluded from this comparison.

Entries are producers selling / functioning producers, followed by number of distinct producer-customer links in parentheses.

| Route | 10 baseline games | Placement v1 | Native v3 | Density v4 |
|---|---:|---:|---:|---:|
| Wind Mill → Granary | 121/398 (121) | 26/37 (26) | 25/33 (25) | 22/33 (22) |
| Water Mill → Granary | 31/78 (31) | 6/8 (6) | 7/13 (7) | 8/10 (8) |
| Bakery → Market | 25/201 (28) | 21/30 (21) | 16/27 (18) | 15/33 (16) |
| Café → Zoo | 3/83 (3) | 1/16 (1) | 3/15 (3) | 1/15 (1) |
| Café → Ferris Wheel | 0/83 (0) | 2/16 (2) | 3/15 (3) | 0/15 (0) |
| Textile Workshop → Lighthouse | 10/216 (10) | 3/26 (3) | 7/30 (7) | 3/23 (3) |
| Tailor → Market | 14/123 (14) | 12/15 (12) | 12/22 (13) | 4/15 (7) |
| Tailor → Temple | 6/123 (6) | 5/15 (6) | 12/22 (12) | 6/15 (6) |
| Fashion House → Amphitheater | 15/69 (15) | 3/9 (4) | 8/14 (8) | 6/10 (6) |
| Fashion House → Bolshoi | 0/69 (0) | 0/9 (0) | 0/14 (0) | 0/10 (0) |
| Fashion House → Broadway | 0/69 (0) | 0/9 (0) | 0/14 (0) | 0/10 (0) |
| Fashion House → Sydney Opera House | 0/69 (0) | 0/9 (0) | 0/14 (0) | 0/10 (0) |

### Quarter coverage

| Group | Completed Quarters selling | Links |
|---|---:|---:|
| Vanilla baseline | 119/391 | 132 |
| TAR baseline | 92/385 | 96 |
| Placement v1 | 48/78 | 81 |
| Native bonus/river v3 | 59/84 | 96 |
| Density v4 / Builder900 | 48/71 | 69 |

Resource support is not required for these sales; material access instead enables additional extraction interactions and Services. Counts establish structural eligibility; actual applied economic-yield/payment amounts were not recorded in these censuses. Detailed per-game and per-link results in sales.json.


Additional bottleneck check: across the ten baseline games,28 of201 functioning Bakeries were adjacent to a functioning same-owner Commercial Hub, and25 had a Market customer. Only14 of216 Textile Workshops were adjacent to a functioning Harbor,10 with a Lighthouse. Eight of123 Tailors were adjacent to a functioning Holy Site,6 with a Temple. In completed density-v4,15 of33 Bakeries had the Hub adjacency and all15 had a Market;3 of23 Workshops had Harbor adjacency and all3 had Lighthouses;7 of15 Tailors had Holy Site adjacency,6 with Temples. Much missing sales access is district geography rather than missing customer buildings.

Of211 baseline Quarters with a qualifying sales relationship,172 lacked owned visible Base materials (133 Bakers/39 Tailors). This confirms structural sales eligibility can coexist with poor material access; actual yield receipt was not instrumented in these snapshots. Comparison groups pool10 baseline games versus one game per tuning variant; map/resource assistance, AI treatments and later war/expansion differ, so differences are descriptive, not isolated causal effects. Stage4 Wonder routes allzero across these13 endpoints; Cafe Zoo/Ferris counts remain tiny.

Reproduction: project/tools/ai_baseline/sales_prevalence.py, archived native diagnostic11 definitions only for direct replacement families; original source SQL and CustomerPopulationReturns script inspected for adjacency, ownership, pillage and material-independent sales rules. Scope is external customer-building sales; internal Mill→Bakery/Workshop→Tailor/FashionHouse exchanges and trade-route exports are not included. All10 baseline game endpoints plus three validated completed tuning endpoints at250; older400 games and incomplete runs omitted.
