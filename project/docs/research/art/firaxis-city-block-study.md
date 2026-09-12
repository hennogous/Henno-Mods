# DIS_CTY_AB city block patterns — 2026-09-10

> **Documentation audit — 2026-09-12: Current.** Explicitly scopes block-scale counts, mixed texture dimensions and unresolved AO bindings. Supports flat terraces without imposing a universal roof rule; not a single-building budget or performance profile.
> Classification: Native asset study. See the [full audit](../../DOCUMENT-AUDIT.md).

> **AO interpretation corrected after the documentation review:** these are measured UV coordinates and source material bindings, not verified final runtime AO allocations. Asset-level AO may override material AO. Resolve the AST before assigning the measured footprint to a texture or concluding that an empty material AO slot means no AO. See [the guidance review](firaxis-guidance-review.md).

Direct CN6 and DDS/TEX analysis. [Full report and review artifacts](</Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/Dropzone/Codex/research/city-block-study/README.md>)
include a packed study blend, clay/base/combined previews, maps, raw data and scripts.
Original files were not changed.

The architectural mesh has 4,298 vertices/2,405 triangles and one material reference;
a separate ground mesh has 6 vertices/2 triangles and another material. This is a
neighbourhood of structures and props, not a single building budget. No draw-call or
automatic batching conclusion follows from the reference counts.

The visible pattern is a limited vocabulary of boxes, stepped heights, thick parapets,
projecting beams and dome caps, with variations in proportion and arrangement. The
atlas similarly reuses two related wall treatments, trim and small material patches.
Warm/pale plaster and turquoise accents provide identity. Broad calm color fields,
small dark openings and selective exposed masonry produce a quiet, graphic painterly
finish. Geometry carries depth/silhouette while aligned maps supply much surface detail.

B/N/G are **1024×512**, AO **1024×1024**, E **512×512**. Do not require square or
identically sized maps by default. Main UV2 occupies **4.75884%** of the unit square by
analytical triangle area, with no positive-area intersections above 1e-12 UV-square
units. The supplied base A texture is not verified as this block’s effective AO. Cross-block reuse is unmeasured. Padding/filtering is not covered by this test.

Indexed components number 956 (780 have four vertices), but diagnostic positional
grouping gives 152 components. About 47.47% of supplied corner normals differ from
triangle face normals by >1°. Neither the component count nor simple geometry implies
uniform flat shading or proves the original artist's kit construction method.

The block supports a hybrid approach: parameterized primitives for varied large forms,
and a compact reusable texture vocabulary for surface detail. Flat terraces and
stepped massing are valid art-direction choices; do not force swept roofs everywhere.
These shape and per-map dimension lessons were added to the art skill.

Limits: MTL bindings are unresolved; preview map roles follow TEX classes. Ground is
omitted, metalness is a neutral default, emissive is off and the shader/tangent basis
is a Blender approximation. UV1 has 52 out-of-bounds triangles and UV3 extensive excursions;
clipped UV coverage cannot establish wrapped sampling or emissive behavior. Main UV2
is in bounds and unaffected. No new polygon limit, cultural attribution, manual-mip
practice or measured engine performance hierarchy is inferred.
