# CSC material opportunity comparison 16 October 2026

Fifteen fresh maps compare vanilla Abundant, Truly Abundant Resources (TAR) enabled with the same Abundant setting, and TAR enabled with its Truly Abundant preset. CSC remains enabled in all three groups. The five paired seeds have identical terrain and features across setups; their resource layouts differ.

**Truly Abundant increases the mean number of both-material sites for all eight Quarters. Enabling TAR while retaining Abundant mostly redistributes sites and does not consistently increase them.** Some zero counts come from an entire material class being absent: Tailors have no specialty resources on maps 1 and 5 in any group; Stonemasons have none on map 5. AI placement guidance cannot produce a connection to a class that the map does not contain.

Counts below are distinct passable land tiles adjacent to at least one base-material source and one specialty-material source. They measure geography before ownership, city reach, research and improvements. All generated resources count, including unrevealed strategic deposits. A separate filter for ordinary placement blockers appears below.

Hills count as adjacent base material for Stonemasons and Blacksmiths; Woods/Rainforest count for Carpenters. The Quarter site itself does not supply its own adjacency. One neighboring tile can match both classes through its terrain and resource; the CSV also gives counts requiring two distinct supporting tiles. Nearby candidate tiles can share sources, so these are tile opportunities rather than independent settlements.

## Vanilla Abundant

| Quarter | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 | Mean |
|---|---:|---:|---:|---:|---:|---:|
| Bakers | 22 | 40 | 13 | 41 | 42 | 31.6 |
| Tailors | 0 | 2 | 4 | 3 | 0 | 1.8 |
| Apothecaries | 1 | 6 | 1 | 11 | 5 | 4.8 |
| Stonemasons | 13 | 29 | 15 | 38 | 0 | 19.0 |
| Carpenters | 69 | 85 | 122 | 102 | 68 | 89.2 |
| Blacksmiths | 20 | 32 | 28 | 34 | 29 | 28.6 |
| Goldsmiths | 0 | 2 | 1 | 0 | 0 | 0.6 |
| Brewers | 27 | 21 | 11 | 25 | 22 | 21.2 |

## TAR with Abundant

| Quarter | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 | Mean |
|---|---:|---:|---:|---:|---:|---:|
| Bakers | 24 | 36 | 19 | 37 | 50 | 33.2 |
| Tailors | 0 | 1 | 3 | 2 | 0 | 1.2 |
| Apothecaries | 2 | 8 | 1 | 12 | 1 | 4.8 |
| Stonemasons | 15 | 13 | 22 | 35 | 0 | 17.0 |
| Carpenters | 65 | 67 | 111 | 106 | 63 | 82.4 |
| Blacksmiths | 25 | 29 | 29 | 46 | 17 | 29.2 |
| Goldsmiths | 2 | 1 | 5 | 0 | 3 | 2.2 |
| Brewers | 14 | 9 | 17 | 26 | 19 | 17.0 |

## TAR with Truly Abundant

| Quarter | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 | Mean |
|---|---:|---:|---:|---:|---:|---:|
| Bakers | 83 | 166 | 69 | 115 | 153 | 117.2 |
| Tailors | 0 | 6 | 10 | 37 | 0 | 10.6 |
| Apothecaries | 14 | 38 | 15 | 23 | 17 | 21.4 |
| Stonemasons | 32 | 61 | 42 | 65 | 0 | 40.0 |
| Carpenters | 133 | 94 | 218 | 220 | 151 | 163.2 |
| Blacksmiths | 58 | 47 | 51 | 93 | 44 | 58.6 |
| Goldsmiths | 3 | 1 | 8 | 0 | 13 | 5.0 |
| Brewers | 109 | 74 | 70 | 71 | 88 | 82.4 |

## Missing material classes

These absences persist across all three resource settings for the paired seeds. They explain the listed zero counts without relying on AI behaviour.

| Quarter | Maps | Missing specialty resources |
|---|---|---|
| Tailors | 1 and 5 | Dyes, Silk and Silver |
| Stonemasons | 5 | Gypsum and Marble |
| Goldsmiths using the individual design page | 4 | Diamonds and Jade |

Other zero counts can occur despite both classes being present, because their sources do not have a common adjacent land tile. Source counts and resource inventories are retained in the data.

## Effect of terrain and feature materials

The following means compare the complete definition against resource sources alone. This isolates the contribution of Hills or Woods/Rainforest to the geographic count.

| Quarter | Vanilla resources only | Vanilla including terrain/features | TAR Abundant resources only | TAR Abundant including terrain/features | Truly Abundant resources only | Truly Abundant including terrain/features |
|---|---:|---:|---:|---:|---:|---:|
| Stonemasons | 2.8 | 19.0 | 4.0 | 17.0 | 5.6 | 40.0 |
| Carpenters | 3.4 | 89.2 | 5.2 | 82.4 | 27.8 | 163.2 |
| Blacksmiths | 1.6 | 28.6 | 2.8 | 29.2 | 11.2 | 58.6 |

## Sites with ordinary placement blockers removed

The common clearable-site comparison excludes occupied districts, nonremovable features other than Gathering Storm floodplains, and luxury or strategic resources on the candidate tile. Bonus-resource removal and normal feature clearing are allowed after research. The same filter applies to every setup. It remains a geographic estimate rather than a complete native city-specific eligibility check.

