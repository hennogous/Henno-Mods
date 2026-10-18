# Tailor density v4 — six fresh native maps, 17 October 2026

Three vanilla Standard maps and three vanilla Abundant maps, paired on three fresh seed pairs. CSC v4 ran automatically inside Civ during map initialization. Online/Prince, Small Continents (74×46), six majors/nine city states, animals enabled, unused-resource cleanup enabled, M&C off. CSC was the only active community mod; TAR and RH disabled. No autoplay or game saves.

## Placement opportunities

Counts are ordinarily clearable land tiles adjacent to mapped Base materials. Base-only excludes Specialty adjacency; both requires both material classes. Ownership, city reach, improvements and research are not filters. Neighbouring sites can share resource deposits.

| Resources | Map | Map seed / game seed | Bakers Base-only / both | Tailors Base-only / both | CSC copies added |
|---|---:|---|---:|---:|---:|
| Abundant | 1 | 830607 / 940619 | 317 / 62 | 199 / 24 | 31 |
| Abundant | 2 | 830708 / 940722 | 347 / 33 | 232 / 24 | 34 |
| Abundant | 3 | 830809 / 940825 | 347 / 36 | 172 / 44 | 29 |
| Standard | 1 | 830607 / 940619 | 344 / 38 | 200 / 12 | 23 |
| Standard | 2 | 830708 / 940722 | 366 / 20 | 208 / 28 | 29 |
| Standard | 3 | 830809 / 940825 | 307 / 39 | 198 / 12 | 21 |

## Material copies

Bakers and Tailors overlap through shared Flax; their totals must not be added together as distinct map resources. Quantity is read from native plots, not inferred from the number of deposits.

| Resources | Map | Bakers Base / Specialty copies | Tailors Base / Specialty copies | Added Bakers Base / Specialty | Added Tailors Base / Specialty |
|---|---:|---:|---:|---:|---:|
| Abundant | 1 | 104 / 30 | 50 / 15 | 7 / 0 | 24 / 7 |
| Abundant | 2 | 111 / 22 | 55 / 14 | 13 / 0 | 28 / 6 |
| Abundant | 3 | 104 / 23 | 45 / 19 | 13 / 0 | 23 / 6 |
| Standard | 1 | 99 / 25 | 46 / 10 | 9 / 0 | 20 / 3 |
| Standard | 2 | 104 / 21 | 50 / 13 | 13 / 0 | 24 / 5 |
| Standard | 3 | 85 / 21 | 42 / 13 | 7 / 0 | 19 / 2 |

## Individual resource inventory

### Abundant map 1

- Bakers base: Bananas 10, Cattle 15, Flax 24, Maize 16, Rice 15, Wheat 24.
- Bakers spec: Coffee 8, Honey 6, Olives 4, Salt 4, Sugar 8.
- Tailors base: Cotton 3, Flax 24, Sheep 23.
- Tailors spec: Dyes 2, Silk 2, Silver 11.

### Abundant map 2

- Bakers base: Bananas 8, Cattle 16, Flax 31, Maize 15, Rice 14, Wheat 27.
- Bakers spec: Coffee 5, Honey 5, Olives 8, Tea 4.
- Tailors base: Cotton 3, Flax 31, Sheep 21.
- Tailors spec: Dyes 2, Silk 6, Silver 6.

### Abundant map 3

- Bakers base: Bananas 10, Cattle 16, Flax 27, Maize 12, Rice 16, Wheat 23.
- Bakers spec: Olives 5, Salt 7, Spices 6, Tea 5.
- Tailors base: Cotton 3, Flax 27, Sheep 15.
- Tailors spec: Dyes 9, Silk 1, Silver 9.

### Standard map 1

- Bakers base: Bananas 10, Cattle 14, Flax 25, Maize 15, Rice 13, Wheat 22.
- Bakers spec: Coffee 7, Honey 5, Olives 3, Salt 3, Sugar 7.
- Tailors base: Cotton 4, Flax 25, Sheep 17.
- Tailors spec: Dyes 1, Silk 2, Silver 7.

### Standard map 2

- Bakers base: Bananas 10, Cattle 15, Flax 29, Maize 15, Rice 11, Wheat 24.
- Bakers spec: Coffee 5, Honey 5, Olives 7, Tea 4.
- Tailors base: Cotton 4, Flax 29, Sheep 17.
- Tailors spec: Silk 6, Silver 7.

### Standard map 3

- Bakers base: Bananas 7, Cattle 13, Flax 22, Maize 11, Rice 14, Wheat 18.
- Bakers spec: Olives 5, Salt 6, Spices 5, Tea 5.
- Tailors base: Cotton 3, Flax 22, Sheep 17.
- Tailors spec: Dyes 7, Silk 1, Silver 5.

## Continental coverage

| Resources | Map | Continent instances | Bakers Base / both coverage | Tailors Base / both coverage | Tailor both-site clusters |
|---|---:|---:|---:|---:|---:|
| Abundant | 1 | 3 | 3 / 3 | 3 / 3 | 17 |
| Abundant | 2 | 3 | 3 / 3 | 3 / 3 | 13 |
| Abundant | 3 | 3 | 3 / 3 | 3 / 3 | 18 |
| Standard | 1 | 3 | 3 / 3 | 3 / 3 | 7 |
| Standard | 2 | 3 | 3 / 3 | 3 / 3 | 14 |
| Standard | 3 | 3 | 3 / 3 | 3 / 3 | 8 |

## Verification and interpretation

All six maps stayed at turn1. The native audit confirms version4, successful automatic startup before UI, actual resource quantity1 for each addition, and the captured native eligibility for every placement. Original resources/quantities and other plot fields are preserved. Exact offline replay of native pre-pass inputs matches additions, palettes, continental counts and density targets. An independent census agrees with the audit. Installed gameplay/source pins and read-only controller transcripts pass. Original mod preferences and auto-start were restored and freshly verified; diagnostic capture was disabled.

The new seeds were not used in the previous five-map preview. Same-seed Standard/Abundant landscapes were checked separately; resource distribution and starting decisions may vary between levels. The density target is relative to each map after the original continental repair:2× Tailor Base-only and4× both, with an abundance-scaled minimum for zero both-class counts. Small site-count overshoots can occur because one deposit supports multiple candidate centers. Baker opportunities may benefit from shared Flax.

This measures material geography, not AI behavior or established Services. No AI tuning coefficients changed during the six-map experiment. Historical v3 worlds and prior AI tests remain separate.

Evidence: `C:\Users\Shadow\Desktop\Codex\csc-tailor-density-native-20261017`. Per-map maps, audits, native eligibility, resource inventories, logs and exact replay checks are retained; aggregate tables are resource-stats.json and resource-stats.csv.

## Controller recovery notes

The first Abundant map encountered a transient debug-console disconnect while
loading. Civ remained alive and completed the map. Read-only retries were
added, original controller/status evidence was preserved, and the existing
turn1 game was resumed; no map was regenerated. All six maps verified before
the aggregate exporter hit an omitted optional feature-key lookup. That
comparison was corrected offline using get(): all three pairs have zero
terrain/feature/continent/river/lake/neighbour differences. Source copies and
pins before the controller-only corrections are retained under connection-reload/.
The actual runtime Core/adapter and installed build remained unchanged
throughout generation. validation.json and finalization-source-hashes.json
record the completed checks. No native regeneration was needed.
