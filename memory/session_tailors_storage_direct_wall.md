# Tailors storage direct-texture trial — 2026-10-06

Henno authorized trial A: replace the current generated storage building's long
back wall with clean timber and two windows, one open-shuttered and one closed.
Trial B subsequently completed as an Astra/Sol comparison, with painted roof
variation and two parent critique rounds; see the follow-up status below. Do not inspect the pre-existing
CSC storage_l asset: it is explicitly excluded from reference for this session.

Output: `codex-outputs/tailors_storage_l/revision-06-back-wall/` beneath the Mac Play
workspace, main file `CSC_TAILORS_Storage_L_BackWall.blend`. Source revision 05
preserved. This is the newly created prototype, not the prohibited existing asset.

Imagegen made the facade B using an exact wall guide. Aligned structural H and
semantic G/M authoring inputs feed the CSC companion generator. Open shutters are
folded flat; open window is a painted recess, not geometric interior/parallax.
Only Shell face 0 (+X, opposite crane) and unused UV padding change. Geometry,
UVs, other owned B/N/G/M texels and AO/E preserved. Export stays 1499 vertices /
899 triangles. Saved-file authoring validator passes; Blender/CN6 checked, game
integration unverified. Visual review finds cleaner construction and stronger
registered normal detail. Henno called it encouraging, while noting the timber
style does not fully match the other walls; do not claim exact style parity.

Generator improvements: optional physical relief (`--height-scale` with
`--surface-size W,H`) and per-pixel `--gloss-map` / `--metalness-map` overrides.
Seven tests pass, with old/default output byte parity confirmed on trial inputs.
These controls do not infer structure or generate artistic character automatically;
authored height/masks and correct UV orientation remain necessary. Instructions
are maintained in `project/docs/art/textures-and-uvs.md`.


## Follow-up status — 7 October 2026

The paired direct-authoring trial is preserved under
`codex-outputs/tailors_storage_l/trial-B-comparison`. Astra finished at 1,481 actual
CN6 vertices, Sol 1,452, both with automated Blender/CN6 checks and two feedback rounds.
Parent judged Astra cleaner; Henno chose Astra. This selected the authoring agent,
not a proven winner between direct authoring and generated-high-poly/bake workflows.
The approved current Hunyuan-derived building still had richer character.

New authorized work under `codex-outputs/tailors_storage_l/astra-facade-upgrade`:
focused façade-quality test plus a taller usable upper storey. Henno's corrections:
preserve deliberately oversized Civ VI features rather than thinning them toward
realistic construction; upper loading bay needs credible capacity and must read as
an upgrade of storage_m. The old 109.42-unit benchmark was applied too rigidly.
Read-only permitted M source measures ~80 above ground with its buried ~21.6 excluded.
New grey section is ~147.36 high, loading floor 62.70, bay 47.92×41.93 with ~40 depth;
24×24×30 diagnostic cargo fits. Parent reviewed grey views and authorized the
façade-guided painting phase. The completed focused pass has 1,467 actual CN6
vertices / 735 triangles and passed saved-file automated validation with no UV2
overlaps. Parent reviewed mapped hero, left, rear, top and neutral relief. One new
imagegen call painted the real façade guide; the result still needed measured
landmark and individual shutter registration. The new façade is richer, while
other elevations retain older generic material treatment. No whole-building
parity or overall cost advantage over Hunyuan is established. Static unloaded
crane has space for hook retraction but no tested animation. Final bundle is
`astra-facade-upgrade/Storage_L_Facade_FINAL/`; REPORT.md records scope and limits.
Keep the old paired trial frozen.

Henno requested the complete best-theory workflow be consolidated in the CSC skill.
Canonical synthesis is now `civ-supply-chains/references/art-geometry-guided-authoring.md`:
optional 2D/diagram/rough 3D concept exploration, then actual geometry/UV guides for
façade painting, registered authored relief/material masks, geometry-only AO and
honest whole-route quality/cost comparison. It distinguishes evidence from hypotheses.
The old project `ai-3d-model-generation.md` was replaced by a concise tooling bridge;
conflicting swatch-only, blanket culling/welding and single-mesh rules were removed.
Do not reintroduce them. New shader-normal disconnection guidance is in the AO docs.


## Next correction — shared atlas and stronger shape, 7 October 2026

Henno judged the 147.36-unit follow-up too tall overall despite better upper-storey
proportions. He reaffirmed that the 109.42-unit benchmark is explicitly a two-storey
gabled building and applies directly here. New work: `astra-shared-atlas/`. Preserve
that useful section by overall uniform size reduction, then author selectively
chunkier/tapered/sweeping roof members and flared supports. The supplied Firaxis
positive/negative shape drawing (BuildingsProcess/media/image8.png) is direct style
authority: Henno says its character is missing even from our concept. Do not limit
shape to the too-regular prior concept. Show the character in grey before painting.

Both upper front and left loading openings should have open shutters and genuine
interior space. Henno subsequently clarified: the FRONT remains a modest WINDOW,
not another loading-bay-sized opening. Preserve distinct functions/proportions from
each side; share compatible material/surface parts without homogenizing façades. Internal goods are explicitly DEFERRED: later library prop scene;
no props, yard or crane load in this building pass. Use compatible geometry and
UV1 overlap to share entrance/arch/shutter/wood/roof modules, maintaining physical
texel density on a compact atlas. Independent UV2 stays unique for geometry AO.
Current delivery not yet complete; do not treat the previous tall pass as final
user acceptance.

Henno's next visual correction: the curved pass's bargeboards are TOO THICK.
Reduce their visible across-slope width roughly a quarter (and projection depth
modestly if needed), preserving sweep, taper, bevels and coherent junctions. The
positive diagram calls for shape character, not unlimited member thickness.


### Shared-atlas pass completed

