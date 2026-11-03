# Current: corrected normals and compact emissive installed

**Current material delivery, 27 October:** buildings **r007**, props **r004**.
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

# Modern Water Mill first model and shelter finish — 27 October 2026

Complete and installed. Current reusable base:
Working Files/3D Art/Level 1/modern/revision-03-finished-shelter/CSC_Level_1_S_Modern.blend.
Water master: BAKERS/Water Mill/modern/revision-01/CSC_BAKERS_Water_Mill_Modern.blend.
Durable truth: project/docs/art/modern-building-kit.md. Evidence and review images:
Desktop/Codex/modern-water-mill-v1-20261027/. 102 published files hash-verified.
Installed masters zero errors; Water has only advisory 2397>2200 vertex warning.
Base 1560 vertices / 868 triangles; Water 2397 / 1345 before reusable props.

Shelter: closed roof underside, solid wood gable, finished barge edges, side bearer
beams and painted supports. Wind Mill retains its AST and silo-side support exception.
Water concept is explicitly INSPIRATION ONLY. Reusable base dimensions and historical
foundation are authoritative. No scaling; historical foundation preserved/retextured.
Intake reused left of shelter; lower front window removed only from Water version.
Separate pallet/trolley attachments. Shaft/compact turbine within old wheel envelope.
Reused painted casing panels/rivets (no new surface artwork). Evaluating appended
object transforms before placement is essential: roof and footing have user edits.

Native Firaxis FX_Rock2_Wake reused from DIS_CTY_AWW worked-flow timeline. Trial
WORKED_A anchor at (39,20.5,-23), scale .65. No live FX/game confirmation; datum
based on old wheel bottom -22.78, not measured river height. Blender static renders
omit wake. Modern-era Water variant installed. Historical CON+PIL retained.

Building atlas current r003: surfaces1024 unchanged; AO2048, Stage2 TL1024 quarter,
base512 block at0,0; Water building512 block at512,0. Props r002 AO Water machinery
uses256..512 square. All surface maps byte-identical. Global AO_allocations is
current, older nested props mapping is provenance. Existing prop AO cells preserved.

Latest user asks why modern props atlas is scatter-shot. Answered during work:
selected historical material slots were copied and modern patches placed in spare
cells, leaving a sparse, poorly grouped surface layout. This was an overly literal
interpretation of reuse, not an engine requirement. A coherent compact arrangement
by material families would be better; repacking needs UV remapping but can preserve
appearance. User has NOT yet instructed a repack. Do not silently remap on that
question alone. Surface atlas and per-model AO allocations have distinct purposes.
# Latest: painted kit / compact props atlas, 27 October 2026

FOLLOW-UP: Henno says normals were messy and asks to avoid repeated reminders.
Strengthened civ6-art entrypoint plus texture-image-generation paint/normal gate:
B-only, neutral N-off/on with two oblique lights, B/N feature registration,
actual mapped scale and converted-result checks, evidence before completion.
CSC delivery gate routed to it. Current r004/r003 normals NOT visually accepted;
prior technical PASS does not prove material quality. Existing recipe has crude
mortar threshold, dark roof lines raised as seams, contrast-based grain and some
old normals kept after B repaint. Do not reuse it as validated best practice.
That guidance-only follow-up was superseded by the completed correction documented above.

User authorized repack, stronger aligned normals, richer Firaxis-style B painting,
entrance-floor removal and propagation of human geometry edits. Completed in
Desktop/Codex/modern-kit-refinement-20261027. Current base is Level1/modern/
revision-04-painted-kit; Water revision-02-painted-kit; silo revision-10-painted-kit;
flour props revision-02. Full paths in project/docs/art/modern-building-kit.md.
Buildings atlas r004; props r003. Props now compact4x3 material block at TL, 128px
cells in1024; AO independent2048, same allocations with base/Water rebakes.
All four current props geometry consumers migrated. Base1496/840; Water2333/1317.
Human source geometry preserved outside requested floor/back wall and notched
foundation. Source/native validation and isolated cook pass; ASTs/placements,
ArtDefs/XLPs unchanged. Inherited CON/PIL degenerate warnings, FX/game untested.
Publication verified157files; cache refreshed29records. Final validation recovery
normalized Windows path separators and supplied asset-named reports for two props
sharing a directory. No source rollback or duplicate native install.
Final comparison images/Historical_Modern_Wind_Mill_SideBySide.png; same icon angle,
both lens0.78 for full sail framing. Water full review images/Modern_Water_Mill_Review.png.
Do not rerun old builder scripts over these current user-editable masters.

