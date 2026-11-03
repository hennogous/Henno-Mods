# Quarter emissive atlases and reusable interiors

Implemented 28 October 2026 for Bakers. Henno requested lighter daytime interiors,
soft nighttime room lighting, and reusable UV3 coordinates with different painted
interior scenes per Quarter. His discussion of brighter Service-active textures
was explicitly deferred. No Service variants or bindings were added.

## Source libraries and runtime bindings

Under `Working Files/3D Art/Textures/CSC_Buildings_Emissive`, edit the PNGs in
`Current/textures`; `CURRENT.json` identifies the immutable release. Initial
release is `2026-10-28_Emissive_r001`. Keep the layout in
`Current/atlas-plan.json` and source copies under `sources/published-registered`.
The rebuild script restores those registered copies; update them when publishing
approved painted edits. Never edit an old immutable release.

| Family | Paintable PNG / runtime texture stem | Size | Materials |
|---|---|---|---|
| Historical Bakers | `CSC_Atlas_E_BAKERS` | 256² | `CSC_BAKERS_E`, `CSC_BAKERS_E_2` |
| Modern Bakers | `CSC_Atlas_Modern_E_BAKERS` | 512² | `CSC_BAKERS_Modern`, `CSC_BAKERS_Modern_2` |

These are two era families per Quarter, not per building. Additional Quarters get
their own painted E maps when their buildings are implemented. They reuse the
applicable era's geometry/UV3 layout. Historical and modern layouts need not be
identical. Historical Bakers starts as an exact copy of its effective installed
DDS; its mesh coordinates and lighting are unchanged. The source historical DDS
on Desktop differed from the installed DDS, so it was not used for migration.
Old shared `CSC_Atlas_E` and `CSC_Atlas_Modern_E` remain compatibility maps for
unmigrated consumers. Non-emissive historical materials remain non-emissive.

The `_2` material suffix is a colour variant here, not a Service lighting variant.
Its light-roof B texture was left untouched. No new active/inactive E pair exists.

## Modern UV3 allocation

The modern 512² E map has four 256² quadrants: Stage 2 top left, Stage 3 top right,
Stage 4 bottom left, storage bottom right. Each quadrant contains a 4×4 grid of
64² cells, numbered row-major from zero with top-left image origin. Room UVs use
a two-pixel inset and 60×60 content. This is independent of the 1024² B atlas.

| Local cells | Purpose |
|---|---|
| 0–7 | Existing façade/window locations; Stage 2 upstairs uses 7, Stage 3 upstairs uses 5 |
| 8 | Room A rear scene |
| 9 | Room A side walls / ceiling |
| 10 | Room A floor |
| 11 | Reserved room A detail |
| 12 | Black sentinel — never paint |
| 13–15 | Reserved room B rear, sides and floor |

Keep the existing global dark coordinate `(0.02, 0.02)` black. It falls in the
bottom-left quadrant's cell 12. Do not fill unused cells casually: other geometry
may deliberately sample black there. Before allocating further cells, audit
the consumers' UV3 and preserve occupied window pixels.

The Bakery's three recessed room boxes share Stage 3 cells 8, 9 and 10. Their
B cells remain 11, 12 and 15. Glass and frames retain black UV3; room surfaces
emit behind them. Changing the Quarter's room artwork should not require moving
UV3. Additional rooms can use the reserved second room set.

## Daytime and nighttime treatment

Day readability comes from lighter painted B: cream plaster, pale honey shelves,
light sage tile and pale oak flooring. ImageGen repainted only three interior
cells. All exterior pixels, including Henno's edits, were preserved exactly.
This is building library release `2026-10-28_Modern_r013`; props remain r007.

E preserves the room's painted colours and shapes at lower resolution. Initial
linear radiance scales are 0.12 for walls and 0.055 for floor, with a slight
0.35-pixel softening before padding. These are authored starting values, not
calibrated native-engine brightness. Existing upstairs window values are retained.
The shader's `Emissive_Minimum_Weight` remains unchanged; no always-on day emission
was introduced. Judge daytime B with E disabled. Normal historical/modern
comparison renders still exclude emissive unless explicitly requested.

## Updated masters and verification

Source paths remain:

- `Level 2/modern/revision-06-ae/CSC_Level_2_Modern.blend`
- `BAKERS/Bakery/modern/revision-04-ae/CSC_BAKERS_Bakery_Modern_Review.blend`
- `BAKERS/Bakery/modern/revision-04-ae/CSC_BAKERS_Bakery_Modern_2_Review.blend`

These are already registered to historical district coordinates. Do not reapply
the registration transform. Only 60 native vertex UV3 values changed. Native
positions, normals, tangents, UV1, UV2, topology and weights match the previous
export; AO was not rebaked because geometry and UV2 did not change. Saved-file
validation passed for all three updated Blender files.

The runtime update changes one FGX, B DDS, two E DDS/TEX pairs and four material
E references. Existing GEO, AST, ArtDefs and XLPs are preserved. Four new texture
content entries were added to ModBuddy. Asset Editor was closed, so its dependency
cache was updated with a backup; opening the browser should find the new maps.

Isolated SDK cook passed without error entities. Saved-AST daytime and explicit
night previews were visually reviewed. Native viewport/night intensity and
in-game results remain a human review; nothing was deployed to the game.

Evidence, backups and attached review images:
`Desktop/Codex/modern-interior-lighting-20261028`.
Maintained scripts: `project/tools/art/modern_bakery/interior_lighting_*.py`.

## Modern props: oven lighting

The modern props library now publishes `2026-10-28_Modern_r008`. Its existing
`CSC_Props_Modern_01_E` binding has expanded from a black16² placeholder to256²,
using the same normalized8×8 grid as B. Cell26 contains only the two warm oven
cavities, derived from the approved painted oven-front artwork with registered
masks; handles, controls and metal remain black. All other cells stay black.
Reserve cell56 around dark UV `(0.02,0.02)`; future prop lighting must audit UV3
consumers before allocating additional cells. This shared props atlas is separate
from the two building-era families above.

Only the oven front's four exported UV3 vertices changed. Its editable master and
both optional Bakery review blends were updated; AO, geometry, other maps and AE
placements were preserved. Seventeen other shared-material geometry consumers
were checked clear of cell26. Saved-file/native checks and isolated cook passed;
day/night previews were reviewed. Engine brightness remains uncalibrated.
Evidence: `Desktop/Codex/modern-oven-emissive-20261028`; maintained recipe:
`project/tools/art/modern_bakery/oven_emissive.py`.

Oven glass correction: props release `2026-10-28_Modern_r009` supersedes r008.
Both complete panes now receive a warm radiance floor, with lighter bread detail
on top; emission no longer follows mainly the bright bread pixels. Frames and
handles remain dark. Cell26 alone changed; geometry, UVs and placements are
unchanged. Recipe: `oven_glass_emissive.py`; evidence:
`Desktop/Codex/modern-oven-glass-emissive-20261028`.

## Dedicated interior family — candidate, 29 October

The Garden Café first version separates room paintings from exterior materials:
`CSC_Interiors_Modern_B_BAKERS` and `CSC_Interiors_Modern_N` at 1024², plus
`CSC_Interiors_Modern_E_BAKERS` at 512². Same normalized 4×4 cells in UV1/UV3:
Bakery rear/side/floor 0/1/2; Café rear/side/floor 4/5/6. Exterior upper-window
E and the props oven E remain as documented above. No Service changes.

This is a candidate library and migrated source copies, not a runtime release;
do not remove the old room cells until installing all affected consumers.
Sources and verification: [Modern Café first version](modern-cafe-first-version.md).
