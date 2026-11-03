# Modern Quarter roads — 27 October 2026

## Latest: crossing lightness / overlap blend fixed — 29 October

Human still saw crossing shoulders lighter. Root cause found: single ring alpha
~.49 at crossing vs ring+approach composite~.74 just beyond it. ThreeIndustrial
alpha maps now use complementary ring coverage plus12-world-unit smooth fade
in the approach's plain cell. This avoids the abrupt cut that a ring-only mask
correction initially produced. Target max(single layer coverage), RGB untouched.
All crossing width checks still pass; B/H coverage10mips and isolatedcook pass.
Installed threeDDS, cache verified. Geometry/UVs/tarmac/ASTs unchanged. Evidence
crossing-blend-20261029, tool crossing_blend.py. Close beforeafter attached.
Live AE/game visual check remains pending. Existing shoulder width4-ish retained.

## Latest: crossing flare shoulders corrected — 29 October

User noticed too little shoulder at pedestrian crossings. Verified inner crossing
edge u87 had2.45–3.35 visible units vs4.2 along straight road. Local Industrial
roundabout alpha now follows actual Modern paved flare (sampled signed-distance
envelope), feathered within approach u79–108 only. B/FOW/H alpha changed; all RGB,
geometry, UVs, tarmac, ASTs preserved. Five crossings at u87/91.5/96 pass >=3.5
units visible each side. H/B alpha match all10mips; cook and installed/cache pass
(threeDDS). SourcePNGs updated. Evidence crossing-shoulders-20261029 with close
beforeafter and per-crossing measurements. Tool crossing_shoulders.py. No liveAE
or game check/deployment. Do not rerun prior one-time paint generators.

## Latest: shoulders fixed and installed — 29 October

User explicitly said “fix shoulders”. Applied broad Industrial-only underlay,
including30-degree elbow. Current measured medians per side:4.25 at50% alpha,
8.95 at25%,13.55 at10%; native targets3.775/8.6/13.2. Existing stone core +
projected Firaxis Ancient gravel RGB/H, calibrated technical fade; no tarmac
paint edits. All23 saved sources checked;14 affected native geometries and
threeIndustrialDDS installed (31files includingGEO). AE cache and isolatedcook
passed; AST/ArtDefs/XLP/materials preserved. Tarmac geometry/UV checks passed;
Z0stone/Z1tarmac retained. Expanded only Industrial projection bounds; atlas
cells now have industrial_world_size. Shared stone/tarmac mesh data split
before changes. Tight inner bends initially folded when widened; fixed by
local inner-edge contraction propagated across duplicate segment endpoints.
Median width retained, no negative triangles remain; inside bends vary locally.
Current evidence: `shoulders-fixed-20261029/` with beforeafter, corrected classical
overlay, measurements, saved/native/mipmap/cook/installed/cache reports.
Tool `fix_shoulders.py`: prepare,paint,build,fix_turns,review,stage,publish.
No live AE/game screenshot or game deployment. Earlier NOT APPLIED notes below
are superseded. User wants images attached inline, not Shadow-path embeds.

## Latest: shoulder check, classical overlay and elbow — 29 October

User requested checking shoulder width against vanilla, overlaying current roads
on classical and adding an approximately30-degree elbow to atlas. Measured33
paired native cross-sections vs15CSC: per-side gravel extension at alpha50/25/10%
is3.775/8.6/13.2 native vs0.425/0.9/1.25CSC. Target roughly4 visible +softfade13.
**Broad shoulder expansion NOT applied**; this was a measurement/check. Current
overlay explicitly labels this, verifies five classical exit anchors, and shows
15-unit tarmac. Evidence in `vanilla-shoulder-calibration-20261029/`.
Added elbow30 slot[400,184,504,240] to both512px atlas pages;42x26 card/radius60/
30-degree heading change. Deterministic inverse-UV bake of existing painted
straight cell; no new painted material, no edits outside the new slot. H=B alpha
all10mips. Two per-module blends, CN6/GEO/FGX installed and browser-indexed;
existing allgeometry/AST unchanged. Tenfiles total; native/saved/cook passed.
IDs CSC_Road_Elbow30_Industrial and CSC_Road_Elbow30_Modern, stoneZ0/tarmacZ1.
Canonical source remains Decals/CSC_ALL_Modern_Roads; masters.json now16 modules.
Current elbow shoulder remains narrow pending a separately requested expansion.

