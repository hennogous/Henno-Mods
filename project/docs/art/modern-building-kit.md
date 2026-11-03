# Modern building kit and atlases

**28 October: modern L1 CON+PIL retake.** The reusable base, silo and both mill
assets now use current modern state shells. Buildings atlas **r009**, props
**r005** add only independent state AO; worked surface maps and occupied AO
pixels are unchanged. See [state masters, assembly and verification](modern-level1-con-pil.md).
This supersedes the historical/prototype CON+PIL status recorded below.
The r009 correction fixes inward/inconsistent state-wall faces and rebakes AO,
including an independent cell for the Wind Mill's exposed cut beam ends.

**28 October: Level 2 revision 03** is available with historical wall openings,
rear dormer, separate workshop, reusable flower box and point-up hexagonal sign.
See [the Level 2 handoff](modern-level2-first-version.md)
for masters, concept fidelity, Stage 3 candidate atlas and validation. This candidate
does not change the published Level 1 atlas or live AE assets described below.

Agreed with Henno, 27 October 2026. The accepted modern Wind Mill revision 08 is
the first reusable modern Stage 2 / Level 1 kit. Preserve its concept-derived
proportions, straight roofs, thin timber beneath green bargeboards, darker ridge,
strong texture-authored brick/windows and foundations extending to Z=-30.

## Models and assembly

**Previous material delivery, 27 October:** buildings **r007**, props **r004**.
The corrective normal pass (buildings r005 / props r004) replaces the rejected
threshold/noise treatment with registered masonry joints, folded roof seams,
recessed glazing and traced timber grain. Twelve saved-assembly diagnostics cover
both mills: B-only, neutral normals off/on under two light directions, and combined
materials. Agent visual review, native DDS readback and isolated SDK cooking passed.
Human visual acceptance and in-game appearance remain unverified.

Buildings r007 retains those corrected normals and the **256x256 emissive atlas**.
All four panes of every upstairs window emit equal warm light; ground-floor windows
map to black. The softness is retained. This corrects r006's two dim panes and lit
ground-floor window to match the historical building convention. The reusable base and Water Mill masters
have UV3-only updates; native geometry, UV1/UV2, B, AO and saved AST placements are
unchanged. Wind Mill inherits the shared base. The dark historical/modern comparison
has emission and glow disabled, as requested. Emissive diagnostics are separate;
they do not establish in-game appearance. Future side-by-side comparisons must
exclude emissive unless explicitly requested.
The portable rebuild retains `sources/registered_E.png`. Current master paths
below remain unchanged. Backups, validation, cook results and review images are at
`C:\Users\Shadow\Desktop\Codex\modern-normal-correction-20261027` (emissive subfolder
for r006 publication; `emissive-r007` for the upstairs-only correction). No new B artwork or geometry was introduced in this pass.

Earlier paint/layout refinement, 27 October: buildings release **r004**, props **r003**. New
ImageGen painting uses `DIS_COM_Base_B.dds` as treatment reference. Brick and roof
relief is stronger; timber normals follow actual painted grain rather than a sine
pattern. Small details stay in colour/normal maps. The building quadrant and
128px sampling scale remain fixed. Props cells are now:

| Row | Column 1 | Column 2 | Column 3 | Column 4 |
|---|---|---|---|---|
| 1 | green roof | green trim | ivory trim | cream metal |
| 2 | wheat silo | elevator casing | dark iron | concrete |
| 3 | marked flour sack | sack ends | pallet wood | stone |

All four current props-material geometry consumers were migrated together:
silo, trolley, pallet and Water Mill machinery. Historical libraries are unchanged.
The entrance slab and backing wall are removed; the main foundation has a notch
following the opening down to Z=-30, with buried masonry remaining beneath walls.
Human mesh edits from revision 03 are preserved exactly outside that targeted work.
Water building propagation matches the shared source within 0.000026 units.
Current Water export: 2,333 vertices / 1,317 triangles excluding reusable attachments.
Existing ASTs, placements, states, ArtDefs and XLPs are byte unchanged.

Evidence: `Desktop/Codex/modern-kit-refinement-20261027`. Saved-file validation,
native FGX positions/frames/UVs/weights/topology, dependency resolution and isolated
SDK cook passed. Inherited CON/PIL degenerate-triangle warnings remain; no new
runtime/game or live AE UI validation is claimed. Matched comparison widens the
same icon camera lens for both buildings to fit historical sails; production
camera presets are unchanged. Earlier sections below retain initial-delivery history.

Paths below are relative to `Working Files/3D Art/`.

