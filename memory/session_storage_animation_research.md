---
name: session-storage-animation-research
description: Native mine/crane animation and Blender 3.1 conversion evidence; skill updated, storage unchanged
metadata:
  type: project
---

7 October 2026: Henno requested animation investigation and addition to civ6-art,
for eventual large-storage animation. Durable result:
`project/docs/art/storage-crane-animation.md`. Installed civ6-art has
`references/art-animation-workflow.md` and SKILL/export routing; not pushed.

Blender 3.1.2 NA2/CN6 add-ons are installed and enabled. Native quarry crane and
mine donkey/sledge gait were imported and rendered. Mine travel uses a one-bone
parent; stock NA2 import skips its only bone. Authored hoist: binary FBX through
CivNexus6 1.3.3, separate animation FGX/ANM, matching weighted CN6 model, geometric
roundtrip verified. FBX scale .01 + apply_unit_scale=False avoids 100x displacement;
format 0 preserves weights, standard 2/3UV formats omit them. Normalize the
converter's AssetObjects: XML prefix to AssetObjects.. for ANM. AE/cook/game remain
untested; this is not a finished animated storage crane.

Read-only current `Storage_L/CSC_Storage_L.blend` inspection found eight static
crane parts and no rig; older Bakers rev01 is not the latest building source.
CSC scene exporter rejects animated armatures. Keep new animation separate or
implement a proper animation contract; do not silently bypass the static check.
Trial assets/scripts/logs: Desktop/Codex/Civ6-animation-research-20261007.

Follow-up: built Civ VI Animation Tools 1.0.0, source in installed civ6-art
`scripts/civ6_animation/`. Blender 5.1.2 integration: 25 checks passed, including
native crane/donkey/one-bone travel, NA2 root/rotation/scale, native rotation/scale
deformation, matching skinned model and source preservation. Installed/enabled in
the 5.1 user profile; File Import/Export and N-sidebar Civ VI buttons. Native
converter uses installed CivNexus6 1.3.3; no Firaxis binaries in ZIP. Package and
install/test evidence: Desktop/Codex/Civ6-animation-addon-20261007. Restart any
already open Blender to load it; live MCP was not connected. AE/cook/game still open.
Fresh-process verification loaded the installed module from AppData and ran its
Import, NA2 Export and FGX/ANM Export operators successfully. Export restored Pose
mode and the original Action. See installed-verification.json/log in the package.

Follow-up first crane animation: `Desktop/Codex/CSC_Storage_L/revision-01-crane-animation/`.
Editable `CSC_Storage_L_Crane_Animation.blend` (source untouched), 12s / frames1–361
at30FPS, Root/Swivel/Trolley/Hoist/Load bones. Actual textile-bale library instance
at uniform0.75. Lift ground→upper bay, trolley4 units inward during lift (explicitly
authorized), clockwise128° swing, trolleyoutward again to clear jamb and get all
of bale inside, setdown/hold. Single delivery; no seamless loop/release yet.
140° clips brace/frame;128° clears. Saved-file all361frame surface check passes.
Geometry/topology/UV parity passes for all33 source meshes and library bale.
Static validator's two bone-terrain/support errors remain honestly recorded;
`final-audit.json` validates them under the actual skeletal-attachment contract.
No static exporter/validator bypass or changes. Intact Blender prototype passes;
production material/AST/states/AE/cook/game remain incomplete.

Crane native roundtrip uncovered symmetric-cube blind spot: default FBX Y/X bone
axes differ from CN6 bind basis and permute geometry around pivots. Fixed exporter
to primaryX/secondaryZ, released/installed1.0.1;25 regression checks pass with
unequal1×2×3 test mesh. Actual crane native maxvertexerror0.04213units, clip12.000001s.
New ZIP/installbackup/regression evidence live in the animation revision package.
Latest generic lesson added to civ6-art animation guide. Durable CSC doc updated.