Final saved building in `astra-shared-atlas/Storage_L_Shared_Atlas_FINAL/Storage_B.blend`
is 109.41999 units above ground, with curved/tapered roof
members, flared supports and the subsequently slimmed bargeboards. Front has a
modest open window; left has the large loading bay/platform/crane; opposite long
wall retains one open and one closed window. Interiors empty, props deferred.
Actual export is 1,594 vertices / 844 triangles (+94 / 6.3% above 1,500 target);
saved audit passes, no UV2 overlaps. One new imagegen call painted a shared module
atlas; B/N/G/M are 1024², geometry AO remains separate. UV1 overlap is deliberate.
Density is lower than prior2048 atlas (roughly roof6.5 vs9.7, walls6.2 vs7.1 px/unit
in initial parent mapped audit), so do not claim unchanged pixel density or
universal workflow superiority. Final report contains the exact delivered paths
and measures. No game/animation validation. Original CSC storage_l never used.

The exact Firaxis positive/negative roof/post shape illustration is now bundled at
`civ6-art/reference-images/shape-marble.png`, linked from art-direction-synthesis.
CSC synthesis now explicitly applies the two-storey109.42 scale to comparable
buildings, plans UV1 reuse while preserving distinct façade functions, and records
that geometry-guided painting can require region registration.


## Storey construction concept — pending review

Henno likes the shared-atlas model but wants the continuous ground-to-roof timber
surfaces broken into levels, with a horizontal floor division and potentially
different upper/lower wall materials. Requested a concept FIRST. Generated from
the latest `astra-shared-atlas/renders/front_left.png`: stone lower storey, oak
floor band and timber upper storey, saved at
`concept-storey-division/stone-ground-floor-concept.png`. This is a proposed
material/construction edit only; no Blender changes or masonry approval inferred.

Henno liked the masonry-storey concept and requested different stone sizes for
corner stacks versus wall infill. Concept v2 uses large dressed corner blocks and
smaller staggered infill courses, preserving the doorway stones. Latest concept:
`concept-storey-division/stone-ground-floor-concept-v2.png`. No mesh changes yet.

Industrial-era concept requested next; generated from masonry conceptv2 at
`concept-industrial-era/industrial-storage-concept.png`. Preserves two-storey
T silhouette, small front window versus left loading bay, two stone sizes and
Tailors purple roof. Proposes iron jib/chain hoist, riveted platform brackets,
metal roof flashing/gutters, glazed front joinery and finished timber. Concept
only; no model/rig modification or user approval yet.

Henno corrected the Industrial direction: RED BRICK upper floor, rather than
timber upper walls. Latest Industrial concept is
`concept-industrial-era/industrial-storage-red-brick-v2.png`: red brick upper
walls/gables, stone lower level, purple roof and iron handling equipment.
Earlier timber Industrial concept is superseded for wall-material direction.
Concept only; Blender remains unchanged.

Industrial rooftop correction: ridge beams stay DARK PURPLE PAINTED WOOD,
not metal flashing/metallic beams. Latest concept:
`concept-industrial-era/industrial-storage-purple-wood-v3.png`. Retains red-brick
upper storey, stone lower storey, iron hoist/platform hardware and gutters.


## Return to Astra Blender build — masonry/crane revision

Henno explicitly asked Astra to implement the Medieval/Renaissance stone-and-timber
conceptv2, ending the Industrial concept tangent. New folder `astra-masonry-crane/`.
Use `concept-storey-division/stone-ground-floor-concept-v2.png` as architecture
authority and frozen shared-atlas blend as model baseline. Preserve109.42scale and
latest restrained bargeboards/open small front window/distinct loading bay.

New required corrections: remove false dark blocking panels at BOTH ground entrances
and provide a sensible visible interior; move medieval timber crane swivel to head
of RIGHT loading-bay jamb so it lifts outside then turns inward away from viewer;
keep crane mount/arm/hoist parts separated with meaningful pivots, animation deferred.
Make both dark-purple wooden ridge beams solid continuous members without dark
transverse breaks. No Industrial brick/metal crane in this build; no goods/props.
Current revision in progress, not completed at this note's writing.

Henno confirmed interior scope: very rough inward-facing walls/faces, minimal
supporting room geometry rather than a detailed interior.

Latest explicit correction: upper floor needs NO underside. Add only interior
faces a player can see through openings; omit hidden ceiling/underside geometry.
This supersedes the earlier assistant suggestion to include an underside.

Latest ground-floor correction: Henno says the floor should NOT be geometry,
perhaps a decal. Remove the room ground-floor faces and let terrain show through.
A decal is only a possible later treatment, not currently requested. Keep rough
inward-facing walls/reveals. Elevated loading platform remains structural; still
no upper-floor underside. This supersedes the earlier visible ground-floor boards.

### Completed masonry/crane Blender revision

Frozen handoff: `astra-masonry-crane/Storage_L_Masonry_Crane_FINAL/Storage_B.blend`
(and CN6, external maps, report). Actual1696 exported vertices /900triangles,
196 above1500 (13.1%). Height109.42. B/N/G/M1024x2048 (double prior atlas allocation);
AO1024sq, baked from geometry with shader normals disconnected. Saved validation
passes; UV2 has no positive overlap. Parent final hero/256 review passed.

Both ground entrances open to terrain: NO ground-floor geometry/decal, inward
wall faces retained. No upper-floor underside. Stone lower walls/large quoins,
timber floor band/upper storey, continuous purple timber ridges. Medieval timber
crane separated at right bay jamb; sampled0to-130deg swing clear, -135deg contacts
jamb and is excluded. Parent inspected3 static poses; animation/cargo remain
unimplemented. No props, original Storage_L, Industrial parts or game integration.

Final blend SHA256:
`ae78f1b56c5622cd5cb918d57fef7765deb202d1bc59f7aaddf384983299c5b7`.

### Roof trim colour refinement — in progress

Henno requests bargeboards match the purple ridge timber, with both darker still.
Astra applying a material/UV-only revision from frozen masonry/crane final.
Deep muted plum trim; warm structural wall timber, floor band and crane retained.
Geometry/UV2 should remain unchanged; no ground floor or upper-floor underside.

Roof trim revision completed: `astra-dark-plum-trim/Storage_L_Dark_Plum_Trim_FINAL/`.
Bargeboards/fascia and ridge beams now share deep muted plum (B median68,45,82),
visibly darker than tiles; grain/highlights retained. Parent reviewed both heroes.
Dedicated trim atlas region preserves warm structural oak. Geometry/transforms/UV2
identical;1696vertices/900triangles; AO retained unchanged; CN6 refreshed forUV1.
New blend SHA256 `c76278d0fc23b262d15f61f5e095fe0b51dc26d52c8f2ba84958fcad547ab10e`.
Previous masonry final preserved.

