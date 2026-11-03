# Modern Bakery — Blender proposals

## Installed in AE — 28 October 2026

Installed: `CSC_BAKERS_Bakery_Modern` and `CSC_BAKERS_Bakery_Modern_2`.
The second retains the standard inventory and adds the delivery truck. Main and
shelter are direct geometry instances; oven, rack, trays, display, sign, flower
box and truck are separate assets, initially one copy each for AE placement.
All pre-existing ASTs are byte-identical to the installation baseline.

Input was Henno's **20:02 saved v3 delivery review**, including both bargeboard
fixes. The original is untouched. Building AO was rebaked in its existing UV2
allocation. Four zero-area gable tessellation triangles were omitted from native
output without changing visible surfaces or editable geometry. Main export:
1090 vertices / 588 triangles; workshop: 544 / 272.

Export masters: `3D Art/BAKERS/Bakery/modern/revision-04-ae` and
`3D Art/Level 2/modern/revision-06-ae`. These prepared building masters are rigidly
registered to the historical L2 district frame. Earlier reviews were centred.
`Desktop/Codex/modern-bakery-ae-20261028/registration.json` records the inverse
historical roof-frame normalization; **do not apply it twice**. Separate props
retain local pivots, with registered placements in the AST. AE now owns placement.

Canonical releases: buildings **2026-10-28_Modern_r012**, props
**2026-10-28_Modern_r007**. Buildings r010 retains the initial installation snapshot.
Henno edited shared B during publication and explicitly requested keeping it;
r011 preserves his exact PNG. His export still had a flat-grey, unpainted Bakery
quadrant; final r012 restores only that top-right quadrant from r010. Every RGBA
pixel outside it matches his edit exactly. Final DDS and portable snapshots use
that merged image. See `accepted-user-texture.json` and `human-texture-merge.json`.
New `CSC_Atlas_Modern_O` uses `Generic_OPAC` through `CSC_BAKERS_Modern`.
Props r007 also preserves Henno's subsequent colour edits to mill cells 0/1/9;
the Bakery cells are unchanged. His later `Wind_Mill_Modern_2.ast` save is outside
this installation and was left untouched. Final verification distinguishes that
later save from the 129 ASTs preserved at publication.

Modern Landmarks priorities 2/3 retain the existing Service SelectionRule for `_2`.
Buildings/GamePropertyRanges/SQL/Lua gates are unchanged; XLP entries are unique.
AssetCloud automatically indexed all new dependencies; no manual cache repair.
AE auto-reimported watched PNGs during publication. Timestamp-only TEX changes
and an unchanged companion DDS re-encoding were verified, backed up, and the
tested native DDS outputs installed.

Nine native round trips, saved-file checks, dependency/state checks, fixed-L2
saved-AST renders and the final isolated SDK cook pass. Existing historical L2
CON+PIL and building debris are reused for this first install: **a modern ruin and
construction kit has not been authored**. New custom props are hidden in
Construction/Pillaged/Unbuilt and use permanent culling. Historical prop debris
is disabled. Direct AE viewport access was denied by computer-use permissions;
native opacity appearance, terrain and live era/service switching remain untested.
No game deployment. Evidence/backups: `Desktop/Codex/modern-bakery-ae-20261028`.

## Prior authoring version 3, human-edited roof and interior experiment

The authoritative input is Henno's saved
`revision-02-concept-c/CSC_BAKERS_Bakery_Modern_2_Review.blend` (28 October,
19:29 local). Its moved dormers and chimney are retained; no earlier generator
was used to reconstruct them. The snapshot/hash and per-object checks live in
`Desktop/Codex/modern-bakery-v3-20261028`. The original input remains unchanged.

Current Bakery masters and standard/delivery review scenes are in
`Working Files/3D Art/BAKERS/Bakery/modern/revision-03-height-interiors`.
The corresponding reusable L2 building/workshop/review files are in
`Working Files/3D Art/Level 2/modern/revision-05-height-interiors`.
Prior versions are preserved. Human edits to these saved files take precedence
over generator scripts.