8 October: user authorized AE setup. Installed separate `CSC_TEST_Storage_Crane`
and `CSC_TEST_Storage_L_Animated` assets in CSC (no production ArtDefs changed).
Worked slot/timeline → `CSC_TEST_Storage_Crane_Lift`, native
`Standard_LandmarkNoRandomOffset` for deterministic preview. Export-copy Load
bone basis corrected so the actual library bale attaches with zero offsets,
rotation0/scale0.75. Animated crane9meshes includes mount; static shell25meshes
uses3UV format2. Crane1UV material has neutralwhiteAO, other originalmapsreused.
Registered AssetCloud, XLP and project Content entries; backups and stage package
under Desktop/Codex/CSC_Storage_L/ae-test-20261008. Conversion errors<.043;
independent shellFGXdecode maxpositionerror.0000464. AE/cook/game unverified.
Reproduce with project/tools/art/build_storage_crane_ae.py (Blender) and
install_storage_crane_ae.py --install (Python); explicit --output required.
Blender5 gotcha: renamed copied rig needs explicit animation_data.action_slot;
assigning only Action can bake a static clip. Added ground/liftheight assertions.

8 October follow-up: AE trials reported crashing; do not call the test package
production-ready. User narrowed scope to preparing his latest UV-edited storage
source, and will perform the export himself. Updated original CSC_Storage_L.blend:
one combined 1,887-vertex mesh, donor Root/Swivel/Trolley/Hoist/Load rig and Action,
saved REST. All UVs/material/face-corner geometry preserved; 361-frame motion audit
passes and static building remains still. No bale/slings added. Backup alongside:
CSC_Storage_L_before_rig_20261008-114851.blend. Evidence source-rig-20261008 under
Desktop/Codex/CSC_Storage_L; durable storage-crane-animation.md updated. Normal
3-UV CivNexus conversion still drops weights; source prep does not resolve that.
Blender Join unlinks only active-scene objects: explicitly removed original
Review links after joining to prevent duplicate surfaces. Combined foundation is
now visible in Review (previously excluded collection), preserved for export.

Latest 8 October steering: user removed crane and positioned/applied transforms
in his own CSC_Storage_L.blend. DO NOT replace that file with our earlier combined
version. Created sibling CSC_Storage_L_Crane.blend from the animation revision,
with eight original crane components' latest pre-separation UV edits, the sling,
rig/action and library bale. Crane material copied from CURRENT building as
CSC_TAILORS_NE; bale keeps library material. Crane_Placement empty moves the whole
assembly: scale .9, X .3160286 m, Y 1.658027 m, Z 0, rotation Z20.4866 degrees.
Scene unit scale .01, so internal translations are 31.60286/165.8027. User explicitly
reconfirmed these numbers after a saved-building alignment discrepancy; follow his
numbers, don't silently fit placement to building. Full361-frame transform parity
max error .0000413 model units; building file hash unchanged. Source opens POSE,
frame1, ready for further animation edits. Preview shows bale in Blender only;
AE missing bale remains unresolved. Evidence positioned-crane-20261008 under
Desktop/Codex/CSC_Storage_L. Parent placement requires baking an export copy or
one AE attachment transform; current animation exporter requires identity rig.
Earlier upgrade was superseded by separate-crane discussion: CN6ToFGX.cs contains
an uncompiled multi-UV skinning draft; installed exe/addons were not upgraded.
An earlier static shell+child AST was staged at attached-crane-20261008 but not
installed. It predates the user's latest building edits: do not install as-is.

8 October delivery continuation: user confirmed bale IS visible in AE; supersedes
older missing-bale notes. Authorized Tailors Textile Workshop + textile bale, native
mine donkey, crane handoff, same-road return and 10-second break. New separate source
Working Files/3D Art/Storage/Storage_L/Delivery/CSC_TAILORS_Storage_Delivery.blend.
68 seconds / 2041 frames @30; donkey returns by58s, rest58-68. Master has Cargo and
DonkeyPath bones; body gait is second68s clip. Ore crate removed from derived donor,
wooden deck added; cargo stays replaceable AE attachment(.675), donkey scale.65.
Latest saved crane has NEGATIVE X(-31.6029 internal), despite stale customproperty
positiveX. Current matrix authoritative; original building/crane hashes preserved.
Native3UV skinning converter implemented, compiled isolated delivery-01/bridge,
saved FGX validation passes. Installed generic FGX exporter/exe unchanged. Master
vertex native error.0111, donkey.3903local(.2537world), attachmentmatrix.0716.
AE trial assets installed/registered: CSC_TEST_TAILORS_Storage_Delivery,
CSC_TEST_TAILORS_Delivery_Donkey, CSC_TEST_TAILORS_Storage_Delivery_Preview.
Preview references current exported CSC_Storage_L and CSC_TAILORS_Textile_Workshop.
MP4+GIF Tailors-Delivery-2x.* placed in Working Files/Dropzone, 34sec at2x; realpause10s.
User stopped computer use before opening trial, asked for manual steps. STOP UI
automation until reauthorized. AE playback/synchronization/cook/game unverified.
Sources/tools/checks documented at project/docs/art/storage-crane-animation.md.