## Latest: vanilla-width calibration installed — 29 October

User found roads too wide. Measured45 cross-sections/15 native modern Commercial
Hub+Campus road meshes using actual FGX UV/alpha mapping:13.73–15.38, median15.09.
Installed main width15 (was26), connector10.38 (was18). Geometry cross-sections
contract; exits/centerlines/roundabout center, textures and Z0/Z1 preserved.
All21 Blender sources and20 native geometries verified;40GEO/FGX installed and
indexed; isolatedcook PASS. Existing ASTs untouched. Ring uses24x24 quads/625verts
to warp its painted lane and mouths; no inverted triangles. Comparison attached
inline from `vanilla-width-calibration-20261029/Vanilla_CSC_Width_Comparison.png`.
Same canonical Decals folder. Native converter material aliasing fixed by
RepairRoadMaterials.cs restoring prior bindings AND file.AddMaterialReference;
without file-level registration readback passed but cooker crashed. Finalcook
passed after fix. No game deployment/live AE visualcheck. Active source model
records updated; do not rerun one-time narrow_roads build against edited masters.

## Current installed road heights — 29 October

User resumed the Z-order update after “ho” / hold. Completed: stone Z0,
tarmac Z1 in all saved masters and twelve changed FGX exports. Twenty-one
saved-file checks, independent native readbacks, isolated cook and AE cache
checks pass. Source folder is `Working Files/3D Art/Decals/CSC_ALL_Modern_Roads`.
Earlier Z20 documentation was incorrect for the installed exports: inactive
Export scene transforms were not evaluated. Always activate Export and update
its view layer before decoding. Sources now agree with native coordinates.
Original native frames, UVs, XY, mesh/group IDs, GEO metadata, textures and all
AST placements/visibility are preserved. Evidence: road output folder
`tarmac-z-order-20261029/final-verification.json`. No live AE/game visual check
or game deployment. Height-channel repair from the preceding turn is retained.


## Superseding roundabout candidate — 29 October

Henno requested five exits + smaller lower connector, entire initial Industrial
stone layout, first building paving circle/NW/NE/bottom-right Stage2, optional
branches independently afterward. See `project/docs/art/modern-quarter-roundabout.md`.
Working master: Working Files/3D Art/Quarters/modern/roundabout-v1/
CSC_ALL_Modern_Roundabout_Kit.blend; fourteen separate surface/route modules.
Paired 512px Industrial/Modern B/H/FOW/S atlases reuse native surface crops with
new technical shapes and white markings. Outputs under Desktop/Codex/
Quarter-Roads-Modern/draft-03-roundabout; maintained scripts modern_roads/.
IMPORTANT correction: user requires alignment with existing major roads. Read
live classical05, not guessed draft01 nodes. Exact five outer corridors derived
from Fade001/004/003/005/006 respectively; old Fade002 sixth spur omitted.
26-unit paved width compared against actual combined Ancient/Classical alpha.
No runtime install/cook. Authoring source has clean stone-base Export; independent
module masters provide material-specific Export and matching ground Preview.
Do not regenerate these masters after user edits; continue from saved files.

Follow-up overlay review: moved circle +40 X / -20 Y to center(5,10), same radius.
Reshaped saved approach meshes with smooth displacement; outer classical road
corridors stay fixed. Both era surfaces and all independent masters updated.
Pre-edit source snapshot is under draft-03-roundabout/history/before-center-shift.
`recenter.py` is a one-time guarded edit, not a general regeneration step.