| Quarter | Vanilla Abundant mean | TAR Abundant mean | TAR Truly Abundant mean |
|---|---:|---:|---:|
| Bakers | 31.6 | 33.0 | 99.2 |
| Tailors | 1.8 | 1.2 | 9.4 |
| Apothecaries | 4.6 | 4.8 | 19.6 |
| Stonemasons | 17.6 | 15.8 | 33.4 |
| Carpenters | 87.0 | 80.8 | 145.4 |
| Blacksmiths | 27.0 | 29.0 | 48.8 |
| Goldsmiths | 0.6 | 2.2 | 5.0 |
| Brewers | 21.0 | 16.8 | 70.8 |

The CSV additionally reports a harvest-aware count using the loaded rules. TAR makes luxury and strategic resources harvestable, so those counts can exceed the common-filter counts. Keeping this variant separate avoids attributing the effect of harvesting rules solely to distribution.

## Material definitions

Bakers and Tailors resolve to the actual loaded CSC material tags, including Flax and enabled animal materials. The six unimplemented Quarters use their individual design pages. The complete resource identifiers and feature/terrain rules are in the [material definitions](../../../tools/map_survey/materials.json).

| Quarter | Definition source | Terrain or feature sources |
|---|---|---|
| Bakers | runtime CLASS_CSC_BAKERS_BASE/SPEC | None |
| Tailors | runtime CLASS_CSC_TAILORS_BASE/SPEC | None |
| Apothecaries | [Apothecaries design](../../../../docs/content/quarters/apothecaries.md) | None |
| Stonemasons | [Stonemasons design](../../../../docs/content/quarters/stonemasons.md) | Hills |
| Carpenters | [Carpenters design](../../../../docs/content/quarters/carpenters.md) | Woods and Rainforest |
| Blacksmiths | [Blacksmiths design](../../../../docs/content/quarters/blacksmiths.md) | Hills |
| Goldsmiths | [Goldsmiths design](../../../../docs/content/quarters/goldsmiths.md) | None |
| Brewers | [Brewers design](../../../../docs/content/quarters/brewers.md) | None |

Carpenters use Copper and Iron as well as Woods/Rainforest for base materials; Aluminium, Amber, Dyes, Silk and Silver are specialty materials. The overview table and incomplete SQL stub contain older lists.

Goldsmiths use Diamonds and Jade from their individual page. The overview additionally lists Pearls; including Pearls gives the alternative counts below.

| Goldsmiths including Pearls | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 |
|---|---:|---:|---:|---:|---:|
| Vanilla Abundant | 0 | 2 | 1 | 0 | 0 |
| TAR with Abundant | 2 | 2 | 6 | 0 | 3 |
| TAR with Truly Abundant | 3 | 1 | 12 | 3 | 14 |

## Setup and verification

- Gathering Storm, Small Continents (74×46), six major civilizations, nine city states, Prince difficulty, Online speed and Ancient Era starts. No turns advance after loading turn 1.
- CSC and official content throughout. TAR is disabled for vanilla Abundant, enabled for TAR Abundant, and enabled for TAR Truly Abundant. Resource values are respectively 3, 3 and 45. Other community mods are disabled. CSC animal materials and resource cleanup use their current enabled defaults.
- Each seed pair reuses the same six leader identities across all three setups. All 3,404 terrain and feature values match within every pair.
- All 15 maps and 51,060 tile records passed coverage, coordinate, reciprocal-neighbor, setting and source checks. All 120 Quarter/map rows passed count invariants. Gameplay SQL errors: zero. All 111 recorded CSC gameplay/configuration files and TAR files remain unchanged.
- The initial edge-neighbor export was corrected to enumerate all six native directions. The first map retains its original dump and a normalization record; all non-neighbor fields are unchanged, and the final coordinate graph matches all fourteen other native exports.
- The first two maps were saved before the user chose numbers-only output. Later maps retain tile data, settings, logs and counts without manual game saves. Original mod preferences and native auto-start were restored at the final main menu.

| Map | Map seed | Game seed |
|---|---:|---:|
| 1 | 830102 | 940104 |
| 2 | 830203 | 940207 |
| 3 | 830304 | 940310 |
| 4 | 830405 | 940413 |
| 5 | 830506 | 940516 |

## Data and tools

- [All 120 Quarter/map counts and filters](C:/Users/Shadow/Desktop/Codex/csc-map-material-opportunities-20261016/quarter-opportunities.csv).
- [Individual candidate tiles and material sources](C:/Users/Shadow/Desktop/Codex/csc-map-material-opportunities-20261016/opportunity-sites.csv).
- [Map resource inventories and resolved definitions](C:/Users/Shadow/Desktop/Codex/csc-map-material-opportunities-20261016/analysis.json).
- [Paired terrain comparison](C:/Users/Shadow/Desktop/Codex/csc-map-material-opportunities-20261016/paired-map-comparison.csv) and [validation result](C:/Users/Shadow/Desktop/Codex/csc-map-material-opportunities-20261016/validation.json).
- [Collection and analysis tools](../../../tools/map_survey/README.md).