8 October revision 2, user feedback: donkey absent in AE; exit through wall; unwanted
U-turn at crane and visible twist on re-entry; requested random offset per instance.
AE log f395c6f0... explicitly says dependent CSC_TEST_TAILORS_Delivery_Donkey could
not resolve from csc_tilebases.xlp for both parents. Revised native model now includes
donkey directly (10 meshes, one32-bone skeleton including object root, ONE68s clip).
Authoring rigs remain separate; export bakes both. Shared clock allows Standard_Landmark
RandomOffset=true safely; Preview deliberately NoRandomOffset. Fixed10sec rest retained,
random starting phase only, not different speeds/new random delay per loop.
Measured doorway centre(-22.361,-189.7365), width18; adjusted native lateraloffset,
startdeep42units, straight returnthroughdoor, directsouthwardpickupdeparture. Hideonly
afterentiresledinside, no visibleturn. Door crossingmaxlateral6.256,height19.22; tail
9.69behinddoorbeforehide. Combinednativeerrors crane.0111 donkey.1253 attachment.0735;
preexportbind.000134. Combined bone creation must initialize head/tail beforematrix,
and normalize editbone basis; avoid bind capture on microscopic hidden-scaleframe.
Installed main+Preview updates, cachemerged andbackups underdelivery-01. Newvideos
Working Files/Dropzone/Tailors-Delivery-v2-2x.mp4 and.gif; workingblendupdatedsameDelivery
path, originalbuilding/craneunchanged. UsercontinuesmanualAEcheck; NO computeruse.
Revision2 final registration fix: XLP uses tab indentation; old installer literal
space-indented closing-tag replacement silently inserted noentries. Confirmed AE
missing-dependent-asset errors and absentEntryIDs. Newinstallerregexacceptswhitespace
and assertsactualsavedEntryIDs. Both revisedmain/Preview IDs nowregistered. ModBuddy
Content entriesalreadyexisted. Directdonkey geometryalsoeliminateschilddependency.

8 October revision 3: Henno confirmed revision 2 looks good in AE, requested tighter
workshop entry/exit and closer road following on both journeys. Route knots now
follow painted road centreline; sampler compensates native lateral body offset
(0,-5.2*.65,0) at every heading. Earlier turn beside workshop and shared road curve,
closer junction approach. Pickup position preserved by centreline-to-origin conversion.
Door check max lateral 5.827 in 18-unit opening, sled 11.51 inside before hiding.
Native 17-pose checks: crane .0111, donkey .1408, attachment .0725, bind .000115.
Same 68s cycle/10s pause, Cargo attachment and random phase semantics. Revision 2
backed up under delivery-01/before-road-revision-03. v3 MP4/GIF in Working Files
Dropzone/Tailors-Delivery-v3-2x.*; working Delivery blend updated. No UI automation;
revision 3 AE motion check remains manual. Original building/crane sources unchanged.

8 October revision 4: User screenshot showed both journeys still cut inside upper
road bend. Previous hand-traced route was wrong; exported road and Blender XY
match within .000064. Added read-only road mesh/UV extraction and alpha-footprint
measurement; use actual decal opacity rather than visual estimates. User also
explicitly asked for quicker workshop road join, pointing to our overlay: now
turns on short Curve_M.009 front road instead of broad sweep through grass gap.
Shared road starts (-57,-170), upper bend near (-50.5,0),(-60.04,20),(-78.18,50).
Both directions: 775 checked centreline samples, all opacity>.65. Door max lateral
5.822 within halfwidth9, sled11.74 inside beforehide. Native errors crane .0111,
donkey .2829, attachment .0723; bind .000115. Installed package-revision-04;
Working Files Delivery blend and Dropzone Tailors-Delivery-v4-2x MP4/GIF updated.
Saved static scene checker flags its expected incompatible animated rules (pantry
derived direct body, source UV/skin weights, bone cargo vs terrain support).
Dedicated native checks cover these; do not regress to static weights/terrain
attachments. Detailed scope disposition in durable storage animation doc.
Original building/crane untouched, no production ArtDefs changed, no UI automation.