The historical shared L2 mesh measures 109.044 source units to its highest roof
ridge point. Modern ridge height is reduced from 113 to 109.044: the upper wall
band is shortened and the roof, dormers, chimney and high flower boxes lowered.
Dormer/shaft/cap shapes and their edited relative placement survive that rigid
lowering, verified against the source. The orphaned dark chimney-mouth card was
repositioned onto the moved cap. Ground floor, footprint, deep foundations and
the oven/rack/trays/truck/workshop remain unchanged. The sign plaque bottom is
lowered from 44 to the historical 35.328. Continuous fascia and soffit faces close
the eaves; gable crossbeams sit one unit lower to stop their ends penetrating the
roof surface and producing dark AO marks.

The bread display now has nine shallow sloped trays with painted round loaves,
baguettes, rolls and croissants. Three new ImageGen cells (props 36–38) have
explicit aligned loaf-height/scoring profiles and contact shadows transferred
into UV2 AO. Flour, seed colour and wear are not used as height. The display drops
from 612 to 432 exported vertices (660 to 216 triangles). The cabinet, canopy
and saved display placement are retained.

Ground-window experiment: actual wall apertures reveal open-front room boxes,
one source unit behind each frame, six units deep. Only their large faces are
geometry; shelves, bread, tools, tiles and floorboards are painted. Stage 3
building cells 11/12/15 hold back/side/floor artwork. Existing window/door frames
retain their registered relief. Cells 14/6 now use low opacity and high gloss
for glass, with opaque frames. Upper-floor glazing and E remain unchanged.

This is a **Blender trial**, not a verified glass shader for Civ VI. The documented
building `Generic_OPAC` path uses screen-door/MSAA coverage, not physical blended
refraction. The Cycles preview demonstrates the geometry/parallax idea; AE and
in-game opacity/ordering still need review. The inset version shows useful depth
but is darker and less immediately warm at game scale than the flat painted B.
The flat/depth board makes that tradeoff explicit; no emissive texture is used.

Building and display AO are freshly baked with B/N disconnected. Henno's imported
historical comparison mesh was hidden only in the viewport, so it is excluded
from render/bake rays and removed from the new published review copies; it remains
in his untouched original source. This matters because viewport hiding alone does
not exclude a mesh from Cycles AO. Saved masters and eight native round trips pass;
main 1090 vertices/592 triangles, workshop 544/272. Native geometry validation does
not validate the new opacity shader. No AE, runtime or canonical atlas publication.
The combined standard review contains 3552 exported vertices against the 2200
whole-scene advisory; the kit remains delivered as independent building/prop masters.
Pixel checks confirm no edits outside the allocated candidate atlas regions, and
the original human-edited source hash is unchanged.

Review evidence includes historical/modern at the same rigidly aligned camera,
ground datum and scale, front/rear/AO, flat/depth/two-angle window views, and display
B-only, combined, neutral normals on/off and two light directions. Full prompt,
guide, generated B, editable heights and B/height registration sheets are retained.

## Previous: version 2, concept C selected

Henno selected C on 28 October 2026 and authorized the recorded 3D corrections.
Current editable assembly: `Working Files/3D Art/BAKERS/Bakery/modern/revision-02-concept-c/CSC_BAKERS_Bakery_Modern_Review.blend`.
The adjacent `CSC_BAKERS_Bakery_Modern_2_Review.blend` adds the delivery truck;
standard baking and sales props remain. These are authoring proposals, not saved
AE assemblies. The previous version is preserved.

The main body and primary roof retain their approved dimensions. The long
side/rear workshop strip is removed: the forward shelter has a short return to
Y=-19, ten source units past the main front wall at Y=-29 (back wall Y=29).
The electric oven faces 45 degrees at (-34,-46), with the stacked bread trolley
at (-43,-59), both under the shelter. The small cream/green truck in `_2` is
at (-79,-64), with open rear doors facing the loading area. These placements are
review proposals; saved AE placements remain authoritative when integrated.