### Roof edge refinement — in progress

Henno likes dark plum trim but rejects purple horizontal skirting around tile
eaves, highlighting the concave T junction in the annotated Oct7image. Remove
the horizontal skirts; align/tighten tile-edge geometry and taper its exposed
underside inward toward walls for a receding overhang. Apply consistently at
analogous corners. Preserve shaped sloping bargeboards and ridge beams in dark
plum, existing silhouette/scale and all non-roof geometry. A thin visible roof
edge return is distinct from the still-forbidden upper-floor underside.
Astra revising from frozen dark-plum model; no new imagegen requested.

Roof edge revision completed: `astra-receding-eaves/Storage_L_Receding_Eaves_FINAL/`.
Removed three vertical purple skirts; all five lower tile edges have thin lips
and consistent receding returns (0.59unit lip,3.71unit inward offset,2.08unit
total drop), shared concave corner coordinates. Six economical end caps close
bargeboard/return seams. Sloping dark plum bargeboards/ridges retained. Parent
reviewed both heroes and junction close-ups, including seam correction.
1742actualCN6vertices/920triangles (+46/+20 vs prior;242over1500). Geometry-only
AO rebaked; zero mesh errors/UV2 overlaps; final bundle reopened. Nonroof
geometry/transforms/UV1 identical; crane clearance checks remain clear.
Final blendSHA256 `edc9706708e5aeb974f2a6be8c11dd6f9ae46c2f4cc7cf4a1f7e17fc55eba6ca`.

### Underground foundation — requested

Henno now asks to add the buried foundation. This supersedes the earlier no-
foundation instruction for the exported model, while foundation-hidden icon/
concept review still applies. Astra adding21.6units below groundz0 using the
previously measured Storage_M depth, following T walls and corner projections.
Above-ground height109.42 remains unchanged. No slab/apron/top-floor cap, no
upper-floor underside or above-ground entrance blockers. New named foundation
geometry included in counts/export, separately hidden only for visual review.

Foundation revision completed: `astra-buried-foundation/Storage_L_Buried_Foundation_FINAL/`.
21.6units below ground, compact T union including six quoin projections;32
vertical uncapped faces,128vertices/64triangles. Total1870/984 (aboveground
1742/920 unchanged);370over1500advisory. Aboveground height109.42; total131.02.
Foundation included in Export and excluded only by named Review collection.
No floor/slab/top/bottom cap. Geometry-only AO rebaked with foundation present.
Initial ridge banding resolved by combined fresh AO target, explicitUV2 and
disconnected AO+Normal shader inputs; individual cause not isolated. Corrected
hero reviewed, saved checks pass, zero mesh errors/UV2 overlaps, bundle reopened.
Final SHA256 `6cc976c5c5d0c904e3a5e517dc28f16a793b458faafa05a77007c1d858835bf0`.
Earlier candidate d456a06d withdrawn; not an approved handoff.

### Door thresholds — requested

Henno explicitly requests geometry for the thresholds to close the foundation
edge at both ground entrances. This is a narrow exception to no ground-floor
geometry: shallow stone sills through the doorway wall depth, no full interior
floor, slab or apron. Tiny lift abovez0 allowed to avoid terrain coplanarity;
most thickness belowgrade. Current building geometry remains109.42high; user
changed the skill working reference to110 without asking to rescale this model.
Astra implementing from frozen buried-foundation final.

Threshold revision completed: `astra-stone-thresholds/Storage_L_Stone_Thresholds_FINAL/`.
Two shallow stone sills: top+0.3, bottom-1.5, width19.57/depth6.23, bevel0.30,
ends tucked intojambs, hidden bottoms/endfaces omitted. Existing maps reused.
40vertices/20triangles added; total1910/1004 includingfoundation (410over1500).
All prior geometry/transforms/UV1 unchanged; roof109.42 andfoundation21.6 retained.
No fullfloor/apron/upperfloorunderside. Corrected geometry-only AO context reused;
saved validation zero mesherrors/UV2overlaps; parent reviewed bothcloseups andhero.
Final SHA256 `ab6f033588c686c84f9e4b810855b0282ad35816f913c56f2723ca70ccc3ed65`.

### Shared quarter atlas feasibility — read-only audit

Henno now explicitly permits inspecting old CSC_Storage_L for material/atlas
replacement; former exclusion superseded for this purpose. It uses quarterB
(loaded Bakers variant) and commonN/G/M1024sq; AO2viaUV2. OldL UV1 ~82.6k
rastertexels, ~5.1k overlap intactS/M; ~77.5k unique relativeS/M only. New
UV1 samples~1.282mtexels on1024x2048. Direct squeezing implies~4xlinear detail
loss before optimization. Recommendation: retain dedicated material now; shared
integration should be coordinated material-kit/atlas revision, auditing states
and allquarter variants, with separateAO/UV2 allocation. No assets changed.
N/G/M/AO/E allverified connected in finalBlend; N hasstrongstructuralrelief.
PNG authoring complete, destination DDS/TEX/normalconvention/game notverified.
Details: `atlas-integration-audit/ASSESSMENT.md`.

### Dedicated compact material — user decision/constraint

Henno does NOT expect to rework other buildings now. Do not justify this asset
on a future family overhaul. Permitted routes: surgical sharedatlas insertion
or dedicatedmaterial. Hard active texture cap for this building:1024square,
or512x1024 ifrectangular. Parent chose dedicatedmaterial afteroldatlas audit.
Astra reducedB/N/G/M to512x1024; AO stays1024square, E8square. B filtered inlinear
light, signedN filtered/renormalized. Geometry/allUVs unchanged, CN6 identical.
Parent before/after768and256 review passes: slightfinegrainsoftening only;
structuralrelief remains readable.75% fewerB/N/G/Mtexels. Finalbundlepending.

### Shared storage quadrant — latest direction supersedes dedicated plan