| Identity | Editable master | Purpose |
|---|---|---|
| `CSC_Level_1_S_Modern` | `Level 1/modern/revision-04-painted-kit/CSC_Level_1_S_Modern.blend` | Human geometry cleanup preserved; open entrance foundation; complete shelter. Building, Shelter and SiloSideSupports groups remain reusable. |
| `CSC_BAKERS_Mill_Silo_Modern` | `BAKERS/Wind Mill/modern/revision-10-painted-kit/CSC_BAKERS_Mill_Silo_Modern.blend` | Silo, elevator, pipe, intake and close stock; migrated modern props UVs. |
| `CSC_BAKERS_Flour_Trolley_Modern` | `BAKERS/Props/Modern/revision-02/CSC_BAKERS_Flour_Trolley_Modern.blend` | Trolley and sack, unchanged geometry/pivot; migrated UVs. |
| `CSC_BAKERS_Flour_Pallet_Modern` | `BAKERS/Props/Modern/revision-02/CSC_BAKERS_Flour_Pallet_Modern.blend` | Sack stack and pallet, unchanged geometry/pivot; migrated UVs. |
| `CSC_BAKERS_Water_Mill_Modern` | `BAKERS/Water Mill/modern/revision-02-painted-kit/CSC_BAKERS_Water_Mill_Modern.blend` | Updated reusable geometry, preserved historic foundation and machinery placement, migrated props UVs. |

Each identity has one editable blend, CN6, native geometry and AE asset. The base
has four shelter corner supports, including the previously absent silo-side
post, footing and brace. Its standalone asset shows all supports. Only the mill
assembly hides the additional SiloSideSupports group; this is an exception for
the silo connection, not the reusable base geometry.

The long wall has only one upper window beside the shelter. The second window
at the shelter junction was removed in revision 02: leave uninterrupted brickwork
there in both the reusable asset and the Wind Mill. Revision 02 preserved all
remaining geometry and UVs and exported 1,405 vertices / 787 triangles. Revision
03 finishes the shelter with a closed roof underside, solid timber gable,
green/wood barge trim, side bearer beams and consistent painted supports. The
revision 03 base exported 1,560 vertices / 868 triangles. Current revision 04 exports
1,496 vertices / 840 triangles after the entrance cleanup.

The existing `CSC_BAKERS_Wind_Mill_Modern.ast` now directly references the shared
base and mill specialisation geometry. Keeping them as direct model instances
makes the silo and connecting structure move with the building. It references
the trolley and pallet stack as two independent asset attachments. Their
placements reconstruct revision 08 (maximum authoring coordinate error below
0.00003 units), with uniform scale and permanent culling. Both props are hidden
in Construction, Pillaged and Unbuilt. Their stock is not duplicated in the
main geometry. The two other upright sacks and two spare pallets remain in the
mill specialisation's Stock group, preserving the user-edited layout.

AE continues to own final assembly placement. Do not export an assembled render
snapshot back into AE. Edit the relevant individual geometry master and preserve
the saved AST's placements on subsequent exports. Keep the bases off origin in
their established district placement. Prop masters have local ground pivots;
attachment transforms restore the previous placement, including the pallet's
existing shallow burial.

The mill's pre-existing CON+PIL geometry/settings are retained; they have not
been redesigned by this split. The reusable base asset references the existing
shared `CSC_Level_1_S_CON+PIL` shell/scaffolding with historical state materials.
This is reuse of existing state content, not a claim of newly authored modern
construction/pillage art. Existing Modern-era ArtDefs are unchanged.

## Separate modern atlas families

These are new libraries; historical building and prop textures remain intact.

| Library below `Textures/` | Runtime maps/material | Layout |
|---|---|---|
| `CSC_Buildings_Modern` | `CSC_Atlas_Modern_B_BAKERS`, `CSC_Atlas_Modern_{N,G,M,E,AO}`; material `CSC_BAKERS_Modern` | 1024² B/N/G/M pages, 256² E from r006, 2048² AO from r003. Stage 2 occupies the top-left quadrant. Top-right reserves Stage 3, bottom-left Stage 4, bottom-right storage. |
| `CSC_Props_Modern` | `CSC_Props_Modern_01_{B,N,G,M,E,AO}`; material `CSC_Props_Modern_01` | 1024², 128-pixel cells; compact 4×3 occupied block in the top left, grouped by material. UV2 AO retains a separate 2048² page with 2×2 Quarter regions. E is black 16². |

The initial building quadrant uses nine of sixteen 128² material cells. The prop
surface sheet uses twelve of sixty-four cells. The initial scattered historical
slot positions were superseded at Henno's request by props r003. Other cells and
building quadrants remain reserved/free. The prop AO page reserves the Bakers
top-left 1024² region; the first Stage 2 assets use only its top-left 512² family
block. Other Quarter regions follow the historical AO arrangement. Do not create
additional pages until they are needed.

`Current/atlas-plan.json` is the allocation authority. Runtime names stay fixed;
revisions live in `Releases/`. Both libraries start at
`2026-10-27_Modern_r001`. Each includes `CURRENT.json`, a library manifest,
preserved full-resolution V8 B/N/G/M source artwork, independent geometry AO
bakes, and a portable `scripts/rebuild_modern_atlases.py`. Delivered blends use
local relative texture snapshots; runtime TEX sources point to canonical Current.