8 October revision 5: User approved v4, requested a smaller upper-left storage loop
to leave room for props. Outbound loading knots now turn inward at (-120,83), loop
near X-127 instead of X-155, and keep the original southward pickup approach.
Centreline westmost -156.59 -> -127.94; outbound distance562.99 ->508.44.
Shared road/workshop path, full inbound route and pickup coordinates unchanged.
Added storage surface collision check: loaded donkey/sled/bale clear building at
all sampled approach frames. Door and alpha-road checks pass. Native errors .0111
crane/.2897 donkey/.0641 attachments, bind .000115. Saved static report repeats the
same five inapplicable static-contract findings from v4; no new issues.
Installed package-revision-05, Working Files Delivery source updated; MP4/GIF
Dropzone/Tailors-Delivery-v5-2x.*. v4 backed up in before-road-revision-05.
No UI automation, originals and production ArtDefs unchanged. v5 AE review manual.

8 October production naming: Henno created CSC_TAILORS_Storage_L.ast using
CSC_ALL_Delivery geometry/animation. Renamed nativeFGX mesh old
CSC_TEST_TAILORS_Donkey_Mesh -> CSC_ALL_Delivery_Donkey, matching GEO and all5 AST
meshstate refs. Native serialization helper preserves source geometry; CN6exact
comparison onlyname differs, 30FPS NA2 before/after identical. Exporter updated
toemit newnameonfuturebuild. Existingcargo alreadycorrect on modelinstance
CSC_TEST_TAILORS_Delivery_Rig / bone Cargo / scale.675; preservedthis because AE
can'tattachtoamesh and Cargo handlesdonkey->crane transfer. User informed.
UserASTotherchangespreserved; noanimchanged. Backups/report under
delivery-01/production-mesh-rename. AssetCloudtimestampsupdated, edgesunchanged.

8 October revision 6: User requested BOTH donkey and sled at original Mine scale
1.0 (previous .65); bale stays .675. Wider workshop sweep and straight approach
55 units outside doorway; neck dips 42 degrees under arch. Home depth60 ensures
longer sled is inside before hiding. Compact storage loop and measured shared
road retained; widened workshop turn intentionally leaves short front curve.
User explicitly said workshop threshold will be removed: DO NOT add a lift or
spend more work clearing it. Final motion has no threshold lift; doorway BVH
excludes low threshold polygons, retained frame/arch and storage checks pass.
68-second cycle/10-second rest and Cargo transfer retained.
Native validation 22 poses: donor max error .5222 model units at rear hoof;
gate now proportional to size (.4 at .65 => .6154 at1.0), normalized error .3394.
This is documented tolerance adjustment, not a fix. Denser FBX sampling did not
improve it. Keep original step1. Added continuous quaternion signs/linear baked
keys; source integer poses unchanged. Same five static validator findings only.
Installed package-revision-06 and production CSC_ALL_Delivery FGX binaries.
User's CSC_TAILORS_Storage_L.ast and GEO/ANM descriptor bytes preserved. AST hash
5a3c13ac4b52223d77a36784c213e4925cb178648a3d28f19d398bcd0fbcfd33.
Production backup delivery-01/production-update-backup-20261008-194028;
approved previous version in before-scale-revision-06. Working Delivery blend
updated and Dropzone Tailors-Delivery-v6-2x.mp4/.gif saved. No UI automation;
user manually reopens CSC_TAILORS_Storage_L and selects Worked. Original source
masters untouched. Native exporter can resume using reexport_delivery_animation.py.