Henno now explicitly chooses a new shared storage quadrant containing S/M/L and
a reusable lean-to. L should initially populate~40–50%; revisitS/M with geometry
roughlystable, geometry-guidedpaint andUVupdates, reusing stone/wood/etc modules
where suitable. This supersedes the earlier expectation of nootherbuildingwork.
Do not continue dedicatedmaterialasfinaldirection; compact512x1024L remains
useful fallback/reference. Atlas dimensions asked:2k atlas/1kquadrant versus
existing1k atlas/512quadrant, responsepending. Preflight underwayread-only.
Likely shelter master: `Props/CSC_Storage_LeanTo.blend`, with CONPILvariants.
SharedUV1doesnotimplysharedAO: independent model UV2 allocations required.
Workfolder `shared-storage-quadrant/`; no productionatlas/sourcewritesyet.

Confirmed byHenno: entire sharedstoragequadrant512x512, existingdistrictatlas
1024square.512isplenty atgamescale; prioritize reuse/gameview overclose-updetail.
No2048atlas option. InitialLsharedmodules provisionally256x448=43.75%quadrant,
leavingright256strip/bottom64strip forS/M/lean-to uniqueart. AOallocationseparate.
Plan/stageoutputs onlyuntil familyintegrationready; preserveotherthreequadrants.

### Shared quadrant L checkpoint and approved hybrid family migration

L-staged now validates at1910 exportedvertices/1004triangles with geometry,
transforms and silhouette unchanged. Commonkit256x448 occupies43.75% of512².
All467faces map into moduleinnerrects with2px dilatedgutters; AO320² independently
allocated. B/N/G/M/AO decodedpixels outsideBRquadrant identical; E256² entirely
unchanged and UV3 samplesverifiedblack. Parent reviewed before/after256 and768:
game-scale readability passes; fine-detailsoftening accepted at this density.
Workpath `shared-storage-quadrant/L-staged/`, registry/diagram/report included.
Savedblend audit SHA256ee99ddecc67fa1a063586108d6ac0f3b5441259eeb0234e1b5a65b0837af0d86.

Henno approved hybrid: common newL materials acrossS/M/lean-to; transfer useful
legacy distinctive details (M latticewindows etc) asbasecolour withoutsceneAO
orlighting; repaintonlyweakgame-sizedetails. PreserveS horizontalboards and
allsourcegeometry/transforms/pivots. Astra continuing normal-statefamily staging
withindependentAO; originalsource andproductionatlases untouched. Construction/
pillage andpalettevariants remain coordinatedintegrationdependencies.

Henno explicitly authorized in-place S/M/lean-to updatedBlendpublication: rename
oldversions withdatedsuffix, newversions retaincurrentcleanfilenames. Preserveold
sharedmaps; publishnewversionedtexturefolder andbindupdatedmodels to it, keeping
backups/untouchedconstruction-pillage assetsfunctional. Parent handlespublication
afterstagedvisual/technicalvalidation; no needrequestapprovalagain.

LATEST publication correction: newtextures takeofficialcanonicaldirectorynames
forAE; oldmaps archived andbackupblendsreboundtoarchive. Versionedactiveatlasplan
isrejected. ParentcheckedAE.tex: B/N/G/M sourcescanonicaluncompressed32bitDDS,
AO2sourcesPNG. Sourceformatconversionprovenpixel-exactretainingDDSheaders.
OnlyS_CON+PIL,M_CON+PIL,genericLeanTo_CON+PIL referenceoldsharedlayout; keep
thoselegacybindingscompatibleviaarchiveuntilUVmigration,reportstates/runtime
stillpending. No productionwrites yet.

Afterinterruption, Henno saysfinishup; explicitlyacceptsTailorspink-purplefor
allotherstorage roofs now andwillrecolorlater. SkipBakersgreenpalettetransfer.
CanonicalBvariants usecommonnewstoragequadrant, otherquadrants unchanged.

### Normal family published — 7 October 2026

Authoritative handoff: `shared-storage-quadrant/Storage_Family_FINAL/`, matching
clean-name sources now published toWorking Files/3D Art Storage_S,Storage_M,
Storage_L andProps/CSC_Storage_LeanTo. CanonicalB/N/G/M DDS, AO2PNG and3B XCFs
updated. Otherthreequadrants pixel-exact; allBstoragevariantsTailorspink-purple
peruser. Materialarea121584/262144=46.38%. IndependentAO L320²/S180²/M180²/
LeanTo128². FinalAO SHA256cbff598e39f33c496546c805cc55c9e4b9f0b0f9859c91ddcb170b34e221a376.

Counts(serializedCN6): S917/451tri, M951/494,L1910/1004,LeanTo358/178. Removed
58S+4LeanTo inheritedzero-area triangles; survivingpositions/allUVsexact.21S
foundationvertices gotmissingstaticweights. Allsavedvalidatorspass; UV2overlap0.
Canonicalbindingsfinalsaved/reopened, then23livefilespublished/hashverified;
35archivedfiles includeoldmaps, datedreboundblends, raworiginalblends andoldCN6.
Backups `_pre_storage_atlas_2026-10-07.blend` referTextures/Archive/
Storage_Atlas_Pre_2026-10-07. ThreeCON+PILcleanblends reboundtoarchiveonly,
notUV-migrated. OtherCON/PILdecalfiles untouched.

Parent correctedprovisionalLeanToCN6frame usinglivecanonicaldecode_blend.py: all
staticmeshes exportworldcoordinates withidentityskeleton. LeanTooriginalroot
translation7.661,-26.192,-29.449 isaccounted inexport, NOTapplied inBlend.
Exportbounds nowz0.06199..46.78342; otherCN6sbyteidenticaltostagedexports.
Stagingreport'sarmature-localframeis supersededbyFINALREADME/cleanbindingsreport.

ThreeB XCFs preservepriorlayers/paths andaddtopstoragegroup withseparateroof,
ridgeandtrimrecolourlayers. Compositequadrantpixel-exacttonewB; outsideunchanged.
Familycommon-scale/game256visualpass. Productionreceiptandhashes inFINALreports.
CON/PILUVmigration,FGX,AEreimport/cook/gamechecks stillpending. Noimagegencalls
forfamilymigration.

### Saved entrance orientation — user request

