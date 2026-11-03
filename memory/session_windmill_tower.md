# Windmill plaster tower — 21 October 2026

CURRENT 26 October: tower bundled into ONE shared intact Wind Mill master plus
CON+PIL companion under BAKERS/Wind Mill. Both runtime variants use these geos;
extra props/material/state settings remain in AE. User explicitly standardized
onto regular layout, then saved new regular position (2.035524,-21.555544,-.136043),
Z-.731351, scale1.158080; final models use that latest position.
Standalone Tower AST+2GEO/FGX pairs archived Desktop/Archive/CSC-windmill-tower-bundled-20261026.
XLP114→113. Component tower source folder preserved. Native Turn ANM/FGX unchanged;
keep original internal model name Tower to bind clip (different model name caused
native SampleBone access violation in discarded staging). Root/Sails unchanged,
new static Mount + Sail_Pivot_Offset preserve original8s motion at placement scale.
Both savedmasters/exports/rigs verified, all241frames matched<.000076; base stays
static. 569 other runtime files unchanged; both cooks pass RigidModel24. Native
vertices2512intact/2751CONPIL, advisorywarnings only. LiveAE/game unverified.
Durable contract project/docs/art/windmill-tower.md. OUT Desktop/Codex/Windmill-bundled-tower-20261026.
Legacy CN6 importer duplicates final triangle per mesh: new worker retains imported
rig axes but reconstructs exact mesh topology from native JSON before saving.
Earlier standalone tower delivery details below are historical.

Latest follow-up24October r044: removed two cloth-covered rungs per blade at radii
23.6/39.2, eight total. Keep4visiblefrombothsides/blade (8,15.8,31.4,48.2). All
retainedgeometry/weights/UV1/3 unchanged. RebakedsailAOonly; surface/tower/CONPIL/
placements/8sclip preserved. 398v388f source sails;1050v592tri native sails,
1584v totalintact/1034CONPIL. Source/native/motion241/clearance/cookPASS,
frontbacknativepreviewinspected. Installedmaster/CN6/FGX/GEO/AO r044; liveAEpending.
Evidence/backups Desktop/Codex/windmill-visible-rungs-20261024.

Latest, 24 October: split each blade into two separate textile panels with exposed
inner/middle/tip rungs. Three rungs thickened 1.55->2.2, tip radius47->48.2; cloth
ranges17.2..29.9 and32.9..47.0. Retains taper/weathered slot39. Sail mesh now462v420f;
native1178v656tri, total1712v intact /1034v CON+PIL. r043 only sail AO cell rebaked;
surface pixels, other AO, tower, CON+PIL, animation and AE placements unchanged.
Saved source0errors/warnings, nativebindings1each, bothvariant cookRigid24, native
motion241samples8s+clearance everyframe PASS. Preview inspected; liveAE/gamepending.
Installed master/CN6/FGX/GEO/sharedAO, focusedAEcache. Evidence/backups:
Desktop/Codex/windmill-split-sails-20261024. Source remains tower/Tower.

Latest, 22 October: r042 weathered sail cloth installed. ImageGen canvas in free
shared-props slot39, B/N/G/M registered, original ivory untouched. Only cloth UV1
translated; native geometry/bindings/weights/UV2/UV3 exact, 1,512 native vertices.
Saved-source validation 0 errors/warnings; both variants isolated cook pass with
RigidModel/24-byte. AO, CON+PIL, parent placements and eight-second clip untouched.
Current saved-assembly preview inspected, live AE/game pending. Evidence/backups:
Desktop/Codex/windmill-weathered-sails-20261022. Source remains tower/Tower.

User approved concept 03: plaster tower, green roof, ladder sails with cream cloth.
Requested animated new asset, ImageGen paint, storage-quadrant cleanup, all storage
UV exports, Bakers/Tailors B1/B2 XCF updates, shared G/M/N and strong normals.

Installed asset `CSC_BAKERS_Wind_Mill_Tower`, animation suffix `_Turn`.
Both Wind_Mill AST references replaced; every other placement/value preserved.
Source: Desktop/Working Files/3D Art/BAKERS/Wind Mill/tower.
New tower 1982 exported vertices; main+bespoke building2910 (advisory2200 exceeded),
full standard assembly4582 including reused flour/hay. Native ten-second motion
validated301frames,61collision samples clear. Final installed source validator0
errors/warnings. AE browser and XLP/project registration done; AE playback/cook/game
unverified, active AI game not disturbed.

