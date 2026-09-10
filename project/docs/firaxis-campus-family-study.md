# Campus family: shared artwork, independent AO — 2026-09-10

Direct CN6 inspection of Library intact/CON/PIL and University, plus the supplied
campus and foundation material definitions. Full data, source hashes, scripts and
atlas plots are in the [study report](</Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/Dropzone/Codex/research/campus-family-study/README.md>).

**All four campus UV2 layouts are mutually disjoint inside the shared AO atlas.**
Triangle-intersection checks also find no positive-area overlaps within each layout.
This supports sharing material artwork while allocating positional shading independently.

| CN6 file | Vertices | Triangles | Meshes / material groups | Campus AO area |
|---|---:|---:|---|---:|
| Library intact | 999 | 537 | 1 / 2 | 2.079% |
| Library CON | 1,567 | 833 | 2 / 3 | 2.135% |
| Library PIL | 1,567 | 833 | 2 / 3 | 2.135% |
| University | 2,742 | 1,478 | 1 / 1 | 10.014% |

AO areas above are analytical triangle-area sums, justified as unions by pairwise
polygon-intersection checks (tolerance 1e-12 UV-square area). They avoid small raster
sampling errors in earlier coverage estimates. Together these campus groups occupy
16.364% of their AO atlas. Other assets can occupy the remaining area; this is not a
whole-atlas capacity census. Foundation and construction-prop groups are excluded
from campus UV measurements because they sample different material domains.

## Strongest comparison

CON and PIL corresponding meshes have identical triangle/group indices, UV1 and
normal/tangent/binormal arrays; positions agree within 0.0001 source units. Yet they
use separate UV2 regions. Shared geometry/artwork does not imply shared AO texels.
Skeletons and UV3 differ, so this is not proof of identical rendered/animated states,
or proof of how the original AO pixels were generated.

CON/PIL share exactly the same sampled campus material footprint, almost entirely
inside the intact Library footprint. Library/University share about 20.91% of the
Library's UV1 footprint, but none of its AO allocation. Packing is interleaved across
the atlas; a contiguous quadrant per building is not a demonstrated native rule.

## Foundation and implementation implications

Foundation_Modern_01 binds only its named B/N/G textures. AO, metalness, opacity,
LightMap and emissive are empty. The named DDS files are still unresolved; differently
named foundation textures were not substituted. Do not require AO bakes or AO UV
uniqueness on a material that does not sample AO.

Skill guidance now favors suitable shared UV1 patches and independent model/state AO
regions in a common map. This need not introduce a new material per variant. Reusing
a parent bake remains an explicit visual/budget compromise, not a Firaxis requirement.
State budgets also need measurement: these CON/PIL files are heavier than the intact
Library because they include a separate construction-prop mesh.

Limits: no AST/runtime state validation, no direct FGX decoding or performance profile.
Triangle non-overlap does not guarantee safe padding/filtering. PIL UV3 has large
out-of-range coordinates, and University UV1 has a small boundary excursion; unit-square
UV1/UV3 raster results do not resolve wrapping or emissive behavior. AO is in bounds
and unaffected. Per-surface texel priorities remain unmeasured; whole-atlas area alone
does not establish them. No custom mip authoring recommendation follows from this study.