S root rotated−90°Z andM+90°Z aroundnativeorigin; both nowexposeentrances
on−X/−Y sides likeL. ActualcleanBlendfiles changed, notonlyreviewcamera.
MatchedS_CON,S_CON+PIL,S_PIL_Decals,M_CON+PIL,M_PIL_Decals rotatedsameamount.
Geometry/allUVs/scales unchanged; normalexports refreshed; validatorspass and
counts917/451,951/494unchanged.9publishedfiles hashverified,9datedpre_orientation
backups. StateUVmigration/runtimeexports remainpending. CurrentFINALbundle
updated; oldreviewrenders archived inorientation/previous/final_renders.
Latestimage `Storage_Family_FINAL/renders/three_buildings_both_entrances.png`.
Orientationpublicationreceipt supersedesoldS/Mhashes; Large/lean-to unchanged.


## 7 October 2026 — storage family entrance/wear revision (published)

- Fixed S/M diagonal stone wedges from whole-triangle material classification by splitting only wall triangles crossing the original plinth line (S12.1/M18.4). Old vertex positions, saved rotations, native pivots/scales and silhouettes retained; interpolated UV2 keeps existing AO valid.
- Added shared rough fieldstone for S/M bases/feet and lean-to feet, leaving doorway surrounds dressed. Added restrained imagegen-painted material wear with registered existing relief.
- Added two tile-to-oak roof-return patches for the different terminal tile courses; actual ridge and gable boards remain plum. Atlas remains a512² storage quadrant in1K district maps; allocated143600px /54.78%, with all other runtime quadrants pixel-identical.
- Saved validators pass; UV2 overlaps0; geometry AO2 bytes unchanged. Actual CN6 vertices/triangles: S986/511, M981/566, L1910/1004, lean-to330/178. All runtime N/G/M available; new roughstone N uses authored block/mortar height through CSC companion generator, no runtimeH.
- Published clean normal-state blends/CN6 and official DDS/XCF locations. Prior textures archived at Textures/Archive/Storage_Atlas_Pre_Wear_2026-10-07; *_pre_wear_2026-10-07.blend backups rebind there. S/M pre-orientation normal backups also point at archived prior textures.
- Current portable bundle: codex-outputs/tailors_storage_l/shared-storage-quadrant/Storage_Family_FINAL. Previous portable release archived under wear-revision/previous-release. Current comparison: renders/three_buildings_both_entrances.png.
- Construction/pillage UV migration, FGX/AE reimport, cooking and game review remain separate unfinished integration work.


## 7 October2026 — final roof-edge / UV cleanup handoff

User requested visible S/M tile-to-wood on bargeboards, removal of L thresholds and foundation walls below doorway clear spans, then ONE facade cleanup before taking over editing. Completed: four compact vertical tile-to-oak strips; S wall/frame UV alignment; M gable patch rebuilt from current common materials in same UV footprint; L two threshold objects removed and doorway foundation gaps open to−21.6. L geometry-only AO rebaked through unchanged UV2 allocation. Atlas occupancy57.904%, still512square. Final saved validators/export checks pass. Counts:{'S': {'vertices': 895, 'triangles': 519}, 'M': {'vertices': 941, 'triangles': 590}, 'L': {'vertices': 1878, 'triangles': 988}}.

Final visual QA caught transition UVs spreading over broad roof triangles due shared mutable clipping records; restored original tiled-roof UVs before publishing. One cleanup pass is complete; further artistic UV work now belongs to Henno. Latest source files published under clean names; pre-eave backups use archived texture bindings. Current handoff in Storage_Family_FINAL/UV_HANDOFF.md and allocation_diagram.png. Prior wear release archived at eave-opening-revision/previous-release. Runtime/state integration remains outstanding.


## 7 October2026 — original-style timber wall island correction

User clarified the earlier cleanup was insufficient: whole architectural wall regions should form coherent UV islands over actual timber-board patches, and base stone should read as1–2courses. Compared archived S/M renders and source UV regions. Transferred original S horizontal boards and M vertical planks to compact new patches, strengthened joint contrast36% at seam centres, authored board-lap/recess height through CSC companion generator. Recovered wall faces misclassified as beams; continuous panel coordinates/seams replace per-face fitting. All current wood wall faces join the panels; the original-material evidence is required for recovering beam-labelled faces. Two-course base patch applies only rough base masonry, preserving dressed arch UVs. Geometry/transforms/roofUV1/UV2/AO unchanged. Atlas remains512square,67.67% allocated.

Final review corrected an over-broad stone-role selection that initially swallowed doorway arches and original-centroid selection that missed plain-wood triangles. Published only corrected result. Current portable bundle Storage_Family_FINAL; pre_wall_islands backups bind to archived texture release. Counts:{'S': {'vertices': 871, 'triangles': 519}, 'M': {'vertices': 990, 'triangles': 590}, 'L': {'vertices': 1878, 'triangles': 988}}. Full saved validation, island-continuity proof, original/render comparisons and texture alignment checks accompany handoff.


## 7 October 2026 — restored medium dark timber and darker shared stone

User requested darker posts/accents as in original M, and slightly darker stone. Added medium_dark_beam patch [768,864,1024,896] with inner [770,866,1022,894]; remapped 23 M framing faces (82 loops), leaving coherent board wall islands untouched. Darkened M gable framing and only wood in M barge-board patches; S framing and purple ridges stay as approved. Shared stone B is multiplied by 0.87. Registered relief/G/M and geometry AO preserved. Full geometry/transforms/UV2 audit exact; all four saved scenes pass validation. Runtime other quadrants pixel-identical; XCF storage composites exact. Allocation70.8% of 512square. Official sources and portable Storage_Family_FINAL updated; all four backups point to Pre_DarkTimber archived textures. CN6 counts: {'S': {'vertices': 871, 'triangles': 519}, 'M': {'vertices': 990, 'triangles': 590}, 'L': {'vertices': 1878, 'triangles': 988}, 'LeanTo': {'vertices': 330, 'triangles': 178}}.


## 7 October 2026 — medium upright corner post correction

