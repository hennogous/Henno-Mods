# Civ VI art: performance priorities and empirical calibration

> **Documentation audit — 2026-09-12: Current.** Explicitly corrects analyzer metrics and rejects an unmeasured engine bottleneck hierarchy. Consistent with later scoped native studies and current skill; no new runtime performance measurements were made.
> Classification: Evidence review. See the [full audit](../../DOCUMENT-AUDIT.md).

Follow-up: [direct Market inspection](firaxis-market-study.md) verifies its geometry
counts, replaces the old UV-coverage estimate and inspects actual corner normals.

Review date: 2026-09-10. Requested by Henno after the blacksmith trial and prior
art-architecture discussion. Pile-specific additions to the new skill are withdrawn;
the supplied conversation is retained unchanged. This review inspects existing
catalog reports and their available analysis code; it is not a fresh SDK census
or a game performance profile.

## What to optimize now

Use native-comparable geometry budgets and avoid unnecessary materials, texture sets,
transparency and duplicated resources. Optimize for readable art per unit of total
cost and authoring effort. Do not optimize solely for a vertex counter.

The earlier fixed hierarchy “materials dominate; vertices hardly matter” exceeds
the evidence. CPU submission, shader/pixel cost, geometry processing, memory pressure
and game simulation can dominate different workloads. Material discipline is a sound
default; it is not proof that materials are this game's current bottleneck.