The initial artwork reuses the approved V8 ImageGen/native textures, packed
deterministically. No replacement procedural artwork was introduced. Texture
repeat scale is retained while patch resolution is reduced for the shared
layout. Normals are renormalized after resizing. Each independent model has
self-AO, so reusable props do not carry occlusion from the old host scene.
The cone UV boundary was repaired during migration to avoid sampling a different
material cell. Future new artwork follows the existing ImageGen requirement.

For future Quarters, reuse these model proportions and shared N/G/M where
compatible, with Quarter-specific B palettes and occupational specialisations.
Do not copy the whole mill or allocate another private full-building atlas.
Preserve occupied cells and explicit model-to-atlas mappings when extending either library.

## Verification and evidence

Four saved-file authoring checks, native FGX readback of positions/frames/UVs/
weights/topology, attachment/state resolution and an isolated SDK cook cover this
delivery. Native rendering verifies the complete reusable base, the assembled
mill and both independent props. Live AE UI and in-game terrain behavior remain
separate review checkpoints.

Working evidence: `Desktop/Codex/modern-mill-modular-v9-20261027/`.
Producer scripts: `project/tools/art/modern_windmill/modular_v9*.py` and
`rebuild_modern_atlases.py`. The extraction starts from the immutable revision 08;
never rerun it over future user edits. Re-export edited individual masters instead.

### Blank shelter wall revision (27 October 2026)

Building atlas release `2026-10-27_Modern_r002` rebakes the shared base AO after
removing the window; all other surface maps and atlas quadrants are unchanged.
The props library remains r001. The reusable base AST also corrects five stale
`CSC_BAKERS` material references to the existing `CSC_BAKERS_E` material used by
the historical building states. Mill AST, placements and ArtDefs are unchanged.
Saved-file validation, native component readback, all-state dependency resolution,
isolated SDK cook and both intact saved-AST renders passed. No live in-game check.
Evidence: `Desktop/Codex/modern-base-blank-brick-20261027/`.
Selective producer: `project/tools/art/modern_windmill/blank_shelter_wall.py`.

### Finished shelter and first modern Water Mill (27 October 2026)

Henno explicitly treats the generated Water Mill concept as inspiration only:
its proportions are not authoritative. Use the reusable kit at its authored
dimensions and the historical Water Mill foundation/footprint as the guide.
The house is translated into the historical frame at (-34, 20.5, 6.15), without
scaling. The original foundation vertices and topology are retained and
retextured. The Wind Mill intake is reused left of the shelter; its user-edited
object transforms must be evaluated after library append. Only the Water Mill
loses the lower long-wall window behind the intake. The complete shelter remains.

The pallet stack and trolley are native CSC asset attachments, positioned on the
existing platform. A compact green/cream bearing housing, vertical shaft and
lower turbine casing occupy the former wheel envelope. Existing painted atlas
patches provide panels/rivets; these details are not modeled. The new asset
exports 2,397 vertices / 1,345 triangles before the reusable prop attachments.
The advisory 2,200-vertex building target produces one warning, not a blocker.

Firaxis `DIS_CTY_AWW.ast` uses `FX_Rock2_Wake` for water turbulence. The modern
Water Mill reuses that native ASSET_FX trigger in its WORKED_A timeline, anchored
at (39, 20.5, -23), uniform scale 0.65. The provisional Z is near the historical
wheel's lowest extent (-22.78), not an in-game water-height measurement. Static
Blender renders do not evaluate the effect. Water-level alignment, effect scale
and state transitions still need the owner's in-game review.

The modern Water Mill retains historical CON+PIL/decal geometry and registers
its own `ARTERA_MODERN` variant for BUILDING_CSC_BAKERS_WATER_MILL.
Existing Wind Mill/base ASTs and all other saved placements are unchanged.

Earlier AO allocation release: buildings `2026-10-27_Modern_r003`, props
`2026-10-27_Modern_r002`. Surface artwork/occupied cells are unchanged. Building
AO is now 2048²: shared base [0,0,512,512], Water Mill building [512,0,1024,512],
both within the Stage 2 top-left 1024² quadrant. Water Mill machinery uses the
previously free props AO rectangle [256,256,512,512]. `AO_allocations` in each
atlas plan is the current allocation authority; the older nested props mapping
is migration provenance. Source snapshots and portable rebuild tools are included.

Both installed masters passed saved-file checks with zero errors; native
position/frame/UV/weight/topology readback, state/dependency resolution and an
isolated SDK cook passed. All 102 published files were hash-verified. Reviewed
images include the reusable base, the Wind Mill and a full-depth Water Mill
view reconstructed from the saved AST. Evidence:
`Desktop/Codex/modern-water-mill-v1-20261027/`. Producers: `water_modern.py`,
`water_modern_native.py`, `finish_water_housing.py`, `review_water_modern.py`.