User spotted diagonal dark posts on long walls. Four triangular corner faces (82/83/90/92) had been tagged as solid dark beam, so face boundaries became post silhouettes. Recovered them into coherent exterior long-wall islands 0 and 3. Added medium_post_wall [768,896,896,960], inner [770,898,894,958], cloning registered vertical boards with straight dark end strips. Shared physical projection across all panel faces keeps posts upright across triangles. Geometry/UV2 unchanged; saved validators and renders pass. Atlas73.9% of512square. Official files plus Storage_Family_FINAL updated; previous files linked to Pre_UprightPosts archived textures. Counts: {'S': {'vertices': 871, 'triangles': 519}, 'M': {'vertices': 984, 'triangles': 590}, 'L': {'vertices': 1878, 'triangles': 988}, 'LeanTo': {'vertices': 330, 'triangles': 178}}.


## 7 October2026 — medium shape and equal corner post width

7 October 2026. Long-wall dark posts now match the existing short-side framing: about4 units at the head and5.5 at the foot. Medium body length reduced5%; roof gains two support lines, a gently rolled slope and flared eaves. Feet flare modestly. Object scales/pivots/rotations remain native. The ridge height is retained; medium remains clearly taller than small.

The geometry-only medium AO was rebaked into its existing180-square UV2 atlas slot. Other AO pixels are exact. Wall materials and relief remain registered; other district atlas quadrants are unchanged. Storage still uses a512square quadrant,73.9% allocated. All saved scenes pass validation.

| Model | CN6 vertices | Triangles |
|---|---:|---:|
|S|871|519|
|M|1041|658|
|L|1878|988|
|LeanTo|330|178|

Height above ground: small: 60.18, medium_after: 80.00, large: 109.42.

Official clean models, exports, DDS/AO and XCF updated. *_pre_medium_shape_2026-10-07.blend backups bind to Textures/Archive/Storage_Atlas_Pre_MediumShape_2026-10-07. FGX/AE reimport, state UV migration, cooking and in-game review remain separate.


## 7 October2026 — large reuses medium timber

7 October2026. The new large building now uses medium_dark_beam for its structural frames and floor band, plus vertical_boards for upper wall infill and gables. Broad wall regions share planar mapping across openings and adjoining faces. Existing windows, shutters, crane, roof materials and stonework retain their treatment.

This is a UV1/material-reuse revision: geometry, transforms, UV2 and AO are unchanged. Existing B/N/G/M patches are reused directly; no extra atlas space or material. Storage remains within its512square quadrant,73.9% allocated. Texture files are byte-identical to the preceding release. All saved scenes pass authoring validation.

Medium retains the earlier fuller roof and corner posts, with height80 versus small60.18 and large109.42.

| Model | CN6 vertices | Triangles |
|---|---:|---:|
|S|871|519|
|M|1041|658|
|L|1878|988|
|LeanTo|330|178|

Clean official Blend and CN6 updated. Large backup *_pre_large_shared_timber_2026-10-07.blend binds to Textures/Archive/Storage_Atlas_Pre_LargeSharedTimber_2026-10-07. FGX/AE reimport, state UV migration, cooking and in-game review remain separate.


## 7 October2026 — medium projecting ridge

7 October2026. Medium now has a bevelled ridge beam 7.6 units wide, between small5.4 and large9.8. It projects about4 units beyond each prior ridge end. Its top is81.76units; body, eaves and roof slopes retain their approved dimensions. The existing plum timber patch is reused.

Only the old ridge faces were replaced. Existing non-ridge UV1/UV2/UV3 are preserved; new ridge AO faces fit inside old ridge allocations. Geometry AO rebaked into the existing180square M slot. Other atlas/AO regions remain unchanged. All saved scenes pass validation.

| Model | CN6 vertices | Triangles |
|---|---:|---:|
|S|871|519|
|M|1030|658|
|L|1878|988|
|LeanTo|330|178|

Clean official Blend and CN6 updated. Medium backup *_pre_medium_ridge_2026-10-07.blend binds to Textures/Archive/Storage_Atlas_Pre_MediumRidge_2026-10-07. FGX/AE reimport, state UV migration, cooking and in-game review remain separate.


## 9 October2026 — Tailor standalone lean-to remap

Updated the requested revision-10 standalone CSC_TAILORS_Tailor_LeanTo.blend in place, with a matching CN6. Material CSC_TAILORS_NE now uses canonical B/N/G/M/E and the shared shelter AO through relative paths to 3D Art/Textures. No atlas textures were altered.

The Tailor shelter is a rotated, uniformly 0.7-scaled version of the shared shelter, with one post/foot intentionally omitted. Transferred the shared UV1/UV2 only onto the existing Tailor surface, preserving that omission, original corner positions, object transform, source/instance identity and 154 triangles. No added boundary vertices. UV3 retained by original-face correspondence/interpolation. Serialized vertices increase from244 to301 because the current atlas/AO adds UV splits. No main Tailor scene or sibling variant was modified.

Added the standard Review scene/light setup and classified standalone master geometry as fixed_geometry for the current validator (original attachment_geometry role recorded as metadata). Saved-file validation passes. This does not constitute FGX conversion, cooking, state-material migration or in-game verification.

The previous master is CSC_TAILORS_Tailor_LeanTo_pre_shared_atlas_2026-10-09.blend beside the clean file, pointing to exact archived source textures under archive/pre-shared-atlas-2026-10-09/textures/. The release/ folder is a portable directory tree including textures. Renders and validation reports are alongside this note.

Output: /Users/henno.gous/Play/codex-outputs/tailor-leanto-atlas-remap-2026-10-09

## 10 October 2026 — Small/Medium CON+PIL atlas migration

Henno completed the preceding large-building edits elsewhere. This pass touched only
the official `CSC_Storage_S_CON+PIL.blend`, `CSC_Storage_M_CON+PIL.blend`, their CN6
exports, and the shared AO image. Both combined masters now use the current storage
quadrant through relative canonical texture paths. Existing mesh/material-group
identities, openings, original corner positions, rotations and sole skeleton bone
are retained. Coplanar UV boundaries separate the base stone from timber: 35 extra
editable positions for S, 50 for M, without changing surface coverage. UV3 is retained
and interpolated at those boundaries. Imported duplicate scaffolding weights for
the absent `Object19929` bone were removed; the current static `Bone` weights were
normalized to 1. No actions or animated bones existed.

The previous geometry AO content was resampled, **not freshly baked**. New UV2
reservations in the storage quadrant, top-left coordinates of the full 1024 atlas:

