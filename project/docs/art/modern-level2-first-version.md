# Modern Level 2 base — first authoring version

## Current: revision 06, installed AE masters

Current main and workshop: `Level 2/modern/revision-06-ae`. They include Henno's
final v3 bargeboard edits and refreshed building AO, registered rigidly to the
historical district coordinates. Do not reapply the old centred-review transform.
Runtime identities: `CSC_Level_2_Modern`, `CSC_Level_2_Modern_Workshop`.
Buildings atlas r012 retains Henno's later L1 B edit and restores the new Bakery
artwork into its previously empty quadrant; props r007 includes
the Bakery/decor cells. Main native output is 1090 vertices / 588 triangles after
omitting four zero-area tessellation triangles. Editable source faces are retained.

The reusable main asset and Bakery reuse historical L2 CON+PIL for now. This is
not a modern state-shell retake. Native conversion, state/dependency inspection
and isolated cook pass; live opacity and terrain remain untested. See
[Bakery installation](modern-bakery-first-version.md) for evidence and limits.

## Previous: revision 05, historical height and window-depth trial

Current masters are in `Level 2/modern/revision-05-height-interiors` under the
Working Files 3D Art folder. They derive from Henno's edited Bakery `_2` review
scene, preserving the moved dormers and chimney. The ridge now matches the
historical maximum of 109.044 source units; the upper wall band and roof are
lowered by 3.956. Foundations, ground floor and short shelter footprint remain.
Eaves are closed, crossing beam ends corrected, and the sign is lowered to its
historical plaque-bottom height (35.328). Building AO has been rebaked without
the viewport-hidden historical reference contributing to the bake.

The ground windows and door include an experimental painted room-box interior
with real apertures, a gap and opacity/gloss glass. These are Bakery palette
artwork in candidate Stage 3 cells 11/12/15; the geometry remains reusable.
Upper E treatment is unchanged. Native building opacity coverage has not been
visually verified: this remains an authoring trial, with no AE/atlas publication.
Main exports 1090 vertices/592 triangles; workshop stays 544/272. See
[Bakery v3](modern-bakery-first-version.md) for the complete provenance and limits.

## Previous: revision 04, Bakery concept C corrections

The current reusable masters and review scene are in
`Working Files/3D Art/Level 2/modern/revision-04-bakery-corrections`.
Henno selected Bakery concept C and authorized its associated corrections.
The approved main envelope is retained; two upper windows on the left-facing
long facade are restored and all three dormers use compact faces/thinner caps.
Ground glazing has warm B artwork, while UV3/E adds upper windows only.
The forward shelter now ends ten source units past the front-wall corner,
at Y=-19, removing the long side/back strip. Complete supports and buried
foundations remain; the changed building and workshop have fresh isolated AO.

Main and workshop are separate editable masters, 914 and 544 exported vertices.
Saved-file and native round-trip validation pass. The combined reusable review
keeps flower boxes and a blank pointed hex sign. Candidate textures are portable
beside the masters; no published atlas, AE or runtime changes were made.
See [Bakery v2](modern-bakery-first-version.md) for placements, atlas allocations
and verification limits. Earlier revisions below are preserved history;
their blank-long-wall and concepts-first instructions are superseded.

## Earlier review correction — 28 October 2026

Henno reports missing upper-storey windows on the left-facing long facade in BOTH
the reusable L2 and Bakery. Restore these in the next selected revision; the earlier
blank-long-wall interpretation below is superseded. Refine the dormers toward the
original Bakery concept. Ground-floor windows need warm lit-looking B artwork;
E adds upstairs lighting as in the historical treatment. Bakery extension/oven
layouts are undergoing concept exploration before any new 3D edits.
See `modern-bakery-first-version.md` for the full current review brief.

## Historical openings and reusable details — revision 03

Current review source: `Level 2/modern/revision-03-window-boxes-sign/CSC_Level_2_Modern_Review.blend`.
The main and workshop remain separate masters beside it. The workshop footprint
from revision 02 is unchanged. Main proportions and the primary roof shape remain;
the requested rear dormer has been restored opposite the chimney.

The historical `Level 2/CSC_Level_2.blend` was rendered from all four elevations
to verify the wall openings. Both long upper walls are blank. Both gable ends have
one central upstairs window. The east ground floor has an entrance door and one
smaller window; the west ground floor is blank. The rear has one offset ground
window. Added shopfront and attic openings from the concept trial were removed.
The shelter conflict is therefore gone. Gable upstairs windows are now 20 wide by
22 high, rather than 26 by 20, so the painted frames are not stretched sideways.

Independent reusable masters live under `Props/Modern/revision-01-architectural-details`:

- `CSC_ALL_Window_Box_Modern.blend`: green box with painted foliage and ivory/yellow
  flowers. Reused under both upstairs gable windows at uniform 0.8 scale and under
  the rear ground window at uniform 0.6 scale in the review proposal.
- `CSC_ALL_Hanging_Sign_Modern.blend`: iron bracket and blank framed hexagonal
  plaque. **Points at top and bottom**, matching the historical sign. The blank
  painted face is reusable for later Quarter-specific artwork.

The modern building atlas Stage 3 artwork occupies the top-right quadrant. Updated
portable sources are in the building master folder's `building-atlas-candidate`.
New flower/sign artwork occupies adjacent props cells 24 and 25, with existing
green timber and iron reused. Its portable sources are under the prop folder's
`props-atlas-candidate`. Both are authoring candidates; published Current remains
buildings r007 / props r004, and no AE or runtime installation was performed.
Reserve these candidate cells when extending this work rather than reallocating them.