Next follow-up: worn Industrial shoulders now act as the Ancient-like underlay
around tarmac. ImageGen paint fitted into existing cells (center native stone
preserved), B/FOW alpha expanded with soft broken-stone/dirt edges; fringe H
derived from paint. Geometry/UV and all Modern maps unchanged. `prepare.py` refuses
to overwrite this painted revision; use saved atlases. `wear.py` is guarded once,
`refresh.py` validates/renders texture updates. Sources/prompt/provenance and
before-paint textures are preserved under the current output folder.

Latest marking correction: user says flatbed scale cannot support a two-way-road
reading. Modern B/FOW now have only five pedestrian crossings across the circle's
exits. Removed all center dashes, give-way marks and inner ring line. Five stripes
per crossing; roads/UV/alpha and worn stone textures unchanged. `crossings.py`
applied the one-time edit, with snapshots in history/before-crossings; prepare.py
also reflects the new design but remains guarded against overwriting painted art.


User requested a first angular modern road layout retaining the classical network,
with full Ancient + Classical coverage in modern01 and progressive tarmac overlays
as buildings fill in; editable blend + overhead render, then user tweaks.
Inspected source Quarters/CSC_ALL_Classical_Base_05_Road_Decals.blend and Ancient/01.
Firaxis Decal_Parts_Industrial_01 is stone paving; Decal_Parts_Modern_01 is tarmac.
Displayed both native sheets and same-geometry comparisons on request. Draft uses
unmarked Modern strips, unchanged B/H textures, plus Ancient/Classical base.

Delivery: Desktop/Codex/Quarter-Roads-Modern/draft-01/
CSC_ALL_Modern_Quarter_Roads_Draft_01.blend. Review scene is 01 complete gravel;
02-05 scenes add tarmac; Classical05 reference scene preserves original XY and UV.
17 editable route meshes, 104 vertices per layer; mesh data shared across three
surface layers and all stages, so Edit Mode vertex edits propagate. Stage allocation
is a proposal. Native export/cooking not performed; no source/runtime assets edited.
External relative DDS snapshots in textures/. START HERE text inside blend.
Overheads: Modern_01_Gravel_Overhead.png, Modern_03_Overhead.png,
Modern_05_Tarmac_Overhead.png and Modern_Quarter_Roads_Overview.png.
Saved authoring validator passes (0 errors); custom saved-file verification checks
linked geometry, material overrides, incremental stages, textures and mesh validity.
Blender preview uses heightmap alpha bump and transparent_max_bounces64 to avoid
black overlap cards. UV2 supplies endpoint fade as preview logic, not an already
implemented Firaxis shader behavior. Draft has not been approved by Henno.
Continue from user's edited saved blend, not regenerated build_draft.py output.

## Industrial middle layer revision

Henno requested Industrial instead of Classical for the middle surface and a view
of version03 transitioning to Modern. Saved draft02 by editing the delivered
saved draft01, preserving every mesh coordinate, UV and object transform.
17 new-layout Classical object materials now use Decal_Parts_Industrial_01 with
its native B/H maps; Ancient underlay and Modern progression remain. Classical
reference scene stays unchanged. Opens on 03 - Tarmac progression.
Delivery: Desktop/Codex/Quarter-Roads-Modern/draft-02-industrial/
CSC_ALL_Modern_Quarter_Roads_Draft_02.blend and
Modern_03_Industrial_to_Tarmac_Overhead.png. All external textures are copied
relative beside the blend. Saved-scene validator passes, original hash unchanged,
geometry/UV/placement parity and texture availability pass. No native integration.
## AE geometry/material handoff — 29 October 2026