Storage v3:30 translated occupied regions +128px ImageGen plaster. Four XCFs updated
with32layers and remapped current paths, legacy layers preserved. Nine native FGXs
UV1-only;12editablemasters (incl crane/delivery),8adjacentCN6 exports. Normals XY1.65
renormalized; softer registered plaster relief. Sharedprop texture pixels untouched.
Newasset has its own512AO geometry bake; existing quarterAO/UV2/UV3 untouched.

Canonical scalar DDS authoring headers differ from runtime Firaxis R8: compareRED,
not RGB! Explicit red extraction needed before texconv R8, since a few authored G
pixels have unequalRGB. Runtimeother3quadrants exact. Sourcewatcher recooked Bakers
B DDS afterpublish; top mip exact, binaryhash changed. Newblend must resolve all
imagepaths absolute beforecopy; final installedvalidator confirmsfixed.

Durable handoff: project/docs/art/windmill-tower.md.
Evidence/backups/rollbackmanifest: Desktop/Codex/windmill-tower-20261021.
Previews Windmill-Tower.png / Windmill-Native-Motion.gif.
Do not rerun migration/publication on alreadymigratedsources; auditinputs predateupdate.

Follow-up: user noted concept sails were wider. Installed 35% wider frames and
cloth with unchanged length, beam thickness, hub, tower, UVs and ten-second clip.
Focused script `project/tools/blender/widen_windmill_sails.py` is guarded against
reapplying. Builder also updated for regeneration. Five files replaced: master,
CN6, source AO PNG, native FGX, runtime AO DDS. Rotor-only AO bake protects tower
texels. Other runtime atlas/AST/clip/GEO hashes unchanged. Source validation has
0 errors/warnings; 301 native frames pass, 61 clearance poses clear.
Revision evidence/backup/install manifest and previews live under original output
folder's `wide-sails/`. Native export vertex ordering changes, so compare rotor
UV/weight attribute multisets rather than index-wise arrays. Live AE/cook/game
still unverified; no active test/build/deploy interrupted.

21 Oct follow-up: user approved inward sail taper and reported both parents crash
AE, screenshot missing Plaster_Tower geometry. Installed linear rail-spacing
taper (60% inner at radius5.5 -> full width at47.8), keeping outer cloth11.61,
cross sections/tower/hub/UVs/clip. Rotor-only AO rebake. Output taper-and-ae-repair/.
Confirmed GEO root bug: renderer turns legacy AssetObjects:GeometryInstance into
AssetObjects.GeometryInstance; integration serialized that unregistered type.
Canonical is AssetObjects..GeometryInstance. AE09:48Z log deserialize failure;
isolated malformed-root controls crash cooker. Writer fixed + regression.
Also removed unused plaster slot on rotor (old empty native0 / occupied1 butGEO1
group). Source/newFGX nowonegroup0; exact native geometry/UV/normal/rig unchanged.
CN6 material names authoritative; native materialBindingNames can be None.
Finalcounts428+1554=1982. Four final isolated fullassembly cooks pass(no entity
errors/error substitution), source0errors/warnings,301frames/61poses pass,2tests.
CAUTION early post-load intermittent cooker failures: three later oldgroupcontrols
also pass, so do not claim group cleanup proven causal or all AE crashes solved.
User must fresh-sessionreopen forliveAEacceptance; noUIautomation or gamedeploy.
Sourcewatcher rebuiltAO DDS; redpixels exact + compatibleR8header verified, kept.
Final6filepublicationmanifest includesintermediategroupbackups,protectedASTs/MTLs/
atlases/clip preserved; cache3entriesrefreshed. Nativecastertool saveguardfixed.