All four saved masters have matching CN6 exports and saved-file/native validation.
Main AO was rebaked for the rear dormer and revised opening layout; props have
independent AO. B-only and neutral normals off/on under two lights were inspected
for the new props. Existing building regions and existing props surface cells
are preserved; new prop DDS surface pixels round-trip exactly. These checks do
not establish live AE or in-game appearance. Comparison renders omit emission.
Evidence: `Desktop/Codex/modern-level2-v3-details-20261028`.

## Extension-only variant — 28 October 2026

`Level 2/modern/revision-02-tailor-footprint` contains a proposed replacement
workshop, plus the unchanged main master and a combined `CSC_Level_2_Modern_Review.blend`.
The user explicitly retained the main building and asked for the historical
Tailor's forward-projecting lean-to relationship, with a modest side/back return.
The modern building should remain recognisably an update of that historical kit.

The forward bay projects 36 units from the front wall. A 12-unit-wide side strip
continues to an 8-unit-deep rear return. Painted surfaces and their scale are reused;
the new module has its own rebaked AO and underground foundations. The extension is
780 exported vertices / 390 triangles. Main geometry, UVs, bindings, surface maps
and main AO were compared with version 1 and are unchanged (896 vertices / 456 triangles).
Saved-file validation and native topology/UV/binding checks pass. Front, rear and
top renders were inspected; comparison images omit emission. This is an authoring
variant, not an AE installation or a promoted shared-atlas release.

Evidence: `Desktop/Codex/modern-level2-v2-footprint-20261028`.
The initial shortened-main experiment was discarded after the user's clarification;
none of its geometry is in the delivered variant.

Created 28 October 2026 for Henno's request to follow the approved Bakery concept
as a visual specification. This is a reusable architectural kit, before Bakery
equipment, bread display, awning, sign, flowers and paving are assembled.

## Authoritative inputs

- Visual specification: `C:\Users\Shadow\Desktop\Codex\bakery-modern-concept-20261026\Bakery_Modern_Sheltered_Dispatch_Concept.png`.
- Historical scale reference: `Working Files\3D Art\Level 2\CSC_Level_2.blend`.
- Painting treatment: Firaxis `DIS_COM_Base_B.dds`; the concept supplies the palette.
- Shared atlas baseline: buildings r007; existing mill allocations are preserved.

The concept's swept roof, two shed dormers, substantial cream roof trim, warm brick
upper storey, slate-coloured lower walls and green shopfront frames are explicit
design constraints. Rear details are extrapolated. Roof seams, masonry joints,
window frames and grain are painted/normal detail rather than individual meshes.
Geometry supplies roof curvature and thickness, dormer bodies, chimney and the
open workshop interior. Foundations extend to Z=-30 and are clipped only in renders.

## Editable masters

Folder: `C:\Users\Shadow\Desktop\Working Files\3D Art\Level 2\modern\revision-01-concept-base`.

| File | Role | Exported vertices | Triangles |
|---|---|---:|---:|
| `CSC_Level_2_Modern.blend` | Reusable main building | 896 | 456 |
| `CSC_Level_2_Modern_Workshop.blend` | Separate open workshop shell in the proposed relative position | 528 | 264 |

Both have Review and Export scenes, three UV channels, one static bone, portable
external textures and matching CN6 exports. The total architectural proposal is
1,424 exported vertices / 720 triangles, after UV2 seams. It contains no bakery props.
The separate workshop preserves the proposed relative placement; AE owns eventual
assembly and may place/reuse it independently.

## Materials and review evidence

`atlas-candidate/` is a portable authoring candidate, **not shared Current**.
The Stage 3 top-right quadrant contains sixteen 128px surface cells on the 1024px
modern atlas. Existing Stage 2 pixels and the bottom half are preserved. Independent
AO allocations on the 2048px page are main [1024,0,1536,512] and workshop
[1536,0,1792,256]. Emissive remains 256px; all four upstairs panes are lit, and
ground-floor glazing is dark. Comparisons omit emission.

The candidate retains generated B artwork, projection/layout guide, the atlas plan,
registered full-page surface maps, editable structural height arrays and AO bakes.
ImageGen provided the painted colour sheet. Explicit measured joint, ridge and frame
profiles supply N; general colour contrast and paint wear do not become height noise.

Evidence root: `C:\Users\Shadow\Desktop\Codex\modern-level2-v1-20261028`.
Reviews include matched concept view, top/rear views, unlit B, neutral normals off/on
under two lights, registered B/height/N sheet and converted DDS materials. The first
pass exposed reversed roof UV direction, inconsistent gable brick scale and a gap
under the workshop roof. Those were corrected; the sloped wall-cap UV scale was
also corrected without changing geometry or AO.
The direct concept comparison then showed masonry courses too large. Brick and
lower slate cells now repeat the painted source 2x2, with the height profiles repeated
and normals recalculated at that mapped scale. Geometry, UVs and AO are unchanged.

Saved-file validation has zero errors. Native FGX readback matches topology, all
three UV channels, weights and geometry within 0.000004 units. Converted surface
DDS top-level pixels match their PNG sources exactly. These are authoring/native
checks, not AE/game appearance acceptance. No live AST, ArtDef, XLP, runtime atlas
or shared library Current was changed. Construction/pillage and runtime integration
are outside this first architectural version.