Two upper windows have been restored on the left-facing long facade. All three
dormers have narrower faces and thinner shed caps. Ground window/door glazing is
warm in the B artwork; UV3 remains black there. Upstairs and dormer UV3 sample
the existing emissive window cell. Review renders disable emission.

Reusable building and workshop masters now live in
`Working Files/3D Art/Level 2/modern/revision-04-bakery-corrections`.
Separate Bakery prop masters include the truck, oven, display, bread rack, trays
and pointed hexagonal sign. Saved masters take precedence after human edits;
do not rerun the source generators over them automatically.

Candidate textures retain the existing modern libraries. New ImageGen truck
surfaces occupy props cells 32–35 (front, cab side, cargo panel, tyre/hub).
Building Stage 3 cell 14 supplies warm ground windows; cell 6 keeps its existing
door frame with new warm panes. Relief is registered to these surfaces and
computed at the actual sampling resolution. Building/workshop/truck AO was
rebaked with B and N disconnected; timber grain follows the beam length.
Portable candidate PNGs and provenance are beside the masters. Published atlas
libraries, AE, ArtDefs and runtime files have not been changed.

Saved-file validators pass for the eight masters and both assemblies. Native
FGX round trips pass for geometry, normals, tangent frames, UV1/2/3, topology
and weights (maximum component error below 0.000004). Export vertex/triangle
counts: main 914/466; shelter 544/272; truck 822/628; oven 236/132;
display 612/660; rack 602/496; trays 120/60; sign 132/68.

Evidence: `Desktop/Codex/modern-bakery-v2-20261028`. The historical reference
uses the shared L2 main and Tailor lean-to. Its fitted roof-frame footprint is
reference evidence only, not a verified native assembly comparison. The v2
overhead review establishes removal of the long rear strip; exact historical
footprint parity, road clearance and in-game scale remain unverified.

Final visual review checked the standard/delivery front views, rear, overhead,
full-scene AO, truck base colour and neutral normal views from two light directions,
and the reusable L2 assembly. Overlapping exterior masonry faces on the short return
were removed before the final AO bake. A pixel comparison confirms zero changes
outside the allocated candidate atlas rectangles. The small E map is unchanged;
all four upstairs pane centres are non-black, with ground UV3 sampling black.
Review boards: `Bakery_V2_Standard_and_Delivery.png` and
`Bakery_V2_Footprint_Comparison.png` in the evidence folder.

## Previous version and concept exploration

## Earlier review direction — concepts before further modeling

Henno's review of this first version supersedes the earlier instruction treating
the long upper wall as blank. Record these corrections for BOTH the reusable L2
master and Bakery derivative; do not implement them until the next concept layout
has been reviewed:

- Restore the missing upper-storey windows on the left-facing long facade.
- Bring both models' dormers closer to the original Bakery concept: compact,
  integrated shed dormers with the concept's window/cheek proportions and roof caps.
- Ground-floor glazing should already look warmly lit in B. E adds the upstairs
  lighting, following the historical treatment; ground-floor warmth must not depend
  on emission. Concept daylight should show warm ground panes without bloom.
- Work-area placement is not approved. Explore an oven front rotated 45 degrees
  to the building, or facing the same direction as the front entrance. Reshaping
  the low extension is allowed if needed; keep the main building recognisable.
- The `_2` version adds a small Bakery delivery truck loading bread for the
  adjacent Market. Retain the standard baking/sales scene and add the delivery
  activity. A compact cream/green van is a concept proposal, not an approved model.
- Produce several concept alternatives first. No mesh, UV, atlas or AE changes
  are authorized by this review step; implementation follows a selected concept.

Concept exploration: `Desktop/Codex/modern-bakery-layout-concepts-20261028`.
The first Blender version below remains unchanged as the comparison baseline.

28 October 2026. Uses the current reusable L2 main building and forward shelter
from `Level 2/modern/revision-03-window-boxes-sign`. The approved modern Bakery
concept supplies the sheltered baking/dispatch scene and striped bread display.
Later explicit directions retaining the historical opening arrangement and the
forward-projecting lean-to take precedence over the concept's architecture.

