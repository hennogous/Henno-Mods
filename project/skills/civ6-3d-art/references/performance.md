# Performance and resource budgets

## Performance priorities

The aim is to control total rendering cost while preserving useful visual detail. At the modest geometry budgets demonstrated by the
blacksmith, do not make vertex minimization the overriding design objective.

| Resource | Working priority and decision |
|---|---|
| Concurrent materials/render groups | Avoid unnecessary additional bindings/groups, especially across many placements. Distinguish material definitions used in alternative states from materials active together. Exact draw calls also depend on passes and batching |
| Textures / memory | Reuse appropriate atlas families, use suitable resolutions/compression/mips, and avoid a new texture set for every small prop or variant. Include AO allocation in this planning |
| Repeated geometry and placements | Reuse resources where useful. Inspect the number of visible instances and their actual submission/culling behavior; do not assume sharing means automatic batching |
| Transparency / overdraw | Consider screen coverage and overlapping layers; cutout and blended materials have different behavior. Compare any geometry alternative against its actual cost and appearance |
| Unique registered assets | Track as a compatibility/capacity constraint for the intended mod stack. It is not interchangeable with placements, draw calls or a continuous measure of frame cost |
| Vertices / triangles | Stay within the brief and a sensible reference-based budget. At this scale, preserve important silhouette/depth before chasing small LOD0 reductions; consider repetition and distance/LODs when evaluating total geometry cost |

These are practical defaults, not a benchmark-derived universal ranking. Measure
the intended game view/mod stack before expensive optimization. A few extra vertices
can be a good trade if they improve a beam or roof without adding another material
or texture set. Conversely, a tiny prop can be costly when it introduces a separate
material, large textures or many submissions. Neither is literally free.

Examples of decisions to prefer:

- Keep the chunky bargeboard instead of flattening it merely to reduce a small count.
- Fit a new small wooden prop into an appropriate existing atlas/material when useful.
- Do not count E and NE state alternatives as simultaneous materials merely because
  both definitions exist; inspect how states are actually bound.
- Do not merge reused props into every building solely to chase an unsupported asset
  tally target; weigh duplicated resources and maintenance against any real benefit.

Count parity with Asset Editor is a **predictability check**. It lets us trust the
budget; it does not establish that this budget is the primary performance bottleneck.

## Evidence boundary

Native asset inventories establish examples and conventions, not which stage limits
frame time. A material definition is not a draw call. Separate simultaneous material
groups, shader/pass cost, unique texture residency, visible instance counts, geometry
cost and registered-asset capacity. Do not assert automatic instancing from references.

No fixed ranking is proven for Civ VI by our current catalog reports. Use material
and texture discipline as preventive design choices, reference-based geometry budgets
as guardrails, and controlled frame-time measurements for further optimization.
Texture sharing has tradeoffs: a larger shared atlas can load unrelated content and
reduce available texel density. Reuse by useful family, not a mandatory giant atlas.
The inspected catalogs do not establish building LOD coverage or switch distances;
verify actual LOD behavior before making LOD authoring the default optimization.

A direct inspection of the supplied Market import finds one completed mesh/material,
480 vertices and 294 triangles. Its UV1 covers about 10.05% of the shared 1K atlas,
with substantial overlap; UV2 covers about 1.41% of its separate 1K AO atlas, without
detected overlap at 1024-sample resolution. This demonstrates independent allocation
for reusable material detail and positional AO. A whole 1K AO map per small building
is not a native requirement; neither is this particular 1.41% allocation a target.
Scene totals also include construction meshes, so identify the measured state first.

The Library provides a useful counterexample to equating meshes with material groups:
one CN6 mesh has 999 vertices and 537 triangles, with two groups (campus surfaces:
843 vertices/445 triangles; foundation: 156/92). These groups match the supplied GEO.
Inspect group ranges and bindings even when an inventory reports one mesh. Count
texture coverage separately per material domain; foundation UVs do not describe use
of the campus atlas. Neither group count alone nor mesh count establishes draw calls.

The campus family demonstrates a useful default: reuse suitable material patches on
UV1 while allocating AO independently for each model/state within a shared AO atlas.
The intact, construction and pillaged Library and University have mutually disjoint
campus UV2 regions. Library CON/PIL share triangle indices, UV1 and supplied normals
(positions agree within 0.0001 source units), yet use separate AO texels. Identical
UV1 is therefore not evidence that variants should inherit the same AO. Reusing a
parent bake remains an explicit quality/budget tradeoff, not a native requirement.
Distinct AO regions in one bound map do not themselves require extra materials.

Budget states individually: this Library's CON/PIL geometry each totals 1,567 vertices
versus 999 intact, including a separate construction-prop mesh. A damaged or construction
state need not be cheaper. Actual state visibility still requires the AST/runtime.

Evaluate cost at the intended scale and repetition: modest per-building geometry can
multiply across cities and rendering passes. Preserve chunky silhouettes, but avoid
unseen redundant geometry and details that neither read nor improve lighting.

Treat named asset limits as a separate combined-content compatibility question.
Published counts for another mod do not establish a safe universal ceiling. Missing
assets can also result from registration, material or cook errors; diagnose them.

## Catalog measurements that need revalidation

The available historical inspector counts UV vertex-grid occupancy rather than
covered UV triangle area; its utilization percentages must not set atlas budgets.
It counts unique geometric face normals, which does not measure hard/smooth shading.
Disconnected imported patches do not prove the original source was authored as
floating quads. Compare exported corner attributes and geometric adjacency directly.
Keep whole-asset statistics separate from individual submesh statistics.