21 Oct ground/states follow-up installed: ground datum moved down27.2 to localZ0;
closed foundation continuesZ-30. Both parentattachment11 Z=-0.136043 (old-3.128043,
correction27.2*1.1/10=2.992); all otherparentASTbytespreserved. Newrebased10secclip.
CON+PIL geometry secondmodel in sameasset; roofless thick irregularshell withwindow,
noaxle/sails. Own2RuinMTLs/512AO. NativePROP_Scaffold_A attachment atuniform1.45,
syntheticNAMEbone/static, nativeConstructionvisibilityonly. NoSDKmeshchanges.
Ground/states outputs+22filemanifestbackups: windmill-tower-20261021/ground-and-states.
Nativecounts2154intact/480ruin; finalinstalledsourcevalidators0errors0warnings;
301motionframespass,61clearanceposesclear, fullbothparentisolatedcookpasses.
TEXwatcher updatesexporttimestamp/formatting, DDSredpixels+R8headercheckedidentical.
Newtools build_windmill_ground_states/integrate_windmill_ground_states/
readback_windmill_ground_animation/review_windmill_ground_states. One-timebuilder
asserts264rawtowervertices andnorebasedflag; doNOT rerunoninstalledsource.
PreviewsWindmill-{Worked,Construction,Pillaged}.png clipgroundonlyreviewmeshes;
exportfoundationintact. Pillagedburnshadernotrendered. LiveAE/gameunverified.
Sharedatlases/XCFs/PBRunchangedforthisgeometryrevision. Durablehandoffupdated.

21Oct sharedmaterial/scaffold correction COMPLETE: userUVmasters12:38/12:47
preserved(vertexpositions,face membership,weights,matrices,per-cornerUV1/UV3).
Use newest saved masters, neverrerunoldbuilder. Tower CSC_BAKERS_E(quartersAO2),
sails/smalltimber CSC_ALL_Props_01(sharedpropAO). AO2bottomrightcells
[516,976,580,1020] intact/[584,976,648,1020] ruin. PropsBakersStage2sails
[0,128,512,512], timber[384,0,448,128]/[448,0,512,128]. Alloutsidepixelsprotected.
NativeUV2alreadytoporigin! Occupancy usesv directly; renderflipsvforBlender.
Found404/436sailfacesinward; recalcclosedsolidsoutwardwithsameUVcornerassignments
fixesblackAO. Bake128Cycles/16AOrays/2xsupersample/2pxdilation/localonly.
NewCSC_Propsrelease2026-10-21_Shared_01_r036 Current+Releases+CURRENTverified,
cellpackerrebuildmatches. RemovednativePROP_Scaffold_Aattachment; exactScaffolding
meshfromLevel1/CSC_Level_1_S_CON+PIL.blend embeddedwithoriginal3UV/topology/native
Pillage_Construction_01material,uniform.7,staticRoot,Constructiononly.
BothparentASTbytesandclipunchanged. Native2154intact,1068CONPIL(480+588).
Evidence shared-materials/12filemanifestandbefore-library. Finalsource0err0warn,
23validationtests,301frames/61clearanceposespass,fullbothparentcookpass.
StatevalidatornowacceptsPillage_Construction_01ONLYwithexplicitmatchingExport
asset_id ending_CON+PIL; intactregressionretained. SourceuserBlendersstillopen,
mustreloadsavedmastersfornewUV2/materials. LiveAE/gameunverified.

22Oct wood revision installed: Desktop/Codex/windmill-wood-20261022,33file backups.
Same stable asset identity/sourcefolder. ImageGen Wood_B + registered Wood_H,
128sq slot formerlyplaster [512,614,644,746] padded; N gradientstrength12,
G/M updated, fourBakers/TailorsXCF plasterlayers REPLACED nothidden. Brace is
texture+normal ONLY perusercorrection. Otheratlaspixels preserved.
Tower meshXY1.15 + BACK*3 (BACK=.5,.866,0), fixedaxle256:264unchanged; Z0/-30.
Sails currentwidth1.35*1.5=2.025, .6innertaperretained. Clothradius29.8→14.2,
38.4→30.2533,47.8fixed; innerropes30.3→14.7. UV1/UV3preserved, AOrebakedexistingcells.
Sharedpropsrelease2026-10-22_Shared_01_r037. Both tower/source no newbracegeometry.
Scaffold has TWOsections in eachsource: removedtowerrearX>CENTER.x, leaving319v147f.
Basebuildingalsohadrear: avoidglobalLevel1edit by hideScaffoldinggroup inbothparent
ASTs and embeddedoriginalfront319v147f as RUIN_Base_Scaffolding with exactinverse
savedAEtransform. Bothfrontscaffoldmeshes Constructiononly, parentplacementsintact.
Finalnative2154intact/1118CONPIL; nativebonebindingsRoot/Sailsoneeach, GEOdouble-dot.
Latestciv6-art exportguidance READ: inactiveindicespaddingalreadycorrect0changed;
savednative readback passes, actualcookedformatsbothRigidModelstride24, fullcookpass.
301framesnativevsBlenderpass61posesclear. No deployedgamebuild/liveAEverification.
Tools revise_windmill_wood/finalize_windmill_scaffolds, windmill_wood_textures/xcf,
integrate_windmill_wood and verify_windmill_wood. One-timeauthoringguarddon'trerun.
ScalarDDS RGBCOMPARE RED ONLY: normalizedFiraxisR8 decodedRGB(R,0,0), sourceL(R,R,R).

