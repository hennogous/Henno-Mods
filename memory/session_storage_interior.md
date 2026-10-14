---
name: Storage L open upper interior
description: 8 October 2026 source rework restores an open upper floor and inward walls; CON+PIL later.
type: project
---

Henno requested a big open upper floor visible through the openings, with simple
interior walls following the exterior and normals facing inward, ready for later
CON+PIL roof removal. Compared original CSC_Storage_L.pre-ao.blend and current
CSC_Storage_L_CON+PIL.blend; both have the original continuous floor. Recent source
had three deep boxed recesses instead. Replaced their 12 faces with one T-shaped
upper floor, plank strips, downward ceiling, inward upper shell lining and shallow
opening reveals. Floor remains original wide crane-bay level46.555393 local units.

Saved the actual Working Files/3D Art/Storage/Storage_L/CSC_Storage_L.blend.
CON+PIL and delivery sources remain unchanged; no production geometry/AST updates.
Current user's source geometry has applied placement differing from earlier crane
placement: recovered exact affine from 1484 matching backup points, preserving all
current exterior vertices/UVs including user edits. Do not reset to earlier location.
Removed only exact matched recess faces; all retained face corners verified identical
in all3UV channels. New inward winding checked numerically. Static Root weights1.

Source1810verts/458faces; CN6 prepared1816verts under2200 advisory target. Saved-file
validator passes automated rules; expected visual review prompts remain. CN6 export
verified in output folder only; user's normal AE export still needed.
New face int attribute storage_interior_part:1floor,2ceiling,3walls,4reveals.

AO baked only newfaces with existing shell/roof as occluders. Shared Atlas_AO2.png
canonical source updated only in12free charts audited against S/M/L normal+CON/PIL,
crane, oldpreAO and lean-to sources using actual AO2 materials (exclude scaffold
materials on another atlas!). Chart rectangles recorded in ao-allocation.json.
2174pixelschanged of2352reserved at1024resolution; every otherpixel identical.
UV1/UV3 and retained UV2 preserved. Runtime DDS not refreshed because this was
source-only rework; when exporting building also refresh shared AO2 texture fromPNG.
Mapped AO cutaway inspected; newfloor/walls show clean contact gradient.

Outputs Desktop/Codex/CSC_Storage_L/interior-20261008. Backup before-interior holds
originalblend andcanonicalAO2PNG. Build/check/render/bake tools project/tools/art:
inspect_storage_interior.py, rework_storage_interior.py, inspect_storage_ao_space.py,
bake_storage_interior_ao.py, save_storage_interior.py, preview_storage_interior.py,
check_storage_interior_export.py. Source rework uses captured component inventory
and placement transform; do not blindly rerun after further user edits.
Dropzone Storage-L-Open-Interior-Cutaway.png, -Reverse.png, -Intact.png.
Cutaway is temporary preview only; intact source roof retained for later state work.

9 October: added 16 quads continuing both beveled entrance surrounds to foundation
bottom; resized complete static building to 0.9 of its previous current size around
its own ground position (-34.9057007,168.9768982,0). Optional pivot question received
no reply; assumption stated before applying. Additional reduction of baked geometry.
Retained UVs unchanged. Source1874verts/474faces; CN61880. Foundationbottom-17.496;
upperfloor37.70987 (previous41.89985). Crane/delivery/CON+PIL/nativeproductionfiles
hash-preserved. Loading bay lower but animation untouched by explicit request.
Backup/evidence: Desktop/Codex/CSC_Storage_L/foundation-scale-20261009.
Saved-file automated checks and CN6 export passed; inspected both entrancecloseups.
Sourceonly, normalAEexportpending. Dropzone Storage-L-Foundation-09-Building.png,
-Front-Entrance.png and -Side-Entrance.png. Don't rerun older interior scripts.

10 October: later explicit user direction supersedes 9Oct source-only/own-origin
scope. Anchored resize at narrow gabled front (-17.6548443,126.5827637,0) by
translating already resized geometry (no second reduction). Crane scaled/moved
with shell, delivery stop/hoist refit; cargo .8, donkey/sled1.0. Installed static
FGX/GEO (1880verts,996triangles) plus deliverymodel/clip, changed ASTCargo scale
only. RuntimeAO2 DDS already newer than interiorPNG, left intact. Sources and
workingDeliveryBlend saved; automated/clearance/nativechecks pass. CON+PIL still
unchanged. Evidence/backup delivery-refit-20261009. No UI; manual AE review next.