## Editable source

Under `Working Files/3D Art/BAKERS/Bakery/modern/revision-01-sheltered-bakery`:

- `CSC_BAKERS_Bakery_Modern_Review.blend`: assembled layout proposal.
- `CSC_BAKERS_Deck_Oven_Modern.blend`: two-deck oven and flue, inside the shelter.
- `CSC_BAKERS_Bread_Display_Modern.blend`: wooden display, bread and striped canopy.
- `CSC_BAKERS_Bread_Rack_Modern.blend`: wheeled cooling/dispatch rack with bread.
- `CSC_BAKERS_Tray_Stack_Modern.blend`: stack of empty baking trays.
- `CSC_BAKERS_Hanging_Sign_Modern.blend`: existing point-up/down hexagonal sign
  geometry with a Bakery bread pictogram.

Each standalone draft has a CN6 and saved-file validation report. These names are
working identities, not newly published reusable-library entries. Oven/display
are Bakery specialisations; the rack/tray design could become a shared food-industry
prop after review. Existing flower boxes remain in the assembly.

The saved L2 main/workshop meshes are appended from their individual masters;
decoded positions, normals, all UV channels and topology are compared with those
sources. Source Blender hashes are also checked unchanged. The buried foundations,
historical openings, rear dormer and complete shelter supports are retained.

## Painted surfaces and relief

Portable `textures/` merges current modern building r009 / props r005 with the
existing L2 candidate allocations. No published Current/library/runtime files change.
Building Stage 3 remains top-right. Existing candidate props cells 24/25 remain.
New Bakery candidates occupy adjacent cells 26–31: oven face, bread tray,
striped cloth, bread sign, empty tray and crust. Six generated B patches were
packed with gutters; explicit structural heights follow the generated paint.
Handles, controls, vents, cloth seams and bread scoring are texture detail.

Independent geometry-baked AO candidates on the 2048 props page:

| Model | Rectangle, top-left pixels |
|---|---|
| Oven | 512,256–768,512 |
| Display | 512,512–768,768 |
| Rack | 768,256–1024,512 |
| Trays | 768,512–896,640 |

Normals are disconnected during AO baking. The sign retains its unchanged
geometry/UV2 bake. Reviews exclude emission. Texture sources and measured height
arrays live beside the masters in `texture-sources/`; the complete evidence root is
`Desktop/Codex/modern-bakery-v1-20261028`.

## Verification and boundaries

Saved-file authoring validation and CN6→FGX round-trip checks cover each new prop:
geometry, normals, tangents, three UV channels, topology and static bone bindings.
Review images include combined, rear, overhead, full-strength AO, base-colour-only
and neutral normals under opposing lights. The first review prompted better bread
UVs/rounded outlines, a more visible oven position, and removal of redundant
oven/tray overlay faces. The new normal-map derivative uses the actual height-array
resolution: the older helper's fixed 512px assumption amplified 128px inputs fourfold.
The rack casts angular shadows across the oven in the assembled neutral-light view;
an isolated-oven diagnostic distinguishes these from a material or AO defect.

The full review assembly contains 3,776 exported vertices. This includes all
architecture, flower-box instances and new props; it exceeds the default 2,200
advisory target. No geometry is hidden from that total through reuse classification.
The separate oven is 236 vertices, display 612, rack 602, trays 120 and sign 132.

This is a first authoring proposal, not AE installation or in-game acceptance.
The modern L2 architecture and its texture quadrant are still candidates. Final
district placement/road clearance, CON+PIL, shared-atlas publication, AE assembly
and ArtDefs are subsequent integration work. No new paving apron is included.
AE will remain the authority for final placement; this review blend is not an
instruction to overwrite the existing historical Bakery assembly.

Source scripts: `project/tools/art/modern_bakery/`. Builders are initial recipes;
after hand edits, use the saved masters and scoped updates rather than regenerating.

## Interior lighting update - 28 October