| Asset | Inner pixels | Outer pixels including 2px gutter |
|---|---|---|
| S CON+PIL | [782,884,890,1020] | [780,882,892,1022] |
| M CON+PIL | [894,884,1002,1020] | [892,882,1004,1022] |

Both regions were entirely white and outside the prior family AO reservations.
All pixels outside these rectangles and gutters remain identical. Preserve these
new allocations during later AO work. B/N/G/M/E were not edited. The portable release
allocation registry records `state_AO`. Existing state geometry was not reshaped to
match the intact Medium's later silhouette revisions.

The S floor's originally packed grounds map was extracted byte-for-byte to
`Storage/Storage_S/authoring-dependencies/DIS_CTY_AW_Grounds_B.dds`. Native scaffolding
material/UVs are preserved; Blender shows its existing untextured placeholder.

| Combined export | Vertices | Triangles |
|---|---:|---:|
| S building | 1286 | 722 |
| S floor | 14 | 10 |
| S scaffold | 319 | 147 |
| M building | 1252 | 709 |
| M scaffold | 269 | 125 |

Saved and published files were reopened and checked. Both CSC validators have zero
errors/warnings. Front/rear pillaged and scaffold construction previews reviewed.
Archived Blend/CN6 files have `_pre_atlas_remap_2026-10-10` beside their clean masters;
the Blend backups retain pre-7-October archived map bindings. Previous canonical AO
is in `Textures/Archive/Storage_State_AO_Pre_2026-10-10/CSC_Atlas_AO2.png`.

Separate S_CON, PIL decal files and shelter CON+PIL were outside this request and
remain unchanged. FGX conversion, Asset Editor state/material wiring, cooking and
in-game verification are still separate integration steps.

Output: `/Users/henno.gous/Play/codex-outputs/storage-conpil-remap-2026-10-10`

## 11 October 2026 — Small entrance wall UV and AO repair

Repaired the user-edited official `Storage/Storage_S/CSC_Storage_S.blend` in place,
plus its CN6 and Small's rectangle in canonical `Textures/CSC_Atlas_AO2.png`.
The edited mesh had 282 coincident opposite-facing polygon pairs and 119 zero-area
bridge polygons, consistent with an applied zero-thickness Solidify. Removed the
extra shell/bridges using prior normals as orientation reference. Kept all retained
vertex coordinates exactly, including the user's shape edits. 294 editable vertices,
283 polygons, 867 serialized CN6 vertices / 515 triangles. No validation errors or
warnings. This is authoring/CN6 verification, not FGX/cooking/game verification.

Restored continuous horizontal boards on the long entrance facade. At Henno's
request, its broad end posts use vertical timber grain matching the other walls;
the user's existing post UVs (source faces 333/451) already provided that treatment
and were retained. All unaffected retained UV1 and all UV3 corners match his edited
file. Other successful gable, stone and roof edits remain.

Fresh geometry-only AO: UV2 explicitly selected, normal input disconnected during
bake, 128 samples, distance 14.7, 180px tile. Retained the user's UV2 chart layout with
a uniform safe fit into Small's existing inner [840,514,1020,694] reservation; outer
[838,512,1022,696]. Updated only that rectangle/gutter and restored 14 pixels of the
user bake's spill above the slot from the known 10-Oct atlas. All other pixels match
his current atlas exactly; B/N/G/M/E unchanged. CON+PIL reservations preserved.
Saved AO node active, active UV2, clear disabled and margin 2; material rendering
uses explicit UV1 and NormalMap UV1. For future geometry-only AO, disconnect the
material normal input during the bake and explicitly select UV2.

Archived pre-repair Blend/CN6 and frozen maps under
`Storage/Storage_S/archive/pre-uv-ao-repair-2026-10-11/`; archive Blend uses its local
`Textures/` folder. Published clean Blend uses canonical `../../Textures/` bindings.
Both were reopened and verified, including external image hashes. The archive
contains the user's pre-repair mesh, not the older .blend1.

Output, front/rear previews, AO comparison and publication receipts:
`/Users/henno.gous/Play/codex-outputs/storage-s-uv-ao-repair-2026-10-11`.

### Same day — match Small CON+PIL to the repaired intact mapping

At Henno's request, updated `CSC_Storage_S_CON+PIL.blend` and matching CN6 in place.
Transferred 243 exact/coplanar surface mappings from the repaired intact Small;
front wall uses coherent horizontal boards and broad vertical timber end posts,
with coplanar UV boundaries following the intact posts' sloping inner edges.
Broken roof rafters/cut surfaces retain their appropriate existing timber mapping.
All original positions and transforms retained; 11 extra boundary vertices, no
surface shape change (area delta -0.0000387). Removed collapsed/sliver faces while
constructing the boundary polygons. 426 editable vertices / 358 polygons. Export:
building 1255 vertices / 668 triangles, floor 14 / 10, scaffold 319 / 147.

UV2 and UV3 retained, interpolated only at new boundaries (max error ~1.2e-7).
No atlas image changed and no fresh state AO bake was needed. Floor/scaffold mesh
and UVs remain exact; scaffold's pre-existing white Blender material preview is
unchanged. Current canonical texture paths retained. Front/rear pillaged and
construction previews inspected; saved and published validation passes. Backup
under `Storage/Storage_S/archive/pre-mapping-match-2026-10-11/` includes old Blend,
CN6 and frozen texture maps; archive Blend points to its own `Textures/` folder.
Both published and archived Blend image bindings reopened and verified.

Output: `/Users/henno.gous/Play/codex-outputs/storage-s-conpil-match-2026-10-11`.

### Same day — requested Small CON+PIL polish

Removed Floor object from both scenes and export, and purged its orphaned mesh,
material and texture dependency. Split the two short-entrance wall triangles at
z=12.1: rough stone remains below, horizontal boards above, removing the diagonal
stone wedges. Four added coplanar positions; all original building positions and
scaffold data unchanged. UV2/UV3 retained/interpolated (<7e-8 error).
All five exposed full rafters and their supporting exposed crossbeams/returns now
sample the existing `medium_dark_beam` strip [770,866,1022,894], grain along each
member. No atlas pixels changed. No AO rebake in this pass.

