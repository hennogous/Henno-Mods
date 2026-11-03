# Modern Quarter roads: first roundabout kit

## Agreed layout and progression

Henno's 29 October 2026 sketch replaces the central classical criss-cross with a
medium roundabout, five exits, and a narrower lower connector joining the two lower
branches without crossing the circle. The entire layout initially uses Industrial
stone paving. The first building adds tarmac to the circle, the two upper exits
beside storage, and the bottom-right Stage 2 exit. Other branches pave when their
destinations require them; this is not a sequential Stage 3 → Stage 4 upgrade.

**Existing major roads are fixed anchors.** Inspect the current classical master
at scale 1 before designing internal connections. Preserve exit centerlines,
headings and road-width compatibility. Do not substitute guessed coordinates from
an earlier concept/draft. Compare actual UV/alpha coverage, not rectangular card
bounds. Keep an equal-scale overlay as delivery evidence.

## Authoring candidate

Working Files source: `3D Art/Decals/CSC_ALL_Modern_Roads/` (Henno's current organization).
Main layout: `CSC_ALL_Modern_Roundabout_Kit.blend`. Its Review scene shows the
first-building state; additional scenes show all stone, either independent extra
branch, and all routes paved. Export contains the complete Industrial base only.
`modules/` contains fourteen separate editable masters and CN6s: circle, five
branches and lower connector, each in Industrial and Modern surfaces. Each master
has a clean Export and separate ground-level Review. Edit shared mesh data to
keep preview and projection synchronized; retain Quarter-coordinate placement.

Paired `CSC_Roads_Industrial_01` and `CSC_Roads_Modern_01` atlases are 512px and use
identical UV allocations. Each includes a five-exit circle, straight, curve,
junction, narrow connector, plain strip, transition, fading end and small patch.
The surface paint and stone height detail come from recorded Firaxis
`Decals_Parts_*_01` source crops. New masks and restrained off-white road markings
are technical artwork; no new procedural surface paint was generated. Native
Modern grayscale height in the selected asphalt crop varies from 84 to 90.
Its alpha255 was initially misread as flat height; the channel repair below
supersedes that interpretation and the original Blender preview wiring.

External B/H/FOW/S PNGs and candidate mipmapped DDSs are in `textures/`.
B/FOW use coverage alpha and sRGB; H is linear grayscale RGB height with coverage
in alpha; S is linear.
Height gutters prevent filtering into unrelated cells. Paint coverage and fading
are stored in B alpha, not Blender-only shader coordinates.

### Worn paving underlay

Henno requested worn shoulders serving the same blending role as Ancient roads
under Classical roads. The Industrial B/FOW now retain the original native paving
in the center and add ImageGen-painted broken stone, small chips and muted dirt
at the margins. Coverage fades irregularly beyond the tarmac edges, including
the circle's inner boundary. Typical fringe limits are 4.5 world units on strips
and 5.5 on larger cells; these fit the existing projection cards and UV layout.
The matching fringe relief is derived from that painted detail in H RGB.
Modern atlas maps and all geometry/UVs remain unchanged.

`wear.py` historically fitted the generated painting to the existing cells without
regenerating the layout. It is now disabled because its height-channel handling
was incorrect; preserve the saved painting and use the corrected H convention.
`refresh.py` validates the saved masters and refreshes stage renders
after external texture edits. The initial `prepare.py` now refuses to overwrite
the painted revision. The complete paint prompt is maintained alongside these
tools; the generated source, source hashes and cell coverage measurements are
recorded in `shoulder-paint-provenance.json` in the evidence directory. The
pre-paint texture snapshot is `history/before-worn-shoulders/` there.

Henno's current marking direction is **pedestrian crossings only**, one across
each of the five exits. Center dashes, give-way symbols and the inner ring line
were removed: the road width relative to the compact flatbed truck should not
suggest two vehicle lanes. Each crossing uses five off-white stripes and is
painted into the existing roundabout cell. No geometry or UV changes are needed.
The lower connector remains unmarked. Its tarmac overlay is enabled in the
southwest-destination preview, since the southeast Stage 2 branch is already paved.
`crossings.py` records this one-time replacement; the initializer now uses the
same crossing-only design. Worn Industrial shoulders are preserved.

## Classical alignment

Source: `3D Art/Quarters/CSC_ALL_Classical_Base_05_Road_Decals.blend`.
The five external corridors use exact centerlines derived from the source fade
cards, including their final straight sections and outward tangents:

| Modern branch | Classical source |
|---|---|
| NW | `CSC_Road_Fade.001_CLA#M` |
| NE | `CSC_Road_Fade.004_CLA#M` |
| E | `CSC_Road_Fade.003_CLA#M` |
| SE / bottom-right Stage 2 | `CSC_Road_Fade.005_CLA#M` |
| SW / lower-left | `CSC_Road_Fade.006_CLA#M` |

The old sixth spur, `Fade.002`, is omitted per the five-exit brief. Modern carriageway
width was initially 26 units with an 18-unit connector. The vanilla calibration
below supersedes these with 15 and 10.38 units respectively. Classical Ancient+Classical
combined coverage at sampled outer approaches is approximately 20–29 units at
15–30 units into the fade cards (coverage-weighted width, including soft shoulders).
Clean paved edges are not pixel-identical to irregular historical shoulders.
The original painted circle has inner radius55 and outer radius81; its current
mapped lane is approximately radius60.5–75.5 away from the exit mouths.
Following Henno's overlay
review it was shifted 40 units right and 20 down, from (-35,30) to (5,10).
The approach curves were reshaped while the five outer corridors stayed fixed.

The first draft's guessed endpoints were corrected after Henno explicitly asked
for alignment verification. Use the live-source measurements and overlay from
this revision, not the earlier angular draft's node list.

## Reproduction and evidence

### Applied shoulder correction — 29 October

The later crossing-lightness fix removes doubled opacity at the overlap with
approach decals. The original ring~0.49 alpha combined with approach~0.49 to
produce~0.74 just past the crossing. Complementary ring alpha and a12-unit smooth
fade in the approach plain cell now preserve the stronger single-layer coverage
through the join. RGB/geometry/UVs and crossing widths are retained. ThreeDDS
installed; mip coverage, width checks, cook and cache pass. Evidence:
`crossing-blend-20261029/`; tool `crossing_blend.py`. Live shader review pending.

The subsequent crossing refinement follows the actual flared paved footprint
near the five pedestrian crossings. The first shoulder pass narrowed to2.45–3.35
visible units at their inner edge; localized B/FOW/H alpha expansion restores
at least3.5 units per side across15 sampled crossing cross-sections. RGB artwork,
geometry, UVs and all existing assemblies remain unchanged. Three updated DDSs
are installed; all-mip coverage, isolated cook and browser checks pass. Evidence:
`crossing-shoulders-20261029/`; tool `crossing_shoulders.py`.

Henno explicitly requested the fix after the measurement below. The Industrial
underlay now uses the existing stone core with projected native Firaxis Ancient
gravel RGB/height, and a broad alpha falloff calibrated to the native samples.
Measured post-fix medians beyond each asphalt edge are4.25 units at50% coverage,
8.95 at25%, and13.55 at10%. Tight inside bends compress the shoulder locally;
folded triangles were removed rather than retaining overlapping projection cards.

The tarmac atlas, tarmac geometry/UVs, road centerlines and Z0/Z1 order are retained.
Industrial projection cards expand separately: main strips64 units across,
connector56, roundabout236×236, elbow64×64. These are projection bounds including
transparent margins, not visible road widths. Industrial-specific sizes are in
each atlas cell's `industrial_world_size`; Modern keeps the prior mapping.
The new30-degree elbow is included. H and B coverage match through all10 mips.

All23 saved sources were checked. Fourteen affected native geometries and three
Industrial DDS maps are installed for AE (31GEO/FGX/DDS files), with browser-cache
verification and a successful isolated cook. Existing ASTs, materials, ArtDefs
and XLPs are preserved. Live AE/game visual review remains outstanding.

Current outputs and validation: `Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout/shoulders-fixed-20261029/`.
`Shoulders_Before_After.png` and `Classical_Fixed_Modern_Overlay.png` use actual
mapped texture coverage at the same world scale. Tool: `fix_shoulders.py`.

### Shoulder measurement and 30-degree elbow — 29 October

Paired native Ancient underlay/Modern tarmac cards were sampled at33 cross-sections
in the Commercial Hub and Campus. Unrelated ground patches were excluded. Median
underlay extension beyond each asphalt edge is3.78 units at50% alpha,8.60 at25%,
and13.20 at10%. These are opacity contours, not three separate uniform bands.
CSC's narrowed stone underlay measures0.425,0.90 and1.25 units respectively across
15 cross-sections. The earlier nominal2.6–3.2 fringe estimates described the
geometry envelope and overstated its visible coverage. Matching vanilla would
mean roughly4 units of visibly substantial gravel per side with a broad soft
fade to12–14 units, while retaining the15-unit tarmac. The initial check left the
underlay unchanged; the subsequent applied correction above supersedes that state.

`Classical_Current_Modern_Overlay.png` compares actual current tarmac coverage
with the complete classical underlay at equal world scale. All five exit
centerlines/endpoints remain within0.0001 units of their classical anchors.
It shows the intentional internal rerouting; it does not depict proposed wider
shoulders or prove placed-building clearance.

The reusable `elbow30` cell is now in both512px atlas pages at pixel rectangle
(400,184)–(504,240), with42×26 world-unit cards, centerline radius60 and30-degree
heading change. B/FOW/H were inverse-UV baked from existing straight-road paint;
all pre-existing cell pixels are unchanged. H coverage matches B through all
ten mip levels. Two editable masters in `modules/` and native DecalGeometry
identities `CSC_Road_Elbow30_Industrial` / `CSC_Road_Elbow30_Modern` are installed
for AE. Their centreline endpoints are approximately(±15.53,-2.04), with tangents
±15 degrees. Rotate/translate in AE with uniform scale. Stone remainsZ0, tarmacZ1.
The elbow currently uses the existing CSC shoulder treatment, not the broader
measured target. No existing layout or AST was modified to place it.

New elbow native readbacks, saved-file checks, atlas preservation checks and an
isolated cook including the existing full layout passed. Ten installed files
(fourGEO/FGX and sixDDS) are verified in the browser cache. Measurement, comparison,
overlay and receipts: `Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout/vanilla-shoulder-calibration-20261029/`.
Tools: `calibrate_shoulders.py`, `classical_overlay.py`, `elbow30.py`.

### Vanilla modern width calibration — 29 October

Measured 45 cross-sections across 15 straight road meshes in the vanilla
Commercial Hub (`DIS_COM_Modern_Base_Decal_04`) and Campus
(`DIS_CMP_Modern_Base_03_Decal`). Native FGX coordinates and UVs map the actual
base-colour alpha coverage to world units. At 50% coverage the samples span
13.73–15.38 units, median15.09; transparent card margins are excluded.

CSC main roads now use nominal width15 (previously26), and the connector10.38
(previously18). Both stone and tarmac geometry contract across their widths;
route lengths, exit centerlines, roundabout center and Z0/Z1 layering stay fixed.
The existing painted atlases and corrected H coverage are byte-identical.
Stone fringe widths contract proportionally to about2.6–3.2 units. A 24×24 quad
grid lets the circle and its five mouths contract without scaling the layout;
the saved ring has625 vertices and no inverted triangles. Painted cell radii
in the atlas manifest remain texture-space authoring values, not current world
lane radii.

All21 saved masters passed validation. All20 native geometries were independently
decoded and cooked before installation;40 GEO/FGX files and their browser records
are updated. Mesh/group names and existing AST placement/visibility are retained.
The native converter aliased some material bindings; the scoped
`RepairRoadMaterials.cs` helper restores bindings from the prior FGX and registers
those materials at file level. Native readback alone missed the missing file-level
registration, which the first cook rejected; the corrected cook passed.

Tools: `calibrate_width.py`, `narrow_roads.py`. Evidence and the equal-scale
vanilla/before/after comparison are in
`Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout/vanilla-width-calibration-20261029/`.
No live AE/game visual confirmation or game deployment was performed.

Maintained tools: `project/tools/art/modern_roads/`:

1. `inspect_classical.py` through Blender: read-only live geometry snapshot/hash
   and measured centerlines.
2. `prepare.py` through Python: paired atlas pages, cell manifest and provenance.
3. `build.py` through Blender: layout, projection meshes, stage renders and checks.
4. `package.py` through Blender: separate module masters with explicit material
   bindings, saved-file validation and model descriptions.
5. `review.py` through Python: comparison boards and candidate DDS validation.
6. `coverage.py` through Python: equal-world-scale alpha overlay and exact external
   centerline/endpoint tests. Native decoded UV V is inverted back for this view.
7. Existing `modern_level2/native.py`, supplied with `CSC_LEVEL2_OUTPUT` and the
   comma-separated module IDs: CN6/FGX conversion and topology/UV/bone readback.

Evidence directory: `Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout/`.
It contains the source hash, atlas layout/provenance, fifteen saved-file reports,
fourteen module native checks, DDS validation, the classical alignment report,
stage boards and `Classical_Modern_Coverage_Overlay.png`.

## Asset Editor geometry/material installation — 29 October 2026

### Height-channel correction after native visual review

Henno's native screenshot showed the rectangular projection-card outline and
raised route margins. Inspection found our authored H maps had flat RGB128 and
nonzero alpha even where B was fully transparent: 168,294 Industrial pixels and
185,336 Modern pixels. Native Firaxis H maps instead have grayscale RGB relief
and coverage alpha closely matching B. This was a channel-generation error,
not evidence that the current UV layout required rebuilding.

`repair_height.py` now installs H RGB sampled from the same native crop and
coordinates as the paint (Industrial centers90–95, subdued painted fringe86–92;
Modern84–90). H alpha copies current B alpha exactly. The installed uncompressed
DDS coverage matches B at every one of ten mip levels, with zero error and zero
height coverage outside B coverage. RGB padding remains within the cell gutters;
coverage is not dilated. All B/FOW/S images, native FGX geometry, UVs and AE
assemblies are preserved. All21 saved Blender masters now use H Color for bump,
with explicit before/after export-geometry/UV/material-identity parity checks.

The current source folder is `3D Art/Decals/CSC_ALL_Modern_Roads`; source references
and active tool inputs were updated to follow Henno's move. Five private variant
assemblies pass SDK cooking with the corrected maps. Evidence and backups:
`height-channel-repair-20261029/` in the road output directory. This verifies the
map correction and cook, not an observed native visual result; the next AE/game
reload still needs visual confirmation. No live game package was deployed.

### Current handoff: five complete layout variants

Inspection of the live classical GEOs and Bakers ASTs confirmed five separate
geometry subsets with 38/41/45/48/52 meshes. Every included mesh is visible in
Worked; unused pieces are omitted from each geometry, not stored as hidden mesh
defaults. Visibility itself belongs to AST state rows. Variant01 hides its roads
in Construction; the other four referenced classical assets show their road
pieces in every inspected state.

The corresponding modern ready-to-use geometries are now installed and indexed:

| Geometry | Tarmac included | Meshes, including 7 stone underlay pieces |
|---|---|---:|
| `CSC_ALL_Modern_Base_01_Road_Decals` | None: all stone | 7 |
| `CSC_ALL_Modern_Base_02_Road_Decals` | Roundabout + NW + NE + SE | 11 |
| `CSC_ALL_Modern_Base_03_Road_Decals` | Initial tarmac + E | 12 |
| `CSC_ALL_Modern_Base_04_Road_Decals` | Initial tarmac + SW + lower Connector | 13 |
| `CSC_ALL_Modern_Base_05_Road_Decals` | All routes | 14 |

03 and 04 are independent destination combinations, not a required progression
through Stage3 before Stage4. Choose one geometry for the base variant, at zero
position/rotation and scale1; all included pieces should be visible. Their mesh
groups retain `CSC_Roads_Industrial_01` or `CSC_Roads_Modern_01`, so material names
match the installed materials. Individual pieces remain editable/selectable.
The source directory contains one matching `.blend`/`.cn6` per layout, with clean
Export and matching Review scenes. Existing district assemblies are unchanged.

Tool: `variants.py`. Evidence: `layout-variants-20261029/` under the road output
directory, including actual classical state/geometry inspection, saved-master
checks, exact approved geometry/UV/material parity, independent native readback,
isolated SDK cook, and browser-registration verification. The private cook ASTs
exercise the classical state conventions; they are not installed district bases.
Live AE/game visual review remains outstanding.

### Earlier all-pieces geometry, retained for custom layouts

`CSC_ALL_Modern_Base_Road_Decals` is still available as one all-pieces geometry.
Henno clarified that he wants the classical workflow: all pieces inside a single
layout geometry, each separately visible and mapped to its material. The combined
FGX/GEO is now installed and browser-indexed. Its fourteen named meshes retain
the exact approved shape, coordinates and UVs: seven `_Industrial` and seven
`_Modern` pieces. Their groups use the two materials below. Add this geometry
once at zero position/rotation and scale1, then toggle each mesh's visibility
in the asset state rows to create the desired variant.

Editable master: `3D Art/Decals/CSC_ALL_Modern_Base_Road_Decals.blend`.
Its Export scene contains all fourteen pieces; Review shows the first-building
proposal. The original module files are retained as sources, but adding fourteen
separate geometry instances is no longer the recommended assembly workflow.
`combined.py` builds the combined master from the saved modules and checks exact
geometry/UV/material parity. Saved-master validation, independent native
readback, private SDK cook and browser registration pass. Evidence is in
`draft-03-roundabout/combined-layout-20261029/`. Existing assemblies and materials
were preserved; native viewport/game appearance remains untested.

Henno requested the geometries and materials for a new district base that he will
assemble. `integrate.py` installed fourteen FGX/GEO pairs, two DecalMaterial MTLs,
and eight DDS/TEX pairs in CSC's conventional source folders. All 46 files are
registered in AssetCloud, with independently checked browser dependencies.

Search geometries for `CSC_Road_`. Each of `Roundabout`, `NW`, `NE`, `E`, `SE`,
`SW`, and `Connector` has `_Industrial` and `_Modern` versions. They retain
district coordinates: add with translation/rotation zero and uniform scale 1.
The current exported stone geometry is Z0 and tarmac Z1. Earlier Z20 notes were
incorrect for the installed geometry: inactive-scene transforms had not been
evaluated before export. Source masters now use the same Z0/Z1 coordinates.
Do not add a second per-surface offset in AE.

The 29 October Z-order update covers the seven tarmac modules, combined layout,
and variants 02–05 (twelve FGX files); stone-only exports remain unchanged.
All 21 saved Blender files passed validation. Independent native readback
verified the lift, unchanged XY/UV/topology/material identities and original
native vertex frames; isolated cooking and installed-file/cache checks passed.
Existing AST placements and visibility were preserved. Evidence is in
`Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout/tarmac-z-order-20261029/`.
The live AE/game rendering of the new separation still needs visual review.
Both versions have identical geometry/UVs and surface-specific group names.

| Material | Purpose |
|---|---|
| `CSC_Roads_Industrial_01` | Worn stone paving underlay |
| `CSC_Roads_Modern_01` | Tarmac with five pedestrian crossings |

Both materials bind BaseColor, Heightmap, FOWColor and Spec to their own 512px
atlas family, using native Decal texture classes. DDSs have ten levels including
the base level; native TEX convention records nine mip levels below the base.

Keep all seven Industrial pieces as the underlay. The first-building overlay is
Modern Roundabout + NW + NE + SE. Add E, SW and Connector according to the relevant
destinations; the review proposal enables Connector with SW. Configure normal
Worked/Unworked visibility in the new asset; visibility is an assembly setting,
not stored in these geometry files. Native layer ordering/projection should be
reviewed in the assembled district before finalizing it.

Fresh CN6 conversion and independent FGX readback checked all fourteen models'
topology, three UV channels, materials and single Bone binding. Texture pixels
match the approved source within one channel value. An isolated SDK cook of
private decal-only test assemblies passed. It reported empty obstruction boxes
for these decal-only test assets and solid Spec-map advisories; no missing
resources or error substitutions were reported. Private test ASTs/XLP and the
test BLP were not installed. Existing ASTs, ArtDefs and XLPs were left untouched.

Evidence: `draft-03-roundabout/ae-integration-20261029/`, including
`staging-validation.json`, `publication-report.json`,
`assetcloud-registration.json`, `final-verification.json` and `cook-check/`.
Asset Editor was closed during installation. Browser indexing and SDK cooking
are verified; live AE appearance, terrain projection, building clearance and
runtime activation remain untested. No game deployment was performed.