8 October revision 7: Requested cargo slide after landing implemented: settle42s,
hold to42.6, slide6modelunits right (view looking into bay) to44, withdraw inward
to45.5, descend hidden by47, underground return47-56. Same68s cycle/10s rest.
Cargo slide clearance checks21samples: level, unchangedrotation, no shell contacts.
26 native sampleposes inclslide; crane.01535, body.5222 normalized.3394, attachment
.07570. Same5knownstatic-scene findings. WorkingDeliveryblend saved; trial+production
installed, ASThash unchanged andmodelFGX byteidentical v6. Cliphash
f178b8342f6f07e04011cab48034fcb338b747ba8c0d7ea61a02ffe1f308fff5.
Backups before-cargo-slide-revision-07 and production-update-backup-20261008-200226.
Dropzone Tailors-Delivery-v7-2x.mp4/.gif, plus normal-speed close-up
Tailors-Delivery-v7-Cargo-Slide.mp4/.gif. NoUI; AE manual.
Generic thread learnings added to installed civ6-art references/art-animation-
coordinated-scenes.md and linked from art-animation-workflow.md; skill validator
passes. Covers sharedrig, cargo bone vsmesh, basis/UV/bind gotchas, road alpha,
hide/reset, scale, randomphase, registration and validation scope. No skillpush.

9 October v8: Henno found full-size workshop turns excessive. Tightened straight
depth55->44 and sweep to(-65,-217),(-71,-204),(-66,-187),(-60,-177), both directions.
Read-only candidates44/48/51 allpassed retained doorway surface checks;44 selected,
then fullrebake verified with actual gait. Door/storage/roadchecks passed. Route
length595.36->568.30 outbound,497.40->470.35 return. Native26poses crane.01535,
body.18593(normalized.12085),attachment.07256. Same5static-contractexceptions.
Installedpackage08 andproductionCSC_ALL_Delivery; ASTpreserved(modelFGXidentical),
cliphash218f7fac30b90c0296a508660e7bc791c93bc6e6ac0b2b624ebfc9460855450c.
Backupbefore-turn-revision-08 andproduction-update-backup-20261009-104952.
WorkingDeliveryblendupdated. DropzoneTailors-Delivery-v8-2x.mp4/.gif and closeups
Tailors-Delivery-v8-Workshop-2x.mp4/.gif. AEmanual,noUI. Donor1.0,bale.675,
cargoslideremains,68s/10s pause. Deliverycontextcachedoldstorage; separateinterior
source reworknotregeneratedoroverwritten, productionstoragegeometryunchanged.

9 October v9: fixed missing right sled runner reported from behind. Our Cart>0.5
vertex deletion had removed 12 runner vertices/triangles (original Mine runner
shares Cart weights). Restore original topology; remove only entire Cart-only
components, using coincident seams for selection connectivity. Existing faces,
positions, UVs and weights preserved. Source496->508vertices, native490->508,
triangles414->426. Native checks pass using unchanged v8 clip hash218f7fac...
Production/trial geometry and Working Delivery blend updated. User's current AST
hash daa45c20ddc6bc5fa58aad2887e1012fe1c8103a83a166be910d2bf937f033a3
preserved (user had edited it since v8; did not revert to old hash). No animation
or attachment edits. Backups before-runner-repair-09 and
runner-install-backup-20261009-112711. Both rear views of reimported FGX inspected
with backface culling; Dropzone/Tailors-Delivery-v9-Runner-Repaired.png. No AE UI.

Later9Oct: Henno deleted TEST assets/animations/material. Removed12missing
Content entries fromciv6proj; zeroexplicitmissingreferences aftervalidation.
No currentAST/XLP/ArtDefneedsCSC_TESTfiles. ProductionALL_Deliverypairs intact.
InternalCSC_TEST_TAILORS_Delivery_Rig isstillrequired andpreserved. Oldtrial
geometryfiles remain butarenotproductiondependencies. No fullbuildrun;
don't restoredeletedtrialswithinstall_storage_delivery.py infutureupdates.

9Oct rigrename: user explicitly requested CSC_ALL_Delivery_Rig. Installed native
model/skeleton/rootbone + cliptrackgroup/roottrack rename, GEO and ASTCargo binding.
CompleteCN6 and2041frames*32bones NA2 identical afteronlyname substitution.
SavednativeexportBlendrenamed incl civ6_root_name, posesunchanged; authoredworking
blends containednooldname. Exporter/template defaultsupdated. Backups/reports in
delivery-01/production-rig-rename. Modelhash7f26bb68e19f04986652eb079552b1895319b9bad674647ace50392e3f63e8fb,
cliphash747ffdebd7d52b91829d9d16d593aa9a11abb5c7391ebee1d97b7e74a2ee7f01.
EarlierinstructiontokeepTESTrig is superseded. No retiredTESTfilesreinstalled.