The installed masters now have lighter painted room textures and fixed interior
UV3 with soft night emission. Source paths and assembly placements are unchanged.
Building atlas release r013; emissive library r001. See
[Quarter emissive atlases](quarter-emissive-atlases.md) for the complete allocation,
material bindings, publication rules and verification. Service lighting variants
were explicitly deferred; no Service logic was modified.

## Historical prop placement match - 28 October

Henno requested a smaller modern bread display matching the historical display,
and the delivery truck moved to the historical Bakery `_2` cart location. Both
modern Bakery ASTs now use display scale 0.731258 (35.10-unit width versus the
former48), with its footprint centred on the historical stand/table and grounded
at Z0. Position is(-14.354698,-5.166189,0) in AE units. The truck retains scale1
and adopts historical cart position(-19.827141,-11.359547,0), orientation
(0,0,-0.240588). Other assembly fields, including differing human rack placements
between standard and `_2`, are preserved. No geometry/atlas/AO edits were needed.
These are AE-owned placement changes; do not restore older review-blend placements.
Backups and matched day/night renders: Desktop/Codex/modern-bakery-placement-20261028.

## Active roof palette comparison - 28 October

Henno requested historical/modern daytime delivery comparison and modern roofing,
main ridge beam and bargeboards matching the historical active texture. Buildings
r014 changes only Stage3 B cells2(roof),3(ridge/barge trim, formerlycream),8(green
wood/roof edges and reused shelter timbers). Window frames staycream. Palette edit
used ImageGen, then historical texture RGB calibration and original per-pixel value
modulation to retain registered seams/grain and all normal/AO maps. Calibration
RGB medians: roof147/186/67, ridge/trim71/95/32, green timber80/107/37.
The active palette is retained in the regular modern B atlas for Henno to recolour;
no new active material or Service binding was created. AST placements unchanged.
Both delivery ASTs rendered with E disabled, identical L2 angle/scale, lens widened
to82% solely in this review job so the historical cart and modern truck fit fully.
Evidence/attached comparison: Desktop/Codex/modern-bakery-active-roof-20261028.

## Modern L2 state replacement - 29 October

The historical CON+PIL placeholder is now replaced in the reusable modern L2 and
both modern Bakery assets. The new shell includes only the main building, with
no extension. Current buildings atlas is r015 (independent state AO only); painted
maps and all worked assemblies are preserved. See [modern L2 CON+PIL](modern-level2-con-pil.md)
for the editable master, visibility rules, atlas allocation and verification.

## Bread display depth correction - 29 October

The modern display's placed width remains 35.1004 and its height remains 25.5940.
Its depth increases from 13.1626 to 31.0520, matching the historical stand/table's
combined depth; the cabinet itself matches the historical table depth, 24.1767.
The rear edge remains fixed, so the additional depth projects away from the wall.
The AE attachment still uses uniform scale0.731258 and its saved transform.

Cabinet, shelves and canopy were reauthored in the existing independent master;
support posts retain their section size. Two rows of the existing painted trays
per shelf retain bread aspect and aligned relief, rather than elongating the
artwork. The prop now exports648vertices (previous432). Both combined review
sources have matching display geometry; their placements remain non-authoritative.

Props release **2026-10-29_Modern_r010** replaces only the display's existing AO
cell [512,512,768,768]. Its 128-sample bake retains the registered painted bread
contact AO. All other AO pixels and B/N/G/M/E maps are unchanged, including the
oven's full-glass emission. Only the display FGX/GEO and shared props AO DDS change
at runtime. Saved-file validation, native readback and isolated cooking pass;
all ASTs remain byte-identical. Evidence: Desktop/Codex/modern-bakery-display-depth-20261029.

**Placement follow-up:** the deeper canopy overlaps the trolley's upper rack in
the alternate Bakery. The standard Bakery's trolley is clear. Henno was asked
whether to move the alternate trolley just clear or retain its saved AE placement;
no reply had arrived at publication, so the placement remains untouched. This is
a visible outstanding assembly adjustment, not a failed depth/UV conversion.