Published official Small CON+PIL Blend/CN6: building1259 serialized vertices /674
triangles, scaffolding319/147; no Floor mesh. 430 editable building vertices,363
polygons. Rendered front/rear and construction; validation passes. Reopened clean
and archived Blend, verified all external image bindings. Previous file and frozen
maps archived under `Storage/Storage_S/archive/pre-polish-2026-10-11/`.
Output: `/Users/henno.gous/Play/codex-outputs/storage-s-conpil-polish-2026-10-11`.

### 11 October — Medium CON+PIL AO rebake after duplicate audit

Read-only duplicate audit confirmed both Small and both Medium masters have no
coincident polygons/triangles, coplanar overlap or zero-area faces, scaffolds
included. Current replacement Large has one exact opposing end-cap pair271/282
and a slightly warped partial pair287/300 at internal roof-trim meeting joints;
no doubled shell. Historical old Large not inspected. Audit outputs:
`/Users/henno.gous/Play/codex-outputs/storage-duplicate-audit-2026-10-11`.

Henno noticed M CON+PIL darker. Saved material, AO strength .72, exposure/world/sun
strength match intact Medium; AO-only review showed the inherited older state bake
had broader/darker occlusion. User then authorized rebaking Medium CON+PIL first,
with Large CON+PIL (exposed rafters, possibly missing upper walls) as subsequent work.

Fresh geometry-only AO now published in canonical CSC_Atlas_AO2.png, replacing only
M CON+PIL's existing inner [894,884,1002,1020], outer [892,882,1004,1022]. No added
atlas space; final108x136. Existing UV2 had no overlaps and all geometry, UV1/UV2/UV3,
weights/transforms remain exact. No CN6 update needed. Isolated scaffolding,
disconnected normal and old AO during bake;128samples,distance16.9353. Baked432x544,
4px margin, then BOX downsampled to108x136 and extended2px outer gutter. Supersampling
resolved dark edge smudges seen with native-resolution2px margin. All pixels outside
reserved rectangle exact; B/N/G/M/E unchanged. AO is specific to damaged geometry,
not a copy of intact Medium's shadows.

Saved/reopened official Blend with active AO bake setup; validators pass. Previous
Blend and six frozen maps archived under Storage/Storage_M/archive/pre-AO-rebake-2026-10-11/.
Source/atlas publication hash verified. Outputs and renders:
`/Users/henno.gous/Play/codex-outputs/storage-m-conpil-ao-2026-10-11`.

## 11 Oct 2026 — New Large CON+PIL built and published

Created the replacement from the user's current 9Oct Large source (sha256
bf0dceaa6e897ff04dd14566989eb10bc906f23be151504fc36204ebd99427af), preserving its
world placement, .9 scale, stonework and underground arch extensions. Opened the
loading-wing roof pitch plus a long-side roof bay; authored dark timber rafters,
valley members and opening posts/plates. Removed two upper-wall panels and matching
interior lining. Existing upper floor retained; no ground floor added. Current
Large has no crane: its separate crane file was preserved unchanged.

Official `Storage/Storage_L/CSC_Storage_L_CON+PIL.blend` and matching CN6 replaced.
Static Bone rig, three UV sets, building material CSC_TAILORS_NE. Reused Medium's
scaffold with uniform1.15 placement, native UVs and Pillage_Construction_01 binding;
flat brown Blender preview only. Building2176 exportedvertices/1210triangles;
scaffold269/125. Total2445 exceeds2200 design target (advisory warning reported),
not a hard export failure. Source-specific state integration/FGX/game not tested.

Fresh unique AO in existing storage quadrant: inner[674,842,762,1018],
outer[672,840,764,1020],88x176 final. Cycles128 geometry-only, distance17,4x bake,
BOX downsample,2px outer gutter. Normal and previous AO disconnected; scaffold
excluded. Explicitly checked all current S/SCP/M/MCP/L/LeanTo UV2: slot clear,
including Large's newer interior charts omitted from older registry. All atlas
pixels outside slot exact; B/N/G/M/E unchanged. Full current allocation registry
and reports at `codex-outputs/storage-l-conpil-2026-10-11/release`.

Reopened canonical deliverable and validated paths, geometry, weights and export.
No degenerate triangles or exact duplicate building faces. 457 unaffected source
faces retain positions/material UVs (see validation report for authoritative count).
Intact Large/crane file hashes protected. Old legacy CON+PIL was archived as opaque
bytes, never loaded/viewed; its internal texture paths remain original, with frozen
maps alongside under `Storage_L/archive/pre-CONPIL-replacement-2026-10-11/`.
Outputs/scripts/front,rear,top,construction renders:
`/Users/henno.gous/Play/codex-outputs/storage-l-conpil-2026-10-11`.

## 11 Oct 2026 — Large pillage decals delivered, doubled at user request

Published `Storage/Storage_L/CSC_Storage_L_PIL_Decals.blend` and CN6 for the new
Large CON+PIL. Ten native Ruin_Debris_Decal cards (40vertices/20triangles), three
main fall zones: loading-wing missing roof valley, missing short/front wall panel,
and missing long-side roof/wall bay. Each main zone has two same-size offset cards;
four smaller peripheral scatters. The second set doubles the original five-card
layout and total card area at the user's request. >90% card area is in primary
clusters. All locations preserve current Large world placement.

Native shared512x256 `Pantry Exports/Ruin_Debris_Decal.dds` reused unchanged;
no new runtime texture/material or atlas changes. Runtime planes Z24.11329 through
24.83329 follow inspected Medium PIL projection-plane convention. Export contains
only10cards+staticBone rig. Review contains the current ruin, ground and flattened
decal preview copies; foundations trimmed in preview only, no scaffold. Source
CON+PIL hash unchanged. Blender/CN6/material/path checks pass after reopening the
installed file. FGX/AE/game projection and Pillaged-only attachment integration
not performed. This file replaces the obsolete Large decal geometry; attach once.
Old decal blend/CN6 archived opaque without inspecting the historical Large design
under `Storage_L/archive/pre-PIL-decals-replacement-2026-10-11/`.
Outputs/layout manifest and front/rear/top previews:
`/Users/henno.gous/Play/codex-outputs/storage-l-pil-decals-2026-10-11`.