10 October v10: completed the coordinated 0.9 storage/crane refit. Narrow gabled
front anchored at (-17.6548443,126.5827637,0); supersedes initial own-origin pivot.
Donkey/sled stay1.0. Cargo .8 selected from 481 lift/swivel/slide poses with at
least .5 side clearance; production AST only Cargo scale changed, other settings
preserved. New hook position drives stop; hoist height uses actual crane scale.
Half-second departure/arrival distance easing fixes native DonkeyPath error .10148
without relaxing gates. Final native crane .01371, donkey .48724 (normalized
.31671), attachment .01287. Door/storage/road/slide checks pass. 68s/10s pause.
Installed buildingFGX/GEO, delivery model+clip FGX, working Delivery Blend; retains
ALL rig/mesh names and repaired runner. No retiredTEST runtimefiles restored.
Backup/evidence delivery-refit-20261009/production-backup-20261010-080107 and
production-refit-check.json. Updated crane/building masters and current context.
RuntimeAO2 already refreshed after interior bake. Preview v10 videos/GIFs in
Dropzone, fullcycle2x and normal-speed loadingbay. NoAE/UI/cook/game check.

10 October v11: user approved option1, a second shared attachment bone for cargo
that tilts a full90 degrees. Added Cargo_TipUpright; calibrated current production
CSC_BAKERS_Flour_Closed (Bakers_Flour_FINAL source), AE scale1.0, zero offsets.
90->0 degrees during28..31s, compensation from actual mesh bounds maintains bottom
at cargo height. Existing Cargo bale remains unchanged in AST at.8. Rig now33bones.
Changed reset to one continuous rightward slide42.6..45.5, corner worldXY
(-31.0275612,131.5083923), then concealed descent45.5..47. Removed old intermediate
6unit target and subsequent left/inward withdrawal. All crane/donkey path poses
exactly preserved;68s/10spause. Lift/slide clearances526poses pass for bothprops.
Native attachments260poses max<.025 (gate.08); crane.01371, donkey.48724 samev10.
Native reset occlusion passes bothprops over45 long-side view directions
(+/-35deg azimuth,25/40/55deg elevations), every descent frame. Not an all-orbit
guarantee. Final saved WorkingBlend static validator has same5 established
animated-contract findings, no new errors; targeted animation gates pass.
Published modelFGX/GEO+clipFGX; ASThash18ad951e... preserved, no TEST runtime restored.
Backup delivery-reset-20261010/production-backup-20261010-113402. Sourceworking
DeliveryBlend updated; hidden optional REVIEW_Closed_Sack_TipUpright, texturesfixed.
Normal generator/exporter knows newbone; oneoff update_delivery_cargo_motion.py
restores pre-v11 backup, do NOT rerun after later user edits. New rightcorner is
placement-specific: update withfuturebuildingrefit. Dropzone v11-Sack-Lift and
v11-Hidden-Reset MP4/GIF normal speed. No computer use; manualAE/cook/game next.

10 October v12: loading plate was axis-aligned, runner beams yaw-3.77797deg.
Rotated 8 added vertices and recentered Y-5.2 -> -5.89104. Original500 vertices,
weights, allUVs/topology preserved. PureCart skinning drifts1.69deg duringgait;
pureSledge_R residual.33deg. Uniform85%Sledge_R/15%Cart keepsplate planar and
followsrunneraverage with max.02810deg across340poses. Generatorhelper updated.
Savedsource/nativeexport/WorkingDeliveryBlend updated. Nativegeometry-only roundtrip
passes, workshop/storage clearance pass. Same5staticvalidatorcontractfindings.
Native top/rear images visuallychecked, inDropzone Sled-Deck-Aligned-Top/Rear.png.
Published only Geometries/CSC_ALL_Delivery.fgx; AST/GEO/ANM/animationbytes preserved.
v11cliphash4432edd6726dd4083a18447a84915fe249846837c4056d7f901f78a181731789.
Evidence/backups delivery-deck-20261010 inclproduction-check.json. NoUI/cook/game.
