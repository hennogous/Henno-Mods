# Modern L1 construction/pillage retake — 28 October 2026

## CURRENT: AO correction r009

Henno's AE AO-only screenshot exposed black mottled upper end walls. Root cause:
new strip() walls had inconsistent endcap winding, with both end walls inward;
all four upper wall solids needed outward consistent recalculation. Corrected
existing saved base and Water state blends in place (backed up), preserving wall
positions and all wall UVs. No worked source edits; Wind inherits shared GEO.
Geometry AO rebaked128 samples, normal texture links disconnected, explicit UV2.
Second fault: WindTieIn shortened beams inherited occluded end-cap UV2 from full
shelter. Dedicated128² AO cell [512,512,640,640] in buildings2048 now fixes exposed
ends. Updated UV2 on those three objects in both saved masters (hidden on Water).
All other atlas pixels unchanged; props library staysr005, buildings Currentr009.

Native full-strength AO-only before/after FRONT/BACK +Water reviewed; native FGX
readback/cook pass; final source reopen checks outward contiguous wall normals.
Only two stateFGXs +buildingAO DDS change in mod; AST/GEO/placements byteunchanged.
Evidence Desktop/Codex/modern-l1-ao-fix-20261028. Use fix_ao_* scripts and current
masters; initial build.py recipe is historical and inherited wrong beam-end AO.
Initial validation/beauty render claim did not catch this. Always inspect native
full-strength grayscale AO, sampling Red from R8, and check solid face contiguity
and positive signed volume before bake. Do not hide defects with reducedAO mix.
Final correction receipt:54published hashes verified; AE regenerated only AO lower
mips (same header/full-resolution pixels) and its TEX m_ExportedTime. Configuration
comparison passes; accepted native files recooked successfully. Both actual saved
masters reopened and four outward contiguous walls each pass. AO_Before_After.png
attached, with grayscale AO-only native front/back/Water diagnostics retained.

## Initial retake (superseded AO notes below)

User paused L2 to refresh stale CON+PIL on modern base + silo + Wind/Water.
Requested native modern scaffold check and careful exposed-timber UV/grain/AO.

Current handoff: `project/docs/art/modern-level1-con-pil.md`.
Evidence: `Desktop/Codex/modern-l1-states-20261028`.
Tools: `project/tools/art/modern_states`.

Masters under Working Files/3D Art:
- `Level 1/modern/CON+PIL/revision-01/CSC_Level_1_S_Modern_CON+PIL.blend`
- `BAKERS/Wind Mill/modern/CON+PIL/revision-01/CSC_BAKERS_Mill_Silo_Modern_CON+PIL.blend`
- `BAKERS/Water Mill/modern/CON+PIL/revision-01/CSC_BAKERS_Water_Mill_Modern_CON+PIL.blend`

Worked masters unchanged: base revision04, silo revision10, Water revision02.
Water state derives from shared shell, retains current river foundation/platform.
New state GEOs bound inside existing four ASTs; no additional standalone AST/XLP.
All worked groups/placements/attachments/Water effects retained. Historical state
GEOs remain on disk for their historical consumers but no longer drive modern shells.
Other prop debris remains Henno's scope.

Full generic/Water shelter versus Wind: SiloFrontFrame hidden only on Wind,
WindTieIn hidden on generic/Water; ScaffoldSiloSide hidden on Wind to avoid an
exposed overlap inside silo. Scaffolds Construction only; DefaultBurnMaterial on
Pillaged. No emission in review. Source footing depth retained to -30.

Atlas Current buildings r008, props r005 (28 October); only AO changes.
Base state [0,512,512,1024] building2048; silo [0,512,512,768] props2048.
Water shell reuses base AO by rigid transform, river foundation uses prior AO.
All occupied worked AO pixels unchanged. AO variants must not overlap while
baking: Wind tie-ins excluded and inherit corresponding member UV2 afterward.
Exposed wood patch has horizontal grain: U must follow longest beam dimension
before object rotation. Explicit per-long-face audit passes with recorded px/unit.

Pantry survey/render confirms Modern Market uses timber Pillage_Construction_01;
Modern Bank/Electronics Factory same material; native Scaffold A/B/C timber with
Construction_props. No specifically modern scaffold set found. Existing authored
static scaffold sections reused; no animated pantry mesh statically re-exported.

Native conversion note: Water state initially merged building + river materials
into one mesh and hit Granny Save AccessViolation; separate RiverFoundation mesh
resolved it. Saved FGX then matched topology/UVs/frames/oneBone bindings and weights.
Review renderer needs to skip entirely invisible child assets before resolving
hidden owner Bone; local review filters only empty graphs, ASTs untouched.

Validation/cook pass; budget warnings are advisory (state GEO includes mutually
exclusive frames and reusable scaffolds). Review shows materials/geometry only,
not runtime burn overlay, particles or debris decals. No game deployment/test.
Publication includes backups/hash guards/AssetCloud refresh; inspect final reports
for exact receipts. L2 stays paused, not superseded or altered.

Final receipt: 102 publication hashes pass, three final saved masters automated
pass (base/Water advisory budget warning, silo none), current worked source hashes
unchanged, final isolated cook pass. AE reimport regenerated only the lower mips
of both AO DDSs; header and 2048² base pixels were byte-identical. Accepted native
FT_GAUSSIAN mips were copied into the isolated stage and recooked successfully.
Old publication hashes remain recorded as published_sha256; actual after hashes
and native-mip-rebuild.json describe the accepted native output. No repeated overwrite.
