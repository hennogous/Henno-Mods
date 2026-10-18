# Offline map generation: native calibration fixtures

Henno requested using the native luxury-diversity experiment to identify the
approximations needed for map generation outside Civ. The resulting tools are
reference capture and calibration tools; full external terrain generation is
still unimplemented.

## What the native runs capture

The private Continents test script observes terrain/features/continents/rivers/
lakes before resources, after resources, and after starting-position adjustment.
It records the resource generator's random draws without consuming extra draws.
Later runs additionally capture sampled `CanHaveResource` decisions, placement
events, adjacency-count calls and sort inputs/outputs. These wrappers forward
the original calls and are removed when resource placement finishes. No
installed game, Workshop or CSC gameplay file is edited.

Capture was requested during the batch, so fixture completeness varies. The
first four maps have final-state exports only. Each calibration JSON lists which
observations it actually contains. The five four-type control maps exactly match
the original survey's terrain, features and resources, including the instrumented
fifth control.

`project/tools/map_lab/calibrate.py` extracts these observations and compares the
actual installed stock resource Lua running under the offline API emulator. Its
frozen SQLite profile keeps a later game's database from changing a comparison.
Native RNG and optional native sort-order replay are diagnostic inputs, not
standalone implementations of those facilities.

## What has already changed

The old emulator used Fisher–Yates shuffling. Civ's installed helper selects an
element, removes it from a copy, and continues through the final size-one draw.
The emulator now loads that exact installed helper. This fixes both the shuffled
order and the number of draws consumed.

Real named continents, rivers, lakes, wrapping and map size are now captured.
Those remove the old connected-landmass continent substitution, assumed-absent
rivers and inferred lakes for these reference cases. Old exports still require
an explicit approximation flag; their missing metadata is not silently invented.

The richer exports still do not contain river-edge flow, cliffs, coastal-lowland
levels or the full starting-position database. `IsRiver` is enough for current
resource eligibility checks; it is not a complete hydrology model for procedural
terrain, every feature generator or authored YnAMP imports.

Early reference cases agree with the emulator's sampled eligibility decisions
and six-neighbour resource counts. Resource replay nevertheless diverges after
an initial matching sequence, with differing placement order visible before
the RNG-call stream diverges. Sorting, tie ordering and numerical behaviour are
therefore isolated for direct comparison. The machine-readable calibration
summary is the authority for current sample totals and remaining mismatches.

The completed batch provides eleven phase-capture cases. Across these cases the
emulator agrees with **44,002 sampled eligibility decisions** and **40,002
adjacency counts**. Of 255 captured placement-score sorts, 246 differ in ordering
when replayed with the recorded scores in ordinary Lua. Native sort replay extends
the first six-type case's matching prefix to 95 placement events before another
sort input diverges. Resource-order sorting is a remaining candidate cause.
There is **no complete exact resource-phase replay yet**, and these checks do not
validate native RNG or new terrain generation.

One attempted diagnostic wrapper changed `table.sort` and Civ rejected that
read-only standard-library table. No map from those failed attempts was counted.
The replacement observes the generator's own candidate arrays through its Lua
methods, leaving the standard sort untouched; a local read-only-library test
verified unchanged RNG state and all resource tiles.

Starting-position adjustment changes a small number of resource tiles even
after the resource Lua finishes. These differences are measured separately;
they should not be attributed to resource placement or its abundance setting.

## Route to a useful external generator

| Layer | Practical route | Validation boundary |
|---|---|---|
| Resource Lua and shared helpers | Execute the installed stock/TAR code; remove avoidable helper and API differences. | Compare pre-resource input to post-resource output, using native traces to locate divergences. |
| Placement eligibility and adjacency | Keep the SQL-backed emulator, expand it only where native cases disagree. | Native samples include resource, terrain, feature, river, lake and occupied-resource conditions. Agreement is evidence for sampled cases, not every mod rule. |
| RNG | A repeatable external stream is sufficient for statistical experiments; exact seed parity requires Civ's RNG algorithm and state at the relevant phase. | A native map seed is not the resource-phase RNG state after terrain, features and wonders have consumed draws. Recorded draws are fixtures only. |
| Sort/tie ordering | Diagnose directly from captured inputs/outputs; choose a documented deterministic approximation if the native implementation cannot be matched. | Different ties can change later adjacency scores and eligibility, eventually changing the draw stream. |
| New landforms and continent stamping | Build an explicit approximation of native fractal, tectonic, area and continent facilities. | Match distributions and spatial structure over unseen seeds; five maps cannot identify or reproduce the hidden native algorithms. |
| Climate, rivers, lakes, features and wonders | Use installed Lua where its required native APIs can be implemented; approximate the remaining engine operations explicitly. | Terrain proportions alone are insufficient: placement, clustering, co-occurrence and regional resource eligibility matter for CSC. |
| Starts and normalization | Implement approximate fertility, spacing and resource adjustment, or omit them for a clearly labelled geography-only tool. | Compare the captured post-resource and post-start phases separately. |
| TAR, Oceans and YnAMP | Load each mod's complete SQL and Lua profile and inventory its native API requirements. | These native calibration runs use vanilla resource generation. Shared API improvements help those mods, but do not certify their full pipelines. |

The immediate useful target is statistical CSC map experimentation with explicit
fidelity limits. Exact native same-seed reproduction and unrestricted drop-in
support for arbitrary map mods are separate, much larger targets.

## Measured terrain targets

`terrain_targets.py` counts each of the five landscapes once. This small
Continents-script sample has 32.5–35.2% land, 23.7–27.5% hills among land tiles,
7.9–9.2% mountains, 27.0–29.9% river-adjacent land and 24.3–27.9% Woods/Rainforest
coverage. Every map has three named continents, but four to nine connected
landmasses. This directly demonstrates why connected landmasses cannot substitute
for Civ's named continent regions.

The JSON also records latitude-band biomes, feature counts, lake counts, named
continent sizes and connected-landmass sizes. These are descriptive targets for
this setup, not universal generation rules or a reason to equalize continents.

## Reproduce

Run `calibrate.py` with explicit `--study`, `--database`, `--game-root`,
`--workshop-root`, `--lua-dependencies` and `--output` paths. The existing isolated
Lupa installation provides the Lua backends. `--reference-sorts` additionally
replays native sort orders for diagnosis; keep its results separate from normal
emulation. `--lua-backend` permits comparisons between installed runtimes.

Raw native evidence: `project/snapshots/map-lab/luxury-study/`.
Calibration: `project/snapshots/map-lab/native-calibration/`.
Terrain targets: `project/snapshots/map-lab/native-calibration/terrain-targets.json`.
Generated evidence is ignored by Git; the source tools and this interpretation
remain versioned project documentation.
