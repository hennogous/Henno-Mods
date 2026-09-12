# Firaxis Market calibration — 2026-09-10

> **Documentation audit — 2026-09-12: Current.** Direct imported-model observations correct old Market UV coverage and blanket shading claims. Limits distinguish Blender approximation from FGX/runtime proof; still suitable as scoped calibration.
> Classification: Native asset study. See the [full audit](../../DOCUMENT-AUDIT.md).

> **AO interpretation corrected after the documentation review:** these are measured UV coordinates and source material bindings, not verified final runtime AO allocations. Asset-level AO may override material AO. Resolve the AST before assigning the measured footprint to a texture or concluding that an empty material AO slot means no AO. See [the guidance review](firaxis-guidance-review.md).

Direct inspection of Henno's supplied `Market.blend`, `DIS_COM_Base.mtl` and DDS/TEX
siblings gives a checked native reference. This is a Blender import, not independently
measured original FGX. Source files were left untouched.

The [full report](</Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/Dropzone/Codex/research/market-study/README.md>)
includes source hashes, raw JSON, scripts, packed study blend, map/UV sheets and
controlled material comparisons.

| Completed mesh measurement | Result |
|---|---|
| Vertices / triangles / assigned materials | 480 / 294 / 1; agrees with catalogs |
| Indexed components | 94 |
| Positional components at 0.001-unit quantization | 17; diagnostic, not an instruction to weld |
| Custom corner normals | Present; 36.85% differ from geometric face normals by >1° |
| UV1 triangle-covered union | 10.050% of shared atlas, with substantial overlap |
| UV2 triangle-covered union | 1.409%, no overlap detected at 1024-sample resolution |
| Supplied textures | B/N/A/G/M 1024²; E 512² |
| Declared formats | B/N/E RGBA8; A/G/M R8 |

Coverage measures triangle interiors, with full-square and duplicate-square checks.
The historical Market UV1 value of 3.0% is not valid covered area; see the
[analyzer audit](art-performance-evidence-review.md). These percentages describe one
mesh's use of shared atlases, not unused capacity in those atlases.

Additional construction-related meshes have 516 and 588 vertices; their actual
concurrent state membership needs AST inspection. Scene totals are not the completed
Market's runtime cost.

## Guidance changes

The clay/base-only/combined comparison shows geometry carrying the swept roof, thick
roof edge, structural members and stepped masses. Texture detail supplies window
recesses, crate boards and other small construction features. Base color already
contributes substantial local depth; normals reinforce aligned features. Increasing
normal strength alone would miss much of the Firaxis finish.

Independent UV2 allocation demonstrates reusable material patches alongside uniquely
mapped AO in another shared atlas. Neither a dedicated full-size AO texture nor this
particular tiny allocation is a universal requirement. Custom normals and positional
connectivity also contradict blanket flat-shading or splitting/welding rules. These
findings have been added to the skill's texture, geometry and performance references.

The Blender shader is an approximation: AO multiplies color, roughness=1−gloss,
daytime emissive is disabled. Both normal green-channel interpretations were rendered;
destination tangent/shader convention remains unverified. This is a qualitative
material study, not proof of in-game lighting parity or performance priorities.

Next useful evidence: matching AST/GEO/FGX and controlled reference view; other meshes
sharing this atlas to measure family allocation; masonry/curved assets to check
generality. Bottleneck rankings still require controlled game frame-time measurements.