General graphics evidence supports finding the limiting stage by controlled changes,
and recognizes both submission and geometry costs. It does not profile Civ VI for us:
[NVIDIA pipeline analysis](https://developer.nvidia.com/gpugems/gpugems/part-v-performance-and-practicalities/chapter-28-graphics-pipeline-performance),
[AMD performance guide](https://gpuopen.com/learn/unreal-engine-performance-guide/)
(the latter is an Unreal guide, not a Civ VI-specific source).

Working decisions:

- **Materials:** Avoid needless concurrent groups. Do not equate material definitions,
  groups and draw calls. Alternative E/NE states are not simultaneous solely because
  both definitions exist. Shadow and other passes affect submissions.
- **Textures:** Reuse by appropriate family, preserve mipmaps, inspect actual cooked
  formats and avoid large unique maps for tiny props. A single enormous atlas is not
  automatically superior: occupancy, residency and useful texel density matter.
- **Geometry:** Keep meaningful silhouettes and lighting geometry; remove redundant
  or genuinely invisible detail when safe. The blacksmith's 1,491 vertices are within
  the reported native range, but per-instance geometry is multiplied by repetition
  and potentially by passes. Vertices are neither free nor always the limiting cost.
- **Asset definitions:** Track capacity/compatibility separately from frame cost.
  Another mod's count does not establish a universal safe threshold.
- **LODs:** Potentially useful, but the reviewed catalogs do not document actual
  building LOD chains or switching behavior. “LODs are the only useful vertex
  optimization” is unsupported.
- **Reuse:** Saves resource duplication where actually shared. Identical references
  and shared materials do not prove hardware instancing or automatic batching.

## What the catalogs support

Sources: [complete building catalog](building-geometry-catalogue.md),
[condensed catalog](geometry-catalogue.md),
[detailed patterns](building-geometry-patterns.md), and
[condensed patterns](geometry-patterns.md). These largely repeat one investigation;
they are not four independent confirmations. Their provenance states .geo metadata
plus CN6/Blender inspection of selected assets.

| Example | Reported vertices | Reported triangles | Implication |
|---|---:|---:|---|
| Market | 480 | 294 | Very economical native designs exist |
| Workshop | 1,002 | 519 | Useful comparison for a production building |
| Stable | 1,322 | 663 | Blacksmith's cost is comparable in order of magnitude |
| University | 2,742 | 1,478 | One tiny budget does not cover every building |
| Modern Granary | 4,022 | 2,170 | A categorical 3,000-vertex ceiling contradicts reported assets |

Blacksmith: measured 1,491 CN6 vertices / 781 triangles; Henno confirms 1,491 in
Blender and Asset Editor. This is predictable and plausible relative to the catalog,
not a direct performance equivalence to the native Workshop (different composition).

The catalog labels `m` as mesh objects, not material count. Cathedral has 12 meshes,
Factory 3 and Ancient Granary 5. Therefore “the game only supports one mesh” is not
a general engine rule; the one-mesh/one-material workflow is our convenient default.
Material/pass cost needs the actual groups and AST state bindings, not the `m` column.

Era progression is explicitly nonuniform: Workshop 1,002 → 655, Granary 2,868 → 4,022,
and Lighthouse 812 → 824. Budgets should follow architectural form and asset role,
not an automatic percentage increase per era.

## Findings that weaken existing numerical rules

The reports link `building-mesh-analysis.json` and `geo-stats-all.tsv`; neither is at
the linked location in this checkout. The available inspector is
[`inspect_building_mesh.py`](../../../tools/scripts/inspect_building_mesh.py). Its current
behavior does not establish that every historical run used exactly this version.
It nevertheless exposes important problems to resolve before repeating the study.

### UV utilization is not occupied area

`analyze_uvs` marks 64×64 cells containing UV **vertices**. It does not rasterize UV
triangles. Executing the unchanged function on two triangles covering the whole
texture produces **0.1% utilization despite actual coverage of 100%**. UVs outside
0–1 are clamped for this metric, not measured according to actual sampler wrapping.

Consequently the reported “2–8%” cannot justify packing 12–50 buildings per atlas,
per-building pixel budgets or claims about texel density. The overlap test counts
duplicate coordinates, not overlapping triangle interiors. Neither proves UV2 validity.

### The shading metric does not measure shading

The inspector calculates geometric face normals from positions, then interprets
the number of distinct directions as hard/smooth shading. That quantity is unchanged
when the same geometry switches between flat and smooth vertex normals. Compare
stored corner normals across geometrically adjacent faces instead. The mere presence
of explicit normal fields does not prove artist-authored custom normal editing.

### Parser and aggregation need attention

The available CN6 parser skips the `materials` marker but not the material-name lines.
On the valid blacksmith file it reports **zero vertices**, where the file contains
1,491. The diagnostic executed its unchanged parsing function outside Blender.
Its bone field interpretation also differs from the current exporter's eight
indices/eight weights layout. Treat old bone-weight conclusions as requiring recheck.

Some summary rows mix whole-asset vertex totals with main-mesh island statistics:
2,868 / 526 is approximately 5.45, not the Ancient Granary row's 4.4. The detailed
patterns identify Cathedral main mesh as 1,796 vertices / 410 islands (~4.38), while
the summary uses 2,216 total vertices with the same islands and average. Compare
like scopes before deriving rules. Preserve source reports; do not invent corrected
raw measurements from these inconsistencies.

Disconnected indexed patches may result from export seams. They support using simple
surface patches where appropriate, but cannot prove original source topology or that
all walls lack backs. Several instructions are also plainly overgeneralized: “never
flat roofs,” “tall/narrow beats squat,” and “foundations are hidden” need era, shape
and terrain context. The native catalog itself contains broad low buildings.

Diagnostics: [`inspector-diagnostics.json`](../../../../output/art-guidance-review/inspector-diagnostics.json).
These test the measurement procedure, not Firaxis source meshes. No profiling or
complete analyzer repair was performed during this review.

## Investigations with the highest return

Start with a small identifiable sample: native Market, Workshop, Stable, Lighthouse,
Granary and one relevant cultural/era variant, plus the blacksmith as a control.
Preserve source hashes, conversion versions, mesh/material/state scope and raw results.

| Priority / question | Measurement or controlled comparison | Guidance it would calibrate |
|---|---|---|
| 1. What creates the native surface read? | Under matched light, compare full material, B-only, neutral color+N, AO off/on and controlled gloss; inspect roof/stone/wood crops at game scale | How much detail/shading to request in B; where N/AO/gloss should carry the result |
| 2. How much texture detail is actually allocated? | Actual DDS dimensions/formats/mips, triangle-area coverage and overlap, material sampler addressing, texels per world unit and per screen pixel; identify cross-asset reuse | Atlas size/sharing, generated tile/course size, padding, useful grain frequency |
| 3. How are normals and geometry used? | Compare geometric adjacency before/after positional matching, exported corner normals/tangent signs and UV seams; inspect shapes in clay | Hard/smooth choices, bevels versus normal maps, economical export topology |
| 4. What proportions survive the camera? | Standardized game-scale views and rotations; measure roof/body, beam/roof, chimney/house ratios within architectural families, plus silhouette changes | Replace rigid invented ratios with reference ranges and useful exceptions |
| 5. What actually costs frame time? | Same save/camera/settings/backend, warm runs; vary geometry alone, material groups alone, texture resolution alone and visible instance count; measure CPU/GPU frame time and memory | Whether geometry, submission, shading or residency deserves optimization in our target scene |
| 6. What changes with distance, terrain and state? | Inspect real LOD definitions/transitions, foundation visibility on hills, shadow geometry, worked/unworked and construction/pillaged bindings, snow/FOW where applicable | Safe hidden-face removal, foundation depth, LOD value and state budgets |

The performance experiment needs enough repeated content to exceed measurement noise,
but retain a representative normal view as well as a stress view. Keep total triangles
fixed when isolating material groups, preserve appearance where possible, and report
warm-run medians/spread rather than a single FPS sample. Separate render time from
turn-processing performance. Do not optimize game simulation through mesh edits.

Before these tests, repair or replace the analyzer with fixtures for known UV area,
overlap, hard/smooth normals, material lists and bone layout. Then recollect a small
sample before scaling to a full catalog. Of the new art studies, matched-material
comparisons and real texel-density measurement are the most immediate priorities
for improving texture image-generation directives.
