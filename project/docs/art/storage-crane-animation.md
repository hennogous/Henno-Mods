# Storage crane animation investigation

Investigated on Shadow, 7 October 2026. The reusable workflow is now in
[`civ6-art/references/art-animation-workflow.md`](https://github.com/hennogous/civ6-art/blob/main/references/art-animation-workflow.md)
(updated locally; not pushed by this task). This report preserves CSC-specific
evidence and the next storage step.

## Result and verification boundary

### Loading platform alignment — 10 October 2026, revision 12

Corrected the added sled platform's plan alignment: it was square to the donor's
local X axis while the runner beams lie at approximately -3.78 degrees. Rotated
the eight platform vertices about their centre and centred them between the inner
runner edges (local Y -5.2 to -5.89104). Height, dimensions and UVs are retained.
The platform originally followed only `Cart`, which yaws differently from the
runner structure during gait. Its eight corners now share an 85% `Sledge_R` /
15% `Cart` blend, keeping the plate planar while following the two runners.
Measured maximum plan-angle error against their average axis is 0.0281 degrees
over 340 sampled walking/idle poses. The initial rigid Cart and rigid Sledge_R
trials had residuals of 1.69 and 0.33 degrees respectively.

All 500 original donor vertices, their weights, all UVs and topology are preserved;
only the eight added platform vertices and their weights changed. Animation keys,
cargo bones, routes, handoff positions and the production AST remain unchanged.
The generator uses `delivery_sled_geometry.align_loading_deck` so future rebuilds
retain the correction. Evidence and backups are in
`Desktop/Codex/CSC_Storage_L/delivery-deck-20261010/`.

Installed only the production `Geometries/CSC_ALL_Delivery.fgx`; GEO, AST, ANM
and the revision-11 clip remain byte-identical. Native round-trip and workshop/
storage clearance checks pass. The saved static validator retains its same five
animated-contract findings. Top and rear renders of the reimported native model
were inspected and copied to Dropzone as `Sled-Deck-Aligned-Top.png` and
`Sled-Deck-Aligned-Rear.png`. Working Delivery Blend is updated. AE/cook/game
review remains manual.

### Optional upright cargo and concealed reset — 10 October 2026, revision 11

The shared delivery rig now has 33 bones, adding `Cargo_TipUpright`. Existing
`Cargo` motion retains the bale's orientation. Choose the attachment bone in AE
on model instance `CSC_ALL_Delivery_Rig`:

| Prop | Attachment bone | Scale | Position / rotation offsets |
|---|---|---|---|
| `CSC_ALL_Textile_Bale` | `Cargo` | 0.8 | Zero |
| `CSC_BAKERS_Flour_Closed` | `Cargo_TipUpright` | 1.0 | Zero |

The optional bone lies the closed sack along the sled, then rotates it a full
90 degrees during seconds 28–31 of the lift. Its translation compensates for the
actual sack bounds so the bottom follows the lift height rather than rotating
through the sled. At 28 / 29.5 / 31 seconds the measured relative angles are
90 / 45 / 0 degrees. The calibrated prop uses the current Bakers_Flour_FINAL
closed-sack geometry under its retained runtime name. Other prop dimensions or
attachment scales can need their own offset tuning; this is not an automatic
fit for arbitrary replacement geometry. The optional preview sack is hidden by
default in the working Blend (`REVIEW_Closed_Sack_TipUpright`).

After landing, cargo holds until 42.6 seconds, slides directly right to the
concealed corner by 45.5 seconds, then drops below grade by 47 seconds. Removed
the previous six-unit intermediate target and subsequent inward/leftward move.
The drop corner is world XY (-31.0275612, 131.5083923), corresponding to local
(-13, -39) in the measured storage frame. Update this target with future building
placement changes. The 68-second cycle, ten-second pause and all existing crane
and donkey path poses remain unchanged (maximum matrix difference zero).

Installed updated delivery model FGX/GEO and clip FGX; existing AST, ANM,
building geometry and materials are preserved. No TEST runtime assets were added.
The Tailors asset continues to use its bale. To try the sack, change the existing
cargo reference and its attachment bone/scale as above; do not attach both options
at once. Reopen the asset in AE, preview Worked, and rebuild/cook for game testing.

Both props clear the shell over 526 lift/slide poses. Descent and underground
return were checked frame-by-frame using native sampled positions, dense surface
samples and 45 long-side viewing directions: azimuth within +/-35 degrees of
the long-side normal and elevations 25/40/55 degrees. No exposed samples were
found. This is a scoped occlusion check, not an all-angle game guarantee.
Native attachment checks cover 260 poses including every frame of tipping and
storage withdrawal; maximum error is below 0.025 model units, within the unchanged
0.08 gate. Crane/donkey native errors match revision 10. Saved-scene validation
has the same five established static-contract findings (derived Mine mesh,
source UV count/skinning, and bone-carried cargo terrain/support rules); the
animated binding, clearance and native checks are the applicable verification.

Evidence/backups: `Desktop/Codex/CSC_Storage_L/delivery-reset-20261010/`.
Dropzone previews: `Tailors-Delivery-v11-Sack-Lift.mp4/.gif` and
`Tailors-Delivery-v11-Hidden-Reset.mp4/.gif`, both normal speed. Working source:
`Working Files/3D Art/Storage/Storage_L/Delivery/CSC_TAILORS_Storage_Delivery.blend`.
Motion helpers are in `project/tools/art/delivery_cargo_motion.py`; the normal
author/export scripts include the new bone. The one-off update script restores
its captured pre-v11 authoring file and must not be rerun after further user edits.

### Coordinated smaller storage refit — 10 October 2026, revision 10

Installed the smaller building and refitted delivery in the production
`CSC_TAILORS_Storage_L` asset. The narrower gabled front stays at its previous
distance from the road: the additional 0.9 resize is anchored at world
(-17.6548443, 126.5827637, 0), superseding the earlier own-origin pivot below.
Both entrance surrounds extend to the foundation bottom. The open upper interior
and existing UV edits remain. Static export is 1,880 vertices / 996 triangles.

The separate crane receives the same scale and translation, and the donkey's
delivery stop follows the new hook position. Donkey and sled remain at original
Mine scale 1.0. The cargo attachment is now 0.8: all 481 lift, swivel and visible
slide poses clear the resized shell, with at least 0.5 model units of bay-side
clearance. The cargo retains its six-unit sideways slide. The 68-second loop and
ten-second pause remain; half-second distance easing at journey starts and ends
avoids a sharp velocity change that failed native attachment round-trip checks.

Published building FGX/GEO, delivery model FGX and animation FGX. The production
AST changes only Cargo's attachment scale; other user settings are preserved.
The rig remains `CSC_ALL_Delivery_Rig`, mesh `CSC_ALL_Delivery_Donkey`, attachment
bone `Cargo`. No retired TEST runtime assets were restored. Building, crane and
the separate `Storage_L/Delivery/CSC_TAILORS_Storage_Delivery.blend` sources are
updated. CON+PIL remains a later task.

Saved-building validation, workshop/storage clearance, road alignment and cargo
slide checks pass. Native round-trip maximum crane error is 0.01371 model units;
donkey error is 0.48724 (0.31671 at the established comparison scale), and maximum
attachment matrix error is 0.01287, within the unchanged acceptance gates.
AE/cook/game testing remains manual: reopen `CSC_TAILORS_Storage_L` and preview
its Worked state. Preview video/GIF names are `Tailors-Delivery-v10-2x` and
`Tailors-Delivery-v10-Loading-Bay` in Working Files/Dropzone.

Evidence and backups: `Desktop/Codex/CSC_Storage_L/delivery-refit-20261009/`,
including `production-refit-check.json` and
`production-backup-20261010-080107/`. The current runtime AO2 DDS already postdates
the interior atlas bake, so this refit did not replace it.

### Building foundation and scale — 9 October 2026

The current `CSC_Storage_L.blend` has both beveled entrance surrounds continued
down to the foundation bottom (16 new quads). The complete static mesh is now
90% of its previous size around its own ground-level position
(-34.9057007, 168.9768982, 0), preserving its district placement. This is an
additional reduction of the current geometry. Existing UV mapping is preserved;
underground extensions reuse the matching pillar surface charts.

Source count is now 1,874 vertices / 474 faces; prepared CN6 count is 1,880.
Foundation depth is 17.496 model units and the upper floor is at 37.70987
(previously 41.89985). Per Henno's instruction, the separate crane, donkey, cargo
and delivery animation were not changed, so their existing handoff height remains.
CON+PIL was not edited. Saved-source checks and normal CN6 export passed; reviewed
both entrance closeups. Only the source Blend was published; normal AE export is
still pending. Evidence, previews and the original source backup are in
`Desktop/Codex/CSC_Storage_L/foundation-scale-20261009/`.

### Sled runner repair — 9 October 2026, revision 9

The cargo-removal selection incorrectly deleted 12 vertices / 12 triangles from
the right runner. The Mine's Cart bone weights include these runner vertices as
well as its crate and ore; a bone-weight selection is not a cargo-part selection.
The authoring tool now removes only complete Cart-only components, connecting
coincident UV/normal seams for selection without welding the actual geometry.
Both runner components remain intact, including their original Cart weights.

Restored the original faces, UVs and weights in the delivery source and working
Blend. Every previously retained face, UV and weight was checked for preservation.
The repaired donkey/sled is 508 source vertices and 426 exported triangles;
the native descriptor now reports 508 vertices (previously 490) and 426 triangles
(previously 414). Export vertex splitting differs from source vertex counting.

Installed the checked geometry in CSC_ALL_Delivery and the existing trial geometry.
The 68-second native animation remains byte-identical to revision 8, and the user's
current production AST and cargo attachment settings were preserved. Native
round-trip animation checks passed; both rear views were inspected with backface
culling on the reimported FGX. AE itself awaits the user's manual reload/review.
The Dropzone preview is `Tailors-Delivery-v9-Runner-Repaired.png`. Evidence and
backups are in `delivery-01/runner-*-check.json`, `before-runner-repair-09` and
`runner-install-backup-20261009-112711`.

After Henno removed the old TEST assets/animations/material, 12 stale Content
entries remained in the ModBuddy project and pointed at missing files. Removed
those entries; all remaining explicit project file references resolve. No current
AST, XLP or ArtDef depends on a CSC_TEST file. Production uses
`Geometries/CSC_ALL_Delivery.geo/.fgx` and `Animations/CSC_ALL_Delivery.anm/.fgx`.
The internal rig name is a model/root-bone identity, not a file dependency.
It was subsequently renamed to `CSC_ALL_Delivery_Rig` at Henno's request (below).
Do not reinstall old trial packages merely to repair production. A full ModBuddy
rebuild was not run during this reference cleanup.

### Production rig rename — 9 October 2026

Renamed `CSC_TEST_TAILORS_Delivery_Rig` to `CSC_ALL_Delivery_Rig` in the native
model, skeleton, root bone, animation track group and root animation track; updated
the GEO model/bone names and AST model-instance/cargo binding together. The Cargo
bone itself is unchanged. Firaxis serialization preserved the existing geometry
and animation curves: complete extracted CN6 and all 2,041 sampled frames across
32 bones compare identically after substituting only the requested name.

The saved native-export Blend and exporter defaults use the new name. Authored
working Blend files had no occurrence of the old name and needed no mutation.
Three-pose checks across all saved scenes showed zero matrix difference. Generated
export FGX/GEO/CN6/NA2 inputs were synchronized; retired project TEST files were
not reinstalled. Backups and reports: `delivery-01/production-rig-rename/`.
No AE UI/cook check was performed for this identity-only change.

### Open upper interior — 8 October 2026

The current `Working Files/3D Art/Storage/Storage_L/CSC_Storage_L.blend` now has a
continuous T-shaped upper floor, inward-facing wall linings following the exterior,
and shallow opening reveals. This replaces three boxed recesses. The original
`.pre-ao` source and old CON+PIL were inspected as references for the open layout.
The floor remains at the wide crane loading bay's original height. Exterior
geometry, current applied placement and all retained UV corners are preserved.
The intact roof stays in the source; roof-cutaway renders are inspection views.
CON+PIL roof removal remains a later task.

The source has 1,810 vertices / 458 faces; prepared CN6 count is 1,816. Saved-file
validation passes the automated static-building rules; all vertices are weighted
to Root and all three UV layers and texture paths are valid. A normal CN6 export
was checked. No production FGX or AST was replaced in this source-edit task.

New interior AO was baked to independent shared-atlas charts, after checking the
storage-family sources for occupancy. Only 2,174 pixels inside the 2,352 reserved
pixels changed in canonical `3D Art/Textures/CSC_Atlas_AO2.png`; all unrelated pixels
remain identical. Refresh the runtime AO2 texture from this PNG with the next
normal building export. Mapped AO, inward normals, intact openings and two cutaway
views were inspected. Output reports and the original blend/PNG backups are in
`Desktop/Codex/CSC_Storage_L/interior-20261008/` (`before-interior` for backups).
Review images are `Working Files/Dropzone/Storage-L-Open-Interior-*.png`.

### Production asset naming — 8 October 2026

Henno assembled `Assets/CSC_TAILORS_Storage_L.ast` with `CSC_ALL_Delivery.geo`
and `Animations/CSC_ALL_Delivery.anm`. The donkey mesh has been renamed from
`CSC_TEST_TAILORS_Donkey_Mesh` to `CSC_ALL_Delivery_Donkey` in the native FGX,
GEO descriptor and all five mesh-state references in that asset. The exporter
now emits the new mesh name for subsequent rebuilds. Earlier trial packages
keep their own existing geometry/reference pairs until rebuilt.

Cargo already resolves correctly: geometry `CSC_ALL_Delivery`, model instance
`CSC_TEST_TAILORS_Delivery_Rig`, bone `Cargo`, scale .675, zero position/rotation.
Attachments target a model instance and bone, not a mesh name. Preserve `Cargo`
because it carries both sled travel and the crane handoff; binding permanently
to a donkey body/cart bone would lose that handoff.

The native rename was verified by complete CN6 comparison (only the mesh name
differs) and identical 30 FPS sampled animation data before/after. Skeleton,
weights, UVs, geometry and animation are unchanged. Backups and the validation
report are under `delivery-01/production-mesh-rename`. The user's other asset
settings were preserved. No AE UI operations were performed.

### Current delivery trial — 9 October 2026

**Revision 8 tightens both workshop turns at full donor scale.** The straight
doorway approach ends at depth -44 instead of -55 model units; the broad sweep
uses (-65,-217), (-71,-204), (-66,-187), (-60,-177). This keeps the sled clear
while joining the road sooner. Outbound/return lengths reduce from 595.36/497.40
to 568.30/470.35. Main road, storage approach, cargo slide and 68-second cycle
remain unchanged. Final baked doorway and storage surface checks and road-alpha
checks passed. The threshold pending removal remains excluded from doorway checks.

Installed in trial assets and production CSC_ALL_Delivery; production AST unchanged
and model FGX byte-identical. Native maxima: crane .01535, donkey .18593, attachment
matrix .07256. Saved scene retains only the known animated/static-contract findings.
Working Delivery blend saved. Backup is `before-turn-revision-08`, with production
backup `production-update-backup-20261009-104952`. Previews in Dropzone:
`Tailors-Delivery-v8-2x.mp4` / `.gif` and close-ups
`Tailors-Delivery-v8-Workshop-2x.mp4` / `.gif`. AE playback remains manual.
The delivery review uses its existing context copy; the separate source interior
rework above is not a production geometry update and was not regenerated here.

#### Revision 7: cargo slide

**Revision 7 adds a sideways cargo slide after landing.** At 42 seconds the
load settles; after a .6-second hold it slides 6 model units to the right when
looking into the bay, over 1.4 seconds. It then withdraws inward until 45.5 seconds,
resets below grade by 47 seconds, and returns hidden to the workshop. The 68-second
cycle, 10-second pause and full-size carrier are retained. The visible slide has
constant height/orientation and no sampled intersections with the storage shell.

Revision 7 is installed in the trial and production delivery. Native validation
checks 26 poses including the slide: max crane vertex error .01535, donkey .5222
(same normalized tolerance as revision 6), attachment matrix .07570. Saved scene
validation retains the five documented static-contract findings only. The model
FGX is byte-identical to revision 6; animation changed. Production AST and GEO/ANM
descriptor bytes are preserved. Prior motion is backed up in
`before-cargo-slide-revision-07`; installation backup is
`production-update-backup-20261008-200226`. AE review remains manual.

Dropzone contains `Tailors-Delivery-v7-2x.mp4` / `.gif` for the full route and
`Tailors-Delivery-v7-Cargo-Slide.mp4` / `.gif` for a normal-speed close-up.
Generic findings were promoted to the installed civ6-art skill's
`references/art-animation-coordinated-scenes.md`, linked from its animation
workflow. Project route coordinates, filenames and tolerance values stay here.

#### Revision 6: original-size carrier

**Revision 6 restores both donkey and sled to original Mine scale 1.0**, at
Henno's request. Cargo remains independently scaled to .675. The workshop
approach now stays straight farther from the doorway before taking a wider turn;
the neck dips beneath the arch. The return continues deeper inside before hiding
the longer sled. Henno will remove the workshop threshold, so there is no added
vertical lift over it and clearance checks exclude that low threshold surface.
The retained doorway frame and arch, and the compact storage approach, pass
sampled mesh-intersection checks. Both journeys retain the measured main road;
the wider workshop sweep intentionally leaves its short front-road curve.

The working source remains `Working Files/3D Art/Storage/Storage_L/Delivery/`
`CSC_TAILORS_Storage_Delivery.blend`. Revision 5 is backed up in
`delivery-01/before-scale-revision-06`. Preview filenames are
`Working Files/Dropzone/Tailors-Delivery-v6-2x.mp4` and `.gif` (twice real speed).
The cycle remains 68 seconds with a 10-second pause; the shared Cargo handoff and
random starting phase remain unchanged. Production updates replace only the
`CSC_ALL_Delivery` geometry/animation binaries, preserving Henno's production AST.

Native validation now includes 22 poses, with extra doorway samples. Body error
is measured proportionally to donor scale: the earlier .4-model-unit gate at
scale .65 becomes .6154 at scale 1.0. The full-size native round trip has a maximum
rear-hoof difference of .5222 units (equivalent to .3394 at the previous size).
This is a documented tolerance adjustment, not a conversion fix; twice-dense
sampling did not improve it. Crane and attachment tolerances remain unchanged.
Export keys use linear interpolation and continuous quaternion signs to avoid
unwanted spins between baked frames. The saved static-building validator retains
only the five known animated-contract findings documented below. AE review is
manual; this revision has not been played in AE by the assistant.

Revision 6 is installed in both trial assets and production `CSC_ALL_Delivery`.
Production AST and GEO/ANM descriptor bytes were preserved. Maximum crane error
is .0111 model units and attachment matrix error .07573. The production backup
is `delivery-01/production-update-backup-20261008-194028`. Reopen
`CSC_TAILORS_Storage_L` in AE and select **Worked**; restart AE if it caches the
previous binary files.

#### Revision 5: compact storage approach

**Revision 5 makes the storage approach more compact.** Henno approved revision
4 and requested that the donkey leave the upper-left road sooner, preserving
space for other props. Only the outbound loading loop changed: its westernmost
centreline point moves from X -156.59 to -127.94 model units, and outbound travel
reduces from 562.99 to 508.44 units. The measured shared road, workshop turn,
return route, final pickup position and heading remain the same. The cycle still
takes 68 seconds, including the 10-second pause.

The loaded body/sled and bale were checked against the storage building surfaces
throughout the revised approach, with no sampled intersections. Doorway and road
coverage checks passed. `storage-clearance-check.json` records that added check.
Revision 4 is preserved under `before-road-revision-05`; the revised package is
`package-revision-05`, and previews use `Tailors-Delivery-v5-2x.mp4` / `.gif` in
Working Files Dropzone. AE asset names and the working Delivery blend path remain
the same. AE review of revision 5 remains manual.

Revision 5 is installed. Native 17-pose checks passed (maximum crane vertex error
.0111 model units, donkey .2897, attachment matrix .0641; bind .000115). The saved
static-building report retains the same five animated-contract findings discussed
under revision 4; no new findings were introduced. Original storage/crane files
and production ArtDefs remain unchanged.

#### Revision 4: measured road and front connection

**Revision 4 corrects the upper road bend after Henno's AE screenshot.** Revision
3's hand-traced route cut inside that bend. The replacement uses alpha-weighted
centres from the actual road decal texture and its mapped triangles, with the
Blender reference checked against the installed road FGX in XY. Both journeys
share this measured line; the outbound cross-road approach below storage also
follows its painted centre. Workshop clearance and pickup alignment are preserved.

Henno also pointed out the workshop turn still missed its short front-road curve.
The final revision 4 replaces the wide westward sweep with that curve's measured
line, joining the main road near (-57, -170). The loaded sled still clears the
opening: maximum doorway lateral extent 5.822 units within the 9-unit half-width,
and the sled is 11.74 units inside before hiding on return.

The reference extraction and coverage check are in `inspect_delivery_roads.py`
and `check_delivery_road_alignment.py` under `project/tools/art/`. Their generated
reports and path overlay remain in the delivery review folder. Road coverage is
checked on the shared travel section; the workshop entrance and crane loading
approach intentionally leave the road and have separate clearance/handoff checks.
Revision 3 is backed up in `before-road-revision-04`. Revision 4 retains the same
Blender/AE asset names and uses `package-revision-04` and Dropzone
`Tailors-Delivery-v4-2x.mp4` / `.gif`.

Final revision 4 checks: all 775 sampled centreline points in each direction on
the defined shared/front-road sections have decal opacity above .65 (the road
coverage threshold is .5). Reference XY agrees with installed road FGX within
.000064 model units. Native checks at 17 poses passed: maximum crane vertex error
.0111, donkey .2829, attachment matrix .0723; Blender bind error .000115. Revision
4 is installed with backups and dependency registration. AE playback of this
revision remains a manual check; no computer use was performed.

The saved-file static building validator was also run and its report retained.
It flags the already-approved animated design: derived pantry donkey bundled in
the shared rig, source donkey UV/skin weights, and a bone-carried cargo attachment
instead of a terrain-supported prop. These are outside that static building
export contract. The dedicated animated exporter supplies three UV channels,
preserves skinning and checks the combined native result; cargo is checked on its
animated bone. Do not change these to static weights or terrain pivots merely to
silence the building validator. The source is for the dedicated delivery exporter.

#### Revision 3: first road refinement (superseded)

**Revision 3 tightens the workshop turns and follows the road more closely.**
Henno confirmed revision 2 looks good in AE. Both journeys now trace the painted
road centreline, including its bend and junction near storage. The path sampler
compensates for the native donkey body's lateral offset from its rig origin, so
opposite headings follow the same visible line. The workshop approach turns onto
the front road sooner while preserving a straight crossing through the doorway.
The crane handoff, direct return, replaceable Cargo, random starting phase, and
68-second cycle with its 10-second pause remain unchanged.

Revision 3 checks passed: doorway crossings remain within 5.827 units of centre
in the 18-unit opening; the entire sled is 11.51 units inside before hiding.
Native round-trip checks across 17 poses measured maximum errors of .0111 crane
model units, .1408 donkey model units, and .0725 for attachment matrices. The
Blender export-copy bind error was .000115. The revised route has been rendered
for review; its AE playback still needs the user's manual check.

Revision 3 uses the same asset names and working Blender path. Reopen
`CSC_TEST_TAILORS_Storage_Delivery_Preview` and select **Worked**; restart AE if it
retains the previous clip. The new MP4 and GIF are
`Working Files\Dropzone\Tailors-Delivery-v3-2x.*`, both at twice playback speed.
The previous approved revision is preserved in `before-road-revision-03`, with
the new native package in `package-revision-03`. Original building/crane sources
and production ArtDefs remain unchanged. No UI automation was used.

#### Revision 2: combined rig and corrected doorway

**Revision 2 supersedes the two-clip arrangement below.** Following Henno's AE
report that the bale moved without a donkey, the native export now includes the
donkey mesh and all its bones directly in the delivery rig. One shared clip drives
the crane, donkey, and Cargo attachment; there is no animated donkey child whose
visibility/state or timing must be inherited. AE's log explicitly reported that
the dependent `CSC_TEST_TAILORS_Delivery_Donkey` asset could not be resolved in
`csc_tilebases.xlp` for both delivery parents. Direct geometry removes that failed
dependency. AE remains a manual verification step at the user's request.
The installer had matched a space-indented XLP closing tag, while this file used
a tab; registration was silently skipped. Revision 2 fixes that insertion and
asserts that both asset EntryIDs exist in the saved XLP.

The doorway path now uses measured jambs: centre (-22.361, -189.7365) model units,
18-unit width, with the donor's lateral mesh offset accounted for in each direction.
The start is deeper inside; both doorway crossings remain within 6.256 units of
the centreline and below 19.22 units high. At the last full-size return sample, the
entire sled is at least 9.69 units behind the entrance plane. It continues inward,
becomes hidden, and only then resets orientation. The pickup departure is now a
direct forward route to the road; the previous U-turn and backtracking are removed.

`CSC_TEST_TAILORS_Storage_Delivery` uses native **Standard_Landmark**, whose Worked
destination has `RandomOffset=true`. This randomizes the starting phase of the
whole 68-second sequence per instance. It does **not** change playback speed or
choose a fresh random pause on every loop. The regular 10-second break remains.
The `_Preview` asset deliberately retains **Standard_LandmarkNoRandomOffset** for
repeatable review. Cargo stays a replaceable attachment, with zero offset/rotation
and scale .675; the donkey's .65 scale is baked into its geometry and bones.

Revision 2 previews: `Working Files\Dropzone\Tailors-Delivery-v2-2x.mp4` and `.gif`.
The source remains in `Storage_L\Delivery\CSC_TAILORS_Storage_Delivery.blend`.
`door-clearance-check.json` and `combined-bind-check.json` in the review folder
record the measured doorway and pre-export bind checks. First-revision files are
preserved in `before-route-revision-02`; the new staged package is
`package-revision-02`. Original storage and crane sources are unchanged.

Revision 2 was installed with AssetCloud dependency updates and backups. Native
round-trip checks across 17 poses passed: crane maximum .0111 model units, donkey
.1253, and attachment matrix .0735. The combined Blender export-copy bind error
was .000134. Both the normal asset and Preview have the donkey as direct geometry
with its native `IMP_Mine_Base` material; the crane retains `CSC_TAILORS_NE`.
No UI automation was used during this revision. Restart/reopen AE and select
Worked in the Preview asset for the user's visibility and motion check.

#### Revision 1 context (historical two-clip arrangement)

Use `CSC_TEST_TAILORS_Storage_Delivery_Preview` for the new 68-second delivery
sequence, including the final **10-second break**. The older 12-second trial
below is historical. The user confirmed that its bale now displays in AE.

The delivery starts at the Tailors' Textile Workshop, follows the reviewed road
layout, waits under the crane, transfers the bale, and returns the empty sled.
The native mine donkey keeps its original rig and gait; the fixed ore crate is
replaced by a wooden deck in this scene-specific derived model.

- `CSC_TEST_TAILORS_Storage_Delivery`: crane, route and cargo, with a donkey child.
- `CSC_TEST_TAILORS_Delivery_Donkey`: the matching 68-second local gait clip.
- `CSC_TEST_TAILORS_Storage_Delivery_Preview`: the same assembly with the current
  exported storage model and workshop for context. Roads are in the Blender review.

Manual AE check: save any open edits, restart AE if the new entries are absent,
open the Preview asset through **Open Entity**, then select its **Worked** state
in Asset Previewer Controls. Observe at least two complete 68-second cycles.
Check emergence, sled/hook alignment, cargo transfer, return, and the final pause.
The delivery asset's **Delivery_Cargo** attachment references
`CSC_ALL_Textile_Bale`, on bone `Cargo` of `CSC_TEST_TAILORS_Delivery_Rig`,
with zero offset/rotation and uniform scale **0.675**. Replace that Asset reference
to try another load. `DonkeyPath` carries the donkey at scale **0.65**.
Both clips use `Standard_LandmarkNoRandomOffset`; attachment randomization is off.

Editable source:
`C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\Delivery\CSC_TAILORS_Storage_Delivery.blend`.
Review contains context; Export contains the animated assembly. This source needs
the dedicated export-copy bake; do not directly export its parented rigs through
the identity-rig animation operator. The supplied native package is already baked.
The original building and separate crane files were not changed. Crane placement
uses the user's latest saved matrix: scale .9, X **-.316029 m**, Y 1.658027 m,
Z rotation 20.4866 degrees; its older positive-X custom-property text is stale.

The crane now uses **CSC_TAILORS_NE directly**, retaining all three UV channels
and skinning through the isolated upgraded CN6 converter. The converter's source
is in `project/tools/cn6libs/CN6ToFGX.cs`; the tested executable is under the review
folder's `bridge/`. The normal installed FGX exporter has not been replaced.
Stock CivNexus6 formats 1/2 still discard weights without this custom template path.

Conversion checks: both native clips measure 68 seconds; saved model vertices,
normals, UVs, indices and quantized weights match CN6. Across 17 sampled poses,
native reimport errors were at most .0111 crane model units and .3903 donkey
model units (.2537 after its attachment scale). Attachment matrix maximum error
was .0716. Hidden cargo reset is continuous beneath grade; the donkey turns back
to its initial orientation inside the workshop before the pause.

Evidence and package: `C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01`.
`authoring-check.json`, `native-check.json`, and `asset-package-check.json` record
the boundaries. **AE playback, child synchronization, cooking and game behavior
remain unverified**: the user requested manual AE steps and stopped computer use.
Only separate test assets/XLP entries were installed; production ArtDefs are unchanged.
MP4 and GIF previews are in `Working Files\Dropzone\Tailors-Delivery-2x.*`;
these play at twice speed, so the real 10-second pause appears as five seconds.

Reproduction tools: `build_storage_delivery.py`, `export_storage_delivery.py`,
`install_storage_delivery.py`, `preview_storage_delivery.py`, and
`save_storage_delivery_working.py` under `project/tools/art/`.

### Earlier crane-only trial

**AE test assets installed, 8 October 2026:** launch Asset Editor from the CSC
project and search Assets for `CSC_TEST_Storage_L_Animated` (full current storage
building) or `CSC_TEST_Storage_Crane` (crane and bale only). Open the asset in
Asset Previewer and select **Worked**. If AE was already open during installation,
restart it so the AssetCloud registration is reloaded. The clip is also named
`CSC_TEST_Storage_Crane_Lift` in the Animations/behavior setup.

Both use `Standard_LandmarkNoRandomOffset`, WORKED_A and its timeline, so playback
starts at ground pickup rather than a random point. Repeating still resets to
the ground after the 12-second end hold; this remains the first one-way delivery.
They are test entries in CSC's TileBase XLP, with no production ArtDef replacement.
Construction/pillage behavior and a seamless work cycle are not production-ready.

The Load attachment bone's export-copy basis is corrected to native identity,
allowing the existing `CSC_ALL_Textile_Bale` asset at zero offset/orientation,
uniform scale 0.75. That bone's sampled native transform differs from the intended
matrix by at most 0.03772 model units/components. The 9-mesh crane (including its
mount) reimport error is at most 0.04213 units. The 25-mesh static building shell
retains all three UV channels; independent FGX decode position error is below
0.000047 units. Blender 5's Action slot is explicitly assigned after renaming
the export rig, with ground/lift heights asserted to reject a static export.

The test crane material reuses CSC's Tailors base/normal/gloss/metalness/opacity
maps, with a new neutral white AO map because this animated conversion retains
only UV1. The shell and library bale retain their existing materials. No shared
atlas or original source blend is edited. AssetCloud, project Content entries
and the existing TileBase XLP are registered; modified registration files are
backed up under `Desktop/Codex/CSC_Storage_L/ae-test-20261008/backup-*`.

Reproducible tools: `project/tools/art/build_storage_crane_ae.py` (Blender) and
`install_storage_crane_ae.py` (Python, stage by default, `--install` to deploy).
Both require explicit `--output`; the package and dependency/conversion reports
are in `Desktop/Codex/CSC_Storage_L/ae-test-20261008/`. File/dependency and native
conversion checks pass. **AE visual playback itself has not been verified.**

**Blender 5 add-on installed:** the follow-up delivered Civ VI Animation Tools
1.0.1 to Shadow's Blender 5.1 profile and enabled it in saved preferences.
Use **File > Import/Export > Civ VI Animation**, or **3D View > Sidebar > Civ VI**.
Restart an already open Blender session to load the installed module.

It imports NA2 and native FGX/ANM (with a matching model), preserves root motion
and scale, and exports FGX/ANM directly through CivNexus6. Optional Include skinned
model emits matching one-UV weighted CN6/FGX/GEO. Twenty-five Blender 5.1.2
integration checks passed, including the mine's formerly skipped one-bone travel
and native rotation/scale on converted geometry. The earlier stock-importer
limitations below describe the investigation; the new add-on fixes them.

Source lives in the local civ6-art skill's `scripts/civ6_animation/`, with
`scripts/install_civ6_animation.py` and `scripts/test_civ6_animation_blender.py`.
Installed module:
`%APPDATA%\Blender Foundation\Blender\5.1\scripts\addons\civ6_animation\`.
Package, preferences backup, installation log and test evidence:
`C:\Users\Shadow\Desktop\Codex\Civ6-animation-addon-20261007\`.
The add-on's CivNexus6 preference points to the existing 1.3.3 installation.

Blender-authored skeletal animation can be converted through CivNexus6's Firaxis
FBX importer, separated into an animation FGX and Landmark ANM, and matched to
skinned geometry exported through CN6. A small authored hoist passed conversion
and geometric round-trip checks. Native quarry-crane and mine-donkey gait clips
were imported into Blender 3.1.2 and inspected in rendered poses.

**AE playback, cooking and in-game verification have not been performed.** The
storage building and live mod assets were not changed. This is an investigation
and skill update, not delivery of the production animated crane.

## Shadow tool inventory

| Tool | Confirmed location/status |
|---|---|
| Blender 3.1.2 | `C:\Program Files\Blender Foundation\Blender 3.1\blender.exe` |
| NA2 importer | `%APPDATA%\Blender Foundation\Blender\3.1\scripts\addons\io_import_na2.py`; installed and enabled |
| CN6 I/O | `io_import_cn6.py` / `io_export_cn6.py` in that same add-ons folder; enabled |
| Other NA2 copies | Found in Blender 2.79 and 4.4 user add-ons; not tested here |
| CivNexus6 1.3.3 | `C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6\` |
| CSC converter | `project/tools/cn6libs/CN6ToFGX.exe`; format 0 preserved this probe's weights |
| SDK native sources | `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry\` |
| Firaxis documentation | SDK `Documentation/Civ6Docs.html`, Animation/BuildingsProcess sections |

No add-on download or installation was needed. The distribution online is
[Deliverator/Sukritact's Blender scripts](https://forums.civfanatics.com/resources/blender-scripts-for-civilization-v-and-civilization-vi.25925/).
NA2 is the inward route; Blender's FBX exporter supplies the outward clip route.

## Native references

The actual mine donkey is `IMP_Mine_Sledge`, not the separate `Donkey.ast` asset.

| Native part | Observed wiring |
|---|---|
| `IMP_Mine_AN_01.ast` | WORKED_A → `Test_Mine_Spline_Track_Anim`; attaches `IMP_Mine_Sledge` to `IMP_Mine_AN_Sledge_Track` |
| `IMP_Mine_AN_Sledge_Track.geo` | One animated bone, no meshes; 45-second route |
| `IMP_Mine_Sledge.ast` | WORKED_A → `Test_Mine_Sledge_Anim`; 24-bone donkey/sledge, one-second gait, dust FX timeline |
| `IMP_QuarryREDO_ANC.ast` | References the large quarry crane `PROP_Crane_LG_Stone` |
| `PROP_Crane_LG_Stone.ast` | WORKED_A → `PROP_Crane_LG_AN_Quarry`; intact and separate pillaged geometry |
| `PROP_Crane_LG.geo` | Six bones, 1,513 vertices: 1,489 crane + 24 load; load parented below rope bone |
| `PROP_Crane_LG_AN_Quarry.anm` | Landmark class, duration 26.633335 seconds |

Both use `Standard_Landmark`; its source graph loops WORKED_A with random offset.
The large crane's Base, Crank, Rope and load move; root and GEO bone remain fixed.
Its Stone asset hides intact geometry when Unworked, Pillaged, Construction and
Unbuilt. Its PIL model appears when Pillaged. Choose CSC state behavior deliberately.
The similarly named `PROP_Crane_LG_Anim.ast` is a construction-state example.

## Conversion experiment

The authored test has an armature `AnimProbeRig`, Root and Load bones, and a cube
weighted entirely to Load. At 30 FPS, frames 1–61 raise its center from Z=1 to Z=5,
pause, lower it and pause at the seam.

1. Blender CN6 export → CSC CN6ToFGX **format 0** → `HoistProbe.fgx`.
   Converted skeleton: AnimProbeRig → Root → Load; one weighted mesh.
2. Binary FBX export: Y forward, Z up, no leaf bones, active Action only,
   no NLA/all-actions export, bake step 1, simplification 0.
3. Firaxis import with Node `AnimProbeRig` → mixed skeleton/animation FGX.
4. CivNexus6 SaveAnimationsAction → animation-only `HoistProbe_Loop.fgx`.
5. Metadata writer with class Landmark → `HoistProbe_Loop.anm`.
6. Sample that clip against **HoistProbe's converted geometry skeleton**, export
   CN6/NA2, reimport, and inspect evaluated cube bounds at five poses.

| Frame | Authored Z | Round-trip bound center Z |
|---|---:|---:|
| 1 | 1 | 1.003395 |
| 16 | 5 | 4.969477 |
| 31 | 5 | 5.000148 |
| 46 | 1 | 1.019092 |
| 60 | 1 | 1.003395 |

Every cube dimension remained 1 within 0.000001; lateral drift was below 0.000002.
The check permits 0.05 units of height error (1% of maximum height), because
conversion/sampling approximates the authored curve. Actual maximum error was
0.030524. This is not an exact curve-preservation claim. The imported clip duration
was 1.966667 seconds, so source and converted frame timing must be checked.

**Measured unit correction:** `global_scale=0.01`, `apply_unit_scale=False` matched
CN6. Scale 1 produced roughly 100–500-unit motion on a 1–5-unit geometry rig;
disabling apply-unit-scale alone did not fix it. Calibrate this per toolchain.

**Metadata correction:** the tested CivNexus6 writer emitted the invalid undeclared
prefix `AssetObjects:AnimationInstance`. Normalize it to native
`AssetObjects..AnimationInstance`; the final test ANM parses as XML.

**Extraction issue:** native quarry NA2 export crashed after partial output.
Caching bone names before sampling through `IGrannyAnimation.SampleBone` allowed
a complete 800-frame file. That file was validated and imported. The stock NA2
importer also skips bone index 0, so it loses the mine's one-bone travel clip;
it successfully imports the child gait. It does not key scale.

## Applying this to the large storage building

Read-only inspection of the current sources found:

- `Working Files/3D Art/Storage/Storage_L/CSC_Storage_L.blend` has Export/Review
  scenes, 33 mesh datablock objects and **no armature**. It already contains
  `CSC_Fixed_Crane_Boom`, Brace, Hook, Mount_Hardware, Pulley, Rope, Rope_Collar
  and Swivel_Shaft. This is the newer source for crane geometry; preserve Henno's
  current edits and placements.
- The September Bakers `revision-01-additions-props/CSC_BAKERS_Storage_L.blend`
  has an older one-bone static rig, a Hoist_Hood and Loading_Landing, and no Action.
  It is historical context; do not replace the newer building with it.

Recommended next implementation: preserve the static building and separate the
current crane parts into a rigged machinery asset. Use root/base, swivel, hoist/load
and optional pulley bones; rigid weights are adequate for hard components. A
single coherent lift/swing/lower/return loop keeps rope and load synchronized.
Quarter-specific stock can be attached to a moving load bone where appropriate.
Author the cycle against the current upper bay and check hood/wall clearance,
rope continuity, pivot locations and the whole animated envelope.

The normal `project/tools/blender/export_assets.py` path cannot currently export
this rig: `scene_export/decode_blend.py` explicitly rejects animated armatures
and non-rest poses. Standard CivNexus6 three-UV output also omits bone bindings.
Do not remove that check and silently route the crane through static export.
Use a separate animated package or extend the exporter with a real animation
contract, skinned model conversion and clip/behavior dependency handling.
Keep the building's existing static material/UV contract. The moving crane needs
a material compatible with the one-UV skinning format, or separately developed
support for skinned multi-UV output.

Before production acceptance: stage a complete small AST/GEO/ANM package, verify
WORKED_A and relevant states in AE, attach it to storage, cook it and check it in
game at gameplay distance. AE/game timing and state inheritance remain open.
Construction visibility follows the current CSC conventions; native crane assets
are references, not authority to show intact machinery during Construction.

## Evidence package

### Crane-only working source, later 8 October 2026

Henno subsequently removed the crane and repositioned the building himself.
His current `Working Files/3D Art/Storage/Storage_L/CSC_Storage_L.blend` supersedes
the combined source described below. Keep that current building file intact.

The new sibling **`CSC_Storage_L_Crane.blend`** contains only crane machinery,
the existing animation rig/action and the attached textile bale. Its
`Crane_Placement` empty controls the full assembly: uniform scale **0.9**,
X **0.3160286 m**, Y **1.658027 m**, Z **0 m**, rotation Z **20.4866°**.
These are Henno's explicitly reconfirmed values. Scene units are 0.01 m per model
unit; internal translations therefore read 31.60286 and 165.8027.

Crane geometry retains all three UV maps, including the latest eight component
UV edits preserved before separation, and uses the current building's
`CSC_TAILORS_NE` material. The bale keeps its library material. The working source
opens in Pose Position with the 361-frame action assigned. All-frame checks
confirm the placement transforms the original motion consistently (maximum
vertex error 0.0000413 model units). A saved-source render confirms the bale is
visible in Blender; its missing AE attachment is still unresolved.

This source is for further authoring. Before native export, bake the assembly
placement consistently into an export copy or apply it once through the AE asset
attachment; the current animation exporter expects an unparented identity rig.
Do not remove the placement controller without accounting for its transform.
Evidence and preview: `Desktop/Codex/CSC_Storage_L/positioned-crane-20261008/`.

### Current source preparation, 8 October 2026

After the AE trial failed, Henno requested preparing his newly UV-edited source
only, leaving the subsequent export to him. The current
`Working Files/3D Art/Storage/Storage_L/CSC_Storage_L.blend` now contains one
`CSC_Storage_L_Mesh` (1,887 vertices) and `CSC_Storage_Crane_Rig` in both Export
and Review. All 33 source meshes, including the buried foundation, are combined.
The foundation can no longer be hidden separately with its old collection toggle.

Original geometry, all three UV layers, smoothing flags and `CSC_TAILORS_NE`
material were compared per face corner before joining and after saved-file reload.
Root holds 1,680 vertices; Swivel 72; Trolley 40; Hoist 95. Every vertex has exactly
one weight of 1. Load remains available as an attachment bone. The donor rig's
name, rest skeleton and existing Action are retained; no donor building geometry,
bale or slings were copied. All 361 frames were checked: static building movement
is zero, and each moving group moves. Rest and three animated poses were rendered
and visually inspected. Saved-source authoring validation has no automated errors.

The file opens in **Rest Position** for model export. To preview, select the rig,
use Armature Data Properties → Skeleton → **Pose Position**, and play frames
1–361. Return to Rest Position before geometry export. Instructions and original
component metadata are also stored in Blender text blocks. Source preparation
does not solve the subsequent conversion limitation: standard CivNexus6 three-UV
output drops skinning. Preserve all UVs in this source and use a conversion path
that retains bone bindings for the animated model. AE/cook/game remain unverified.

Backup: `CSC_Storage_L_before_rig_20261008-114851.blend` beside the source.
Evidence: `Desktop/Codex/CSC_Storage_L/source-rig-20261008/`, including
`rig-audit.json`, `installed-validation.json` and pose images. Preparation tool:
`project/tools/art/prepare_storage_source_rig.py`. It refuses installation if the
source has changed since inspection, and backs up the source before replacement.

### First authored storage animation, 7 October 2026

Henno requested a textile bale lifted from the ground and swung into the upper
storage bay, and authorized moving the load inward along the arm during the lift.
The separate revision is at
`Desktop/Codex/CSC_Storage_L/revision-01-crane-animation/CSC_Storage_L_Crane_Animation.blend`.
That first trial left the working source unchanged; see the later source preparation above.

The 361-frame, 30-FPS Action `CSC_Storage_Crane_Lift_Textile_Bale` takes 12 seconds:
ground hold, lift, short hold, 128-degree clockwise swivel, lower and end hold.
The trolley travels four model units inward during the lift and returns toward
the arm end near the end of the turn to place the entire bale inside the bay.
A larger 140-degree turn intersected the frame; the revised path clears it.
This is a single delivery, not a seamless resetting loop or unloading action.

`CSC_Storage_Crane_Rig` uses Root, Swivel, Trolley, Hoist and Load bones. Existing
crane meshes retain their coordinates/UVs; rigid groups animate each component.
Rope endpoints follow Trolley and Hoist without object-scale animation. Two sling
legs use the existing rope material. The bale is an independent instance of
`CSC_ALL_Textile_Bale`, uniformly scaled to 0.75 and bone-parented through an
attachment controller. Its source mesh, topology and all three UV sets are unchanged.
The building and bale keep their external textures in the revision's `textures/`.

Validation covers source geometry/UV parity, all-frame moving-surface clearance,
saved scene inspection and native clip/model reimport. The native crane trial
has a 12.000001-second clip and maximum sampled vertex error of 0.04213 model
units. That trial revealed the FBX/CN6 bone-basis mismatch; add-on 1.0.1 now sets
primary bone axis X / secondary Z. All 25 integration checks passed again with
an asymmetric rectangular test mesh. The installed update/ZIP is in `addon-1.0.1/`.

Read `final-audit.json` with `scene-validation.json`: the existing static scene
validator rejects `terrain_follow=bone` and building support without a static
height pivot. Those two rules are inapplicable to this moving bone attachment;
the scoped animation audit verifies its actual armature/bone and placement.
The generic validator and static exporter were not weakened. Other automated
scene checks pass; direct geometry is 1,926 export vertices plus the 20-vertex bale.

`native/` contains the separate clip FGX/ANM/FBX/NA2 and matching one-UV weighted
crane CN6/FGX/GEO. It is a conversion trial: the material still needs a one-UV
animated equivalent, and the bale remains a separate attachment. Production AST,
states, AE/cook/game integration are still incomplete. `preview.mp4` and the
editable blend are the first-animation review deliverables.

### Earlier research

`C:\Users\Shadow\Desktop\Codex\Civ6-animation-research-20261007\` contains:

- Native CN6/NA2 exports, `*-animation-study.blend` and numbered pose PNGs.
- `Blender-authored-hoist-probe.blend`/FBX, `HoistProbe.fgx`,
  `HoistProbe_Loop.fgx`/ANM and `HoistProbe-roundtrip.blend`.
- `evidence.json`, `blender-evidence.json`, `roundtrip-check.json`,
  `storage-source-inventory.json` and logs.
- `AnimProbe.cs`, Blender probe scripts and a local CivNexus6 source checkout at
  `fc3ac86c2ef3b02459e101b5930df95e0b68f70d`.

This is research tooling, not a supported production exporter. The package also
retains failed/earlier diagnostic outputs; use the final filenames above. The
`PROP_Crane_LG_AN_Quarry__0.000-26.633.na2` file is incomplete; the validated file
is `PROP_Crane_LG_AN_Quarry.na2`. The earlier
`Blender-authored-hoist-sampled.na2` records the failed 100x-scale experiment.