22Oct later angular correction INSTALLED: windmill-angular-20261022/12files,
sharedpropsr038. Compared02-timber-towerconcept. Six broad tapered planar walls;
12oldfacets pairedcoplanar, originalringoddvertices becomeedge-midpoints,
evenverticeshexcorners0/60/...inRIGHT/BACKbasis, radialgaincos15/cos30 preserves
frontinradius. Centerretainswoodrevision+BACK3. Base/cap/roof/ruininnerouterallhex;
window/axleverticesfixed. EachflatfacegetsfullbracedwoodswatchUV1; UV3preserved.
Rebake4existingtowerAOcells only, sailsAOunchanged. Noartwork/XCFchanges.
CriticallegacyexporteraveragesNBTbysourcevertex: splitnoncoplanaredgesonexportcopy
AFTERsavingeditablemaster. ActualFGXwallnormaldotgeometric>.999999; nativecounts
2202intact/1154CONPIL. Sourcevalidatorstillestimates2154, actual48morecorrecthard
normalvertices,2over2200advisoryacceptedforreadability. BothcookedRigidModel24byte.
Nativeallnon-towermeshesbyte-semanticsidenticaltor037(sails,bothscaffolds), rigand
301frameclipunchanged;61rotationposesclear, isolatedbothparentcookpassed.
ParentsASTsunchanged, source0errors/warnings. Tools facet_windmill_tower,
integrate_windmill_angular,verify_windmill_angular. Currentr038hashesverified.
LiveAE/gameunverified. NeedreloadsourceBlenders/AEforshapeupdate.

## 22 October — black sail AO marks fixed

User disliked the rectangular black spots. Root cause: the 0.3-thick billowed
cloth had nonplanar quads with opposite front/back triangulation. The sheets
crossed locally, producing AO-black rectangles. UV2 interior overlap audit had
zero overlapping pixel samples; ivory artwork was clean. Explicit corresponding
triangles on both sides remove the crossing without moving vertices. 32 quads
split; source sails now 518 vertices / 468 faces, native still 1554 / 816 triangles.
Only existing props AO cell [0,128,512,512] rebaked. Front interior samples dark
below 128 fell from 480 to zero across 5876 pixels; rear frame shadows retained.
Canonical release r039 installed and hash-verified in Current/Releases. Four
changed files installed: intact blend/CN6/FGX and shared props AO DDS. All other
native meshes, skeleton, positions, UV1/UV3, source weights, parent ASTs, animation,
quarter AO and other props AO pixels preserved. Source validation zero errors and
warnings, all301frames,61clearanceposes, isolated both-assembly cook and actual
RigidModel24-byte records pass. Cache refreshed2files. Final preview inspected.
Evidence: Desktop/Codex/windmill-sail-cleanup-20261022. New tools fix/inspect/
audit/verify/integrate/review_windmill_sail_cleanup (inspect/audit use sail_ao).
Live AE/game still unverified. Reload asset and saved master to see correction.

## 22 October — user UV edits/window removal, simplified sail joints, r040

Current sources changed by Henno: tower260v151f, CONPIL shell156v110f, windows
removed; both had unused props material slot1 (all faces material0). User's
screenshot CN6ToFGX createMaterials index1 error matches empty slot. Removed it
from both saved masters; conversions now pass saved-FGX readback. Do not restore
old window/axle geometry or prior UVs. Sources were saved in Edit Mode: exit mode
in background copies BEFORE comparing UV data; otherwise stale mesh UV arrays
omit the live edit-mesh changes. Snapshot hashes matched; final preservation
check passes every tower/scaffold position, face, UV1/UV3 exactly.

Sails: trim all rung ends into rails; remove48 internal endcap faces and16 raised
tie boxes (128vertices). Keep all6 cross-rungs, rails, cloth and hub. Source390v324f;
native978v528tris (previous1554/816). Existing detailed source first blade baked
selected-to-active to eight long-rail face strips, high bevel .18/2segments,
480² B/N/G/M bakes. Existing ImageGen wood/rope reused; no newly drawn artwork.
Canonical props slot38 inner[772,516,892,636], 120²patch+4padding. Only128 rail UV1
corners remapped; other retained UV1/allUV3 exact, allcloth/rail/hubpositions exact.
Per-blade index bug caught and corrected before final export: local corners use
(index%114)%8, not index%8. Joint maps on allfourblades now consistent.

