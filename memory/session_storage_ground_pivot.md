# Storage ground pivot — 20 October 2026

User authorized direct shared master changes despite temporarily unmigrated
consumers. Installed centered/unrotated storage main, CON+PIL and PIL decals;
all four supplied Blender originals updated with backups. Fully migrated only
CSC_BAKERS_Storage_L and CSC_BAKERS_Classical_Base_03. Separate sibling delivery
asset CSC_BAKERS_Storage_Delivery uses CSC_ALL_Delivery_Pivot geometry/animation
and the same physical pivot as storage. Old shared delivery remains unchanged.

Transform and durable handoff: project/docs/art/storage-ground-pivot-trial.md.
Evidence: Desktop/Codex/CSC_Storage_L/pivot-trial-20261020.
Native geometry/26 attachment/animated source and converted animation checks
pass; visual saved-AST comparison inspected. ModBuddy build succeeded and both
platform tilebase BLPs rebuilt. Henno subsequently reports it looks good in game;
slight donkey levitation near the riverside Wind Mill on return remains.
Consistent with fixed animation heights relative to storage pivot; not measured
or corrected. Other bases, No_Delivery variants, Tailors and Water Mill not migrated.

Source delivery uses a parent coordinate frame, so future export of the
centered source must omit --rebase-transform (otherwise double transformation).
Static FGX preserves installed triangulation; arbitrary re-triangulation in
Blender after rotating n-gons can choose different diagonals.

Follow-up: user explicitly authorized a separate donkey/sled terrain experiment
on Base 03, cargo unchanged. Base03 now references
CSC_TRIAL_BAKERS_Delivery_Split, hiding the combined donkey and attaching
CSC_TRIAL_Delivery_Donkey to existing DonkeyPath with Pivot Height.
Child clip factors out the original route; both parent/child use no-random-offset
behavior. Crane/cargo originals remain byte-identical. 15-frame source/native
checks pass (<0.000217 / <0.279 Blender units), native skin/UV check passes.
Saved validator's sole STATIC_WEIGHTS error is the animated contract mismatch.
Native renders inspected. Henno subsequently reports the current behavior looks
"pretty much spot on" in game. Treat split Base 03 as the accepted visual reference;
retain cargo unchanged. Do not generalize this to measured engine behavior or
unreviewed placements.
Normal CSC SDK build/cook succeeded at 19:55, zero warnings/errors; Windows and
MacOS tilebase BLPs rebuilt. Game left under Henno's control.
Evidence/master: Desktop/Codex/CSC_Storage_L/donkey-terrain-trial-20261020.
See durable document for rollback and the deliberately unchanged cargo behavior.

Family rollout 20Oct: Henno accepts storage contact/props and split donkey.
Migrated remaining five storage ASTs (114 points), eleven district attachments;
all six variants / twelve bases now centered, eight with split delivery.
Props stay storage children. Cargo records unchanged; Tailors textile cargo
kept distinct. Added three variant split-delivery ASTs reusing exact accepted
child and centered parent binaries. Removed orphan cargo/bindings in two
No_Delivery ASTs. Base03 accepted files and reused binaries hash-protected.
All60 base/state resolutions and placement-matrix checks pass; normal, pillaged,
construction saved-AST Tailors03 previews inspected.
Reported pillaged disappearance was in game. User says possibly build issue;
fix only if found, otherwise prioritize placements. No definite source defect;
damaged shell visible/aligned offline, runtime remains unconfirmed after rebuild.
Desktop evidence: CSC_Storage_L/storage-family-pivot-20261020. See durable doc.
SDK build/cook complete at20:26, zero warnings/errors. Both platform BLPs contain
all24 affected identifiers;19 staged/live AST hashes match,3 new installed loose
copies match. Existing ASTs cooked from workspace pantry (not all loose Content).
No game restart or new in-game verification performed.

Cafe wall follow-up: user requested centered CSC_ALL_Stage_4_Wall children with
overall translation on Cafe/Cafe_2 wall attachment. AST-only11-segmentassembly,
no newgeometry/sourceexports. Subtract AE(15.2981458249,8.3288062046,0) from every
wallsegment; both Cafe parentpositions now(15.351223825,8.289325205,0), all other
fields unchanged.22worldmatrixchecks max2.85e-14; before/after savedASTvisuals
inspected, paving preserved. Evidence Desktop/Codex/CSC_Cafe_Wall/ground-pivot-20261020.
Future paving-fit reconstruction must include wallparenttransform (old local
wall point coordinates no longer equal Cafe coordinates). See durable pivotdoc.
Wall SDK build/cook passed0warnings/errors; both platforms rebuilt and verified,
3staged/liveASTs match, geometryhashes unchanged. In-game terrainreview pending.

WaterMill follow-up: user requested building-side flour baked into shared geometry
for standard/_2, carts left attached, current material mappings preserved.
Installed shared17meshFGX/GEO (original3+13commonflour+1variantonly); standardAST
hidesvariantonly. Bothnativecarts and2loaded sacks remain independent unchanged;
askedoptionalquestion, noansweratimplementation, statedassumptionkeepcartloads.
Removed50staleASTrows/variant referencing10absentoldflourmeshes. Currentflour
CSC_ALL_Props_01 and existing nativegroup name retained; E vsE_2buildingpalette,
foundation/floor,stateflags/CONPIL/wheel/groundpatches preserved. Nativeattribute
checks17meshes pass; savedmastervalidator0errors/1advisorybudget2974>2200.
Updated originalLevel1/Bakers/CSC_BAKERS_Water_Mill.blend withnativealigned geometry
andportabletextures; beforemaster backedup. Source/native/state/visualchecks pass.
Evidence Desktop/Codex/CSC_Water_Mill/fixed-flour-20261020; durable
project/docs/art/water-mill-fixed-flour.md. Riversideterrain ingamecheck pending.
WaterMill build/cook complete20:44, 0MSBuildwarnings/errors; bothplatform
variantentries/freshBLPs verified, 4runtimefiles+source+textures matchstaging,
originalrootframe unchanged. ExistingCONPIL2degeneratetriangles unchanged.