LATEST29Oct HEIGHT FIX: native screenshot showed projection rectangle/raised
route edges. Our H channels were wrong: RGB128 constant, alpha150..255 even on
transparent B. Firaxis H is grayscale RGB height + coverage alpha (native crop
Industrial90..95, Modern84..90). Corrected both H PNG/DDS source+installed:
grayscale native-sampled centers, subdued Industrial fringe86..92, alpha EXACT
B across all10mips. No UV/FGX/basepaint/AST changes.21 blends preview Height now
uses Color instead of Alpha, saved validators+exportshape parity pass. Isolated
5variantcook pass; final native visual confirmation pending. Tool repair_height.py
and height-channel-repair-20261029 evidence. prepare/build fixed, historical wear
script disabled against regression. User moved folder again: CURRENT source is
3D Art/Decals/CSC_ALL_Modern_Roads (textures/ and modules/ inside); AE source
references, tool paths and active hash manifests updated. Overrides prior root
Decals location and earlier incorrect height-in-alpha/flat-asphalt statements.

CURRENT SOURCE LOCATION (user-directed relocation): all road masters now live
directly under Desktop/Working Files/3D Art/Decals; textures in Decals/textures,
independent module sources in Decals/modules.74 files moved byte-identically;
21 saved blends validate and all external image paths resolve.28 installed GEO/
TEX source-path references and AE index updated, tool inputs/routes updated.
Old roundabout-v1 folder only has a MOVED.txt pointer and empty directories.
Evidence source-relocation-20261029. This overrides older source paths below.

LATEST handoff supersedes the single all-pieces recommendation below: user asked
to inspect classical and deliver preselected complete layout geometries. Actual
classical01..05 GEOs have38/41/45/48/52mesh subsets, all visible in Worked, rather
than hidden geometry defaults. Installed CSC_ALL_Modern_Base_01..05_Road_Decals
GEO/FGX, matching saved blend/CN6 sources in roundabout-v1. 01allstone7meshes;
02initialRoundabout/NW/NE/SE11;03plusE12;04plusSW+Connector13;05all14. All retain
7stoneunderlay meshes.03/04 independent destinations. Models/UVs/materials exact
approved parity; saved validation/native conversion/cook/cache dependency checks
PASS. Evidence layout-variants-20261029 and variants.py. Existing ASTs/materials/
XLP/ArtDefs untouched; private testASTs not installed. Old combined/module assets
retained; use new numbered geometries for normal district-variant assembly.

CURRENT clarification: user wants one combined geometry like classical layouts,
with individual mesh visibility toggles. Installed/browser-indexed
CSC_ALL_Modern_Base_Road_Decals.geo/fgx with all14 Industrial+Modern meshes and
the two material names. Matching new blend at roundabout-v1 root. Exact approved
module geometry/UV/material parity, saved validation, native readback and private
cook PASS. Evidence combined-layout-20261029; tool combined.py. Recommend this
single geometry at origin/rotation0/scale1; user toggles per-mesh state visibility.
Separate modules remain available but are superseded as the preferred handoff.
No public AST/XLP/ArtDef or material changes in this correction.

User requested export of required geometries/materials for his new district base.
Installed 14 CSC_Road_{Roundabout,NW,NE,E,SE,SW,Connector}_{Industrial,Modern}
FGX/GEO pairs, CSC_Roads_{Industrial,Modern}_01 DecalMaterial MTLs and 8 DDS/TEX
pairs (46 files). AE closed; AssetCloud explicitly registered and all entries/
dependencies independently read back. Fresh native conversion checks pass and
isolated SDK cook passes. Empty OB advisories are for private decal-only cook
assemblies; two solid Spec-map advisories. No public AST, ArtDef, XLP or runtime
changes. No live AE or game appearance claim. Add at origin, rotation0, scale1;
Z20 authored projection already in mesh. Underlay all7 Industrial, first overlay
Roundabout/NW/NE/SE Modern, remaining destinations independent. User owns new
assembly. Source masters/paint unchanged. Tool modern_roads/integrate.py; evidence
Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout/ae-integration-20261029.
Full setup notes: project/docs/art/modern-quarter-roundabout.md.