Both tower AO2 cells rebaked; sail props AO rebaked; obsolete NAME/RUIN_Timber
cells [384,0,448,128]/[448,0,512,128] clearedwhite+allocationsremoved. Shared r040
installed inCurrent/Releases; all other surface/AO pixels preserved. 16files
installed incl2masters/CN6/FGX/GEO, ownASTmaterialgroupcleanup, DDSandquarterAO2PNG.
ParentASTs and animation untouched; user current assembly edits preserved.
Native totals1512intact/1034CONPIL, bothcookedRigidModel24byte; eachmesh1binding.
Bothsource0errors0warnings,301frames,61clearanceposes,3statepreviews andisolated
bothparentcookpass. FocusedAEcache11files refreshed. LiveAE/gameunverified.
Evidence/backups Desktop/Codex/windmill-simplify-20261022; tools inspect/simplify/
verify_windmill_simplify_sources.py and integrate/verify_windmill_simplify.py.

## 22 October — Tower identity and eight-second rotation, r041

Active identity CSC_BAKERS_Wind_Mill_Tower, CON+PIL and Turn clip renamed across
52 active files, native skeleton/model/mesh names, Blender datablocks/properties,
source folder now BAKERS/Wind Mill/tower, shared Current library filenames and
manifests, tools/docs/memory filenames, project/XLP references and AE cache.
Existing unused legacy Tower asset/geometry backed up before replacement; XLP
duplicate collapsed to one entry. Historical Desktop/Codex outputs, release
snapshots and backups stay unchanged. No active old identity occurrences remain.

Rotation key times scaled0.8 from1..301 to1..241 at30fps, linear360deg/8seconds.
Native clip andANM both8seconds, 241sample readback maxerror.037026/.000260modelspan,
looperror.004746/.0000333span, fixedRootexact. Geometry/nativeSkeleton matchr040
exactly aftername substitution; bothmasters0errors/warnings; isolatedcookpasses,
RigidModel24byte counts1512/1034unchanged. Libraryr041 onlymetadata/names,pixels
bit-identical; allhashesverified. Sourcefolderbackup OUT/before-source;52file
backupsincllegacynamecollisions OUT/before-files; librarybackup OUT/before-library.
WindowsheldCurrent/atlas/sources/bakery-r024-baseline directoryopen, so directory
move failed after copy. Verifiedcompletebackup then restoredallstagedlibraryfiles
inplace; publication/finalhashverificationpass. Preferinplacefileswithbackup for
futureCurrentupdates rather thanmovingwholeopenfolder. AEcache17filesrefreshed,
oldnamekeys/recordsrenamed+deduplicated. LiveAE/gameunverified.
Evidence Desktop/Codex/windmill-rename-8s-20261022. Renamer tool has stage/check/
install/finish_library/cache/verify modes. Legacy one-shot authoring scripts have
renamed IDs but old workflow assumptions; don't rerun them on current sources.
## 30 October 2026 — human export animation repair

Current intact master is BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend, shared by both
historical variants. Human renamed armature to public asset ID; October 28 20:06
FGX/GEO export changed native model/root from Tower to Wind_Mill, breaking unchanged
Tower_Turn clip binding. Existing civ6_root_name was ignored by geometry exporter.
Fix: explicit csc_native_model_name=CSC_BAKERS_Wind_Mill_Tower in saved source;
maintained and installed io_export_cn6 now honors optional property only for native
root identity. File names remain CSC_BAKERS_Wind_Mill. Default no-property naming
control checked. Restart Blender/reopen source before next export to load addon.
Actual latest native meshes/UV1/2/3/NBT/weights/groups/triangles identical, no rollback.
All241 frames vs original combined reference max0.000170844; tower/base stationary;
original8sec animation SHA unchanged. Both ASTs point to shared repaired geometry,
both isolated cook pass RigidModel24. Candidate source validator0errors1budgetwarning.
Installed FGX/GEO, source and local export copies; other mod files hash-protected.
Evidence/backups Desktop/Codex/windmill-animation-repair-20261030. No AE UI/game
deployment or playback claim. Durable current instructions in windmill-tower.md.

