# Bakery prop kit — updated 17 October 2026

The Bakery redo has seven editable prop masters and installed native assets. Henno explicitly authorised Astra to build, export, install and attempt initial attachment placement; AE owns the current saved assemblies. Revision 07 fixes the oven's pinched crown mapping and consolidates every basket/cart bread surface into one ImageGen swatch, freeing three atlas cells. It retains the raised texture-only bread piles, square trays, bolder cart, enlarged dough and independent peel. Geometry, AO and current AE placements are preserved.

## Source and review locations

- Editable sources: `C:\Users\Shadow\Desktop\Working Files\3D Art\BAKERS\Bakery\revision-08-prop-kit`.
- Combined review kit: `CSC_BAKERS_Bakery_Prop_Kit.blend` in that folder. The seven independent `.blend` masters sit beside it, with an exact portable texture snapshot in `textures/`.
- Current review/export package: `C:\Users\Shadow\Desktop\Codex\Bakery-redo-20261016\production\revision08`. Initial installation and parent-change evidence remains in its parent `production` folder.
- Backups of overwritten runtime inputs and the previous atlas: `production\before-install`.
- Canonical atlas: `C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Props\Current`, release `2026-10-17_Shared_01_r031`; immutable snapshot under `Releases` and pointer in `CURRENT.json`. Previous releases and source revisions remain historical snapshots.

The kit is an organised collection of masters, not the final parent building assembly. Reconstruct saved parent ASTs with `project/tools/blender/render_ae_asset.py` for subsequent building render work.

## Installed assets

Each identifier has a matching `.blend` master, `Assets/<id>.ast`, and `Geometries/<id>.fgx` / `.geo`. All use `CSC_ALL_Props_01`. The initial delivery registered all seven. During revision 07, concurrent AE edits removed Round/Oval basket XLP entries; these remain editable/native inventory, while Peel/Dough/Long/Cart/Oven retain unique XLP entries. This update preserves that live registration choice and does not recreate removed entries.

| Identifier | Export vertices | Triangles | Content |
|---|---:|---:|---|
| `CSC_BAKERS_Oven_v2` | 879 | 427 | Original oven shape remapped to shared patches |
| `CSC_BAKERS_Peel` | 60 | 32 | Wooden baker's peel |
| `CSC_BAKERS_Dough_Set` | 308 | 374 | Dough balls, mixing bowl and flour opacity card |
| `CSC_BAKERS_Bread_Basket_Round` | 288 | 250 | Rectangular tray, mixed bread mapping A |
| `CSC_BAKERS_Bread_Basket_Oval` | 288 | 250 | Rectangular tray, mixed bread mapping B |
| `CSC_BAKERS_Bread_Basket_Long` | 288 | 250 | Rectangular tray, mixed bread mapping C |
| `CSC_BAKERS_Bread_Cart` | 1,458 | 1,012 | Substantial handcart, white/yellow canopy and rectangular stocked trays |

Individual baked loaves remain texture only. Each basket has one generic raised carrier (48 source vertices, 37 faces) with a broad crown and shoulders; individual loaf silhouettes, scoring, overlap and crust are painted. The cart contains two such basket piles and no individual loaf meshes. Raised carriers replace revision 02's flat fill faces to satisfy Henno's higher-stack instruction. Crown and shoulder regions share one bread swatch, using its upper and lower panels respectively. Basket weave repeats around sectors to preserve its aspect. Basket variants remain independent assets for duplication and rotation. The cart does not depend on nested basket attachments.

Revision 04 trays have straight walls and right-angle corners, with a footprint of 11.76×8.4 source units. Only the generic bread carriers have softened/chamfered corners. `Round`, `Oval` and `Long` describe the painted bread arrangements; all tray shells are rectangular. The shallower footprint fits the existing three-basket stand layout without moving attachments. Saved-source bounds and actual parent transforms show minimum separating gaps of 1.4958 (Round/Oval), 0.1643 (Round/Long), and 0.2169 (Oval/Long) source units. A true top view independently confirms clearance.

Revision 05 preserves every source vertex, face, object transform, weight, UV2 and UV3. Crown UV1 now samples nearly the full assigned bread patch with a 1.5% inset, so the three dominant painted loaves remain visible rather than cropping them into fragments. Side textures span shoulder height continuously without restarting at each band. Four basket/cart native assets receive UV-only updates; no individual loaf geometry was added.

### Bread swatch usage

The native audit covers every installed geometry mesh bound to the shared prop atlas (36 geometries through 39 assets), using fresh FGX readback and positive-area UV triangle clipping. Before consolidation, all four bread cells had real consumers. Henno then explicitly requested changing the mapping to use one swatch; revision 07 migrates those consumers rather than simply deleting active textures. Native CN6 UV1 V is already measured from the image top, so it must not receive the Blender-style `1−V` conversion.

| Swatch | Slot | Native consumers | Triangles sampling it |
|---|---:|---|---:|
| Mixed loaf crown and side views | 61 | Round/Oval/Long baskets, cart | 410 |

Counts describe native geometry once, excluding repeated attachment instances and XLP selection. Slots 10, 30 and 62 are now cleared, removed from active region allocations and available again; all three have zero native triangle intersections after migration. Slot 61 retains the legacy key `bakery_round_crust` for tool compatibility but contains mixed round/oval/long bread. Its upper 75% holds three large top-view loaves; the lower 25% provides two stacked horizontal side profiles. UV reflections/rotation provide variety; asset identifiers remain stable. The current standard Bakery uses two Long basket instances. The alternate had all three variants plus cart at task start, but its AST was externally removed during this pass and was not recreated. Evidence: `production/revision07/native-bread-atlas-usage*.json`, `bread-consolidation-UV.json` and per-cell UV overlays.

The cart has a 28×17 bed (previously 24×15), deeper timber walls, thicker posts, broad wood wheel rims/spokes/hubs with restrained iron tires, and a 31×21 canopy with a raised ridge. Painted timber grain follows structural members. The carrier piles remain clear of the canopy and the frame is visible at reduced scene size.

All three dough balls are 40% larger in XYZ than revision 01, with the mixing bowl and flour-card geometry unchanged. Dough remains volumetric. The peel remains an independent `.blend` master, native asset and parent attachment; there is no peel geometry inside `Dough_Set`.

Oven geometry retains its original 233 editable vertices. Current dome UVs use constant-scale side bands and a planar crown chart; the chimney uses Cartesian charts. Earlier cylindrical angle mapping pinched the crown and was replaced in revision 07. The current 8×16 running-bond swatch is sampled at a consistent physical scale rather than wrapped once around the entire dome. Existing stone, fire and log appearances occupy shared patches. Original source remains at `Working Files\3D Art\Props\Bakers\CSC_BAKERS_Oven_v2.blend`; use the new revision source for future edits.

## Shared material and opacity

r025 added eleven surface patches in previously free slots and seven self-AO allocations in Bakers Stage3. r026 updated brick/bread paint and enlarged dough. Those Bakery artistic additions were procedural, not ImageGen.

r027 uses built-in ImageGen for the bread top arrangements, bread-stack sides, cart timber, wicker and striped canopy base colours. The source bread page was refined against the actual approved concept to remove photographic detail. Raw generated images, the initial bread edit target, concept/style reference, exact prompts, source hashes and measured quadrant crop rectangles are retained in `Current/atlas/sources/imagegen-r027/` and the delivered source provenance folders. `generation-manifest.json` and `provenance.json` identify their roles. The generated terracotta quadrant is unused; the existing oven paint remains unchanged.

Surface changes from r026 are confined to slots 8, 9, 10, 29, 30, 61 and 62; cart timber 9 and bread-stack side 10 were previously free. Source crops are packed deterministically into the permanent atlas layout. Calm flat normals avoid converting painted highlights/shadows into physical height; technical maps were not independently image-generated. AO was rebaked only for the baskets and cart. All other surface pixels, nonallocated AO, opacity and emissive maps remain unchanged. Independent readback verified the actual ImageGen crops in the canonical atlas and that native cart UVs sample the new material/bread regions. Release hashes and deterministic rebuilds pass.

r028 changes only basket/cart geometry, their four existing self-AO cells, and corresponding source/provenance metadata. Every surface, opacity and emissive PNG, non-AO runtime DDS, shared material and XLP is byte-identical to r027. Both parent Bakery ASTs and the oven/dough/peel native geometry remain byte-identical. No new ImageGen artwork was needed for the tray shape correction.

r029 replaces only base-colour bread cells 10, 30, 61 and 62 using a built-in ImageGen edit of the prior accepted source page. Each top quadrant has three larger loaves; the side quadrant has two broad loaves. Raw artwork, prompt, source/crop hashes and quadrant rectangles are retained in `Current/atlas/sources/imagegen-r029/` and `revision-05-prop-kit/art-provenance/imagegen-r029/`. All N/G/M/AO/O/E maps and all other base-colour pixels remain byte-identical to r028. An independent audit verified raw ImageGen crop-to-patch-to-shared-atlas pixels, native triangle/geometry/UV2/UV3/weight preservation, installed files and release hashes. All ASTs remain unchanged.

The shared Landmark material now binds `CSC_Props_Shared_01_O` through its `Opacity` slot. This is a separate map, not base-colour alpha. Every previously occupied UV1 region is solid white. The new flour region supplies coverage for a single tabletop face beneath the dough and bowl. It is a mesh card, not terrain projection.

The O texture is `Generic_OPAC`, `PF_R8_UNORM`, box filtered with complete mips and gamma 1. The DDS uses the established scalar RGB header (`DDPF_RGB=0x40`, 8-bit red mask `0xff`). Native string properties such as `m_ClassName` must use their `text` attribute. Soft coverage in the Blender preview is not evidence of exact Firaxis opacity behaviour.

## Revision 06 texture and relief update

r030 uses built-in ImageGen edits for the muted bread sheet and clearer oven brick sheet. The brick edit follows an exact 24×12 running-bond guide. Raw outputs, prompts, crop hashes and the guide are retained in canonical `Current/atlas/sources/imagegen-r030/` and source `art-provenance/imagegen-r030/`. Base-colour changes are confined to the oven brick and four bread regions (slots 34, 10, 30, 61 and 62). All other base-colour pixels and all G/M/AO/O/E maps remain unchanged.

Normal maps are technical derivatives of aligned relief rather than independently generated RGB artwork. Brick mortar and bevels follow the ImageGen guide; bread uses broad fitted loaf domes with shallow recessed masks on the actual pale scoring. Wicker reeds and timber grooves/knots follow their accepted ImageGen artwork. Existing registered normal relief is strengthened by material family; original oven stone/log normal crops were recovered through pixel-exact matching base-colour provenance. Smooth materials stay calm. Height fields, scoring masks and the method/strength records are retained under `relief-r030/` in both provenance locations. Normals are calculated at the actual 120-pixel patch size and capped at 60°; the stronger relief is in the runtime map, with Blender Normal strength 1.

Matching-light colour and neutral-material comparisons verified the relief independently of painted shadows. Stray bread cuts found in the first pass were removed by tightening masks to the painted scoring; all four score overlays were inspected. The brick joint alignment audit reports a maximum 0.399-pixel discrepancy at runtime patch resolution. Representative timber, masonry and sackcloth diagnostics also show the broader shared-map changes. These shared N changes affect every asset sampling those atlas regions.

Revision 06 preserves every source vertex, face, transform, weight and all three UV channels. All seven installed prop AST/FGX/GEO files remain byte-identical to revision 05. Both current saved parent assemblies are preserved through this texture-only installation. The standard Bakery AST had been externally edited since revision 05 (last write 17 October, 12:12:27; SHA-256 starts `4f42f379`); those edits remain intact. The alternate retains its prior `f583546d` hash. Historical reverse-AST comparisons below describe the earlier delivery, not later AE edits. Final source, native-file, atlas and installed-texture evidence is in `production/revision06`; fresh colour reviews and the saved-AST alternate review use the updated textures. Cooking and in-game material response remain untested.

## Revision 07 mapping and atlas consolidation

Henno's AE screenshot exposed the remaining oven defect: cylindrical UVs pinched the brick columns into spokes at the dome crown, and their angular origin did not match the dome centre. Revision 07 uses constant-scale side bands around the fitted centre `(0, -3.9)`, planar XY crown mapping and Cartesian chimney charts. The existing 233-position oven geometry is retained. The crown/side chart boundary remains visible in close views, but there is no polar singularity or radial starburst. Hero, true-top, high, rear and bright Standard-transform reviews were inspected.

New built-in ImageGen artwork follows an 8-column/16-course running-bond guide, representing 8×4-unit bricks over a 64×64-unit patch. Narrow darker sand mortar and restrained bevel contrast replace the previous pale outlines. Aligned technical normals use roughly 26° p90 tilt, capped at 45°; no new cap swatch is allocated. Existing brick slot 34 is reused.

The same revision consolidates all bread to slot 61 as described above. Built-in ImageGen painted the exact 75% crown/25% shoulder guide, then a second ImageGen edit reduced orange saturation while preserving the arrangement. A final bottom-panel edit creates two stacked horizontal side profiles; deterministic cropping retains the accepted crown exactly. Crown UVs sample image U `.02–.98` / V `.02–.73`; final shoulder UVs sample U `.02–.98` / V `.77–.98`, continuously across each whole side. All three baskets and both cart piles use that single patch. The three retired bread cells are explicitly blanked in the deterministic packer and returned to free allocations after native UV proof. Historical releases retain their original textures and UV layouts.

Only oven/bread UV1 faces change. Source geometry, face topology, normals, transforms, weights, UV2/UV3, AO, opacity and emissive maps remain intact. Basket/cart/oven native FGX/GEO updates preserve all AST identities and saved placements; the dough and peel native assets remain unchanged. B/N/G/M changes are confined to slots 34/61 and the three cleared cells. ImageGen raw outputs, all three bread prompts, brick prompt, layout guides, height/scoring masks and crop provenance are under source `art-provenance/imagegen-r031/` and canonical `Current/atlas/sources/imagegen-r031/`. Saved-source image-path checks verify every master and the combined kit resolve the exact revision 07 texture snapshot.

## Revision 08 emissive binding and UV3

Henno explicitly requested switching the shared props material to the original window/coals texture. `CSC_ALL_Props_01` now binds existing `CSC_Atlas_E` in its Emissive slot. The unused `CSC_Props_Shared_01_E` is entirely black and remains unchanged. No texture was generated, copied into the shared sheet or re-exported; no atlas release was made. The canonical library remains r034 (including the intervening Cafe changes), and revision 08 keeps a portable r034 snapshot plus a lossless decode of the actual legacy runtime emissive DDS.

Six oven opening faces (112–114 and 116–118; 12 native triangles) sample the legacy coals crop `[192,184,248,232)` through UV3, aligned affinely with their existing fire UV1 mapping. All nonopening UV3 coordinates remain unchanged and sample black. Native positions, normals, tangents, UV1/UV2, weights, triangles and counts remain identical to the fresh live pre-edit FGX. Only the oven FGX changed; GEO, all texture/TEX/XLP files and every canonical library file remain untouched.

The direct material switch exposed potential window sampling on other shared props. The audit covers 44 geometries and includes constant/degenerate UV3 triangles. To preserve their prior non-glowing appearance, 49 `EmissiveEnabled` booleans were changed from true to false across 20 ASTs, only in affected visible mesh-group states. These are per-asset/per-state flags, not material edits or geometry changes. All other AST semantics, including placements, materials, visibility and culling, are preserved. The oven's Worked emission remains enabled. Automatic approval initially rejected the unmitigated switch; the ordered flag-first installation passed after the effective-emission audit showed no unintended enabled consumers.

Evidence: `production/revision08/installation-report.json`, `native-UV3-preservation.json`, `emissive-state-mitigation/report.json`, `legacy-emissive-audit-after.json`, `saved-source-preservation.json` and `final-verification.json`. All seven masters and the combined kit validate. `Oven_Emission_Only.jpg` verifies that only the openings emit; this is a diagnostic, separate from production icon/SV renders, which continue to omit emission. Cook/game acceptance remains untested.

## Parent assembly changes

The initial installation added the reused `CSC_ALL_Workbench_Wide`, dough set, peel, one basket of each shape and remapped oven to both Bakery ASTs, plus the cart in the alternate's requested road position. It retained the normal compact stand/table and removed superseded bread attachments and the alternate's extra fixed sales stands/stock. Subsequent AE edits are authoritative. During revision 07, the standard was saved again (captured hash starts `0c96d47a`, last write 12:41:51), the alternate AST was removed, Round/Oval XLP entries were removed, and shared TEX/XLP files changed. These concurrent edits were preserved. This revision writes native geometry/textures and canonical sources, not AST/TEX/XLP files; final parent review uses the saved standard.

The old oven mesh group embedded in the parent geometry is hidden in all five states, with the remapped standalone oven fitted in its place. The parent Bakery FGX was not regenerated. Original roof bindings, architecture, CON+PIL, pillage decals, cobbles and unrelated attachment data remain unchanged. New prop assets appear in Worked/Unworked and are hidden in Construction/Pillaged/Unbuilt; new attachment culling is PERMANENT.

First-pass Blender-space positions are below. AST positions divide these coordinates by ten; AST Z orientation is the negative Blender angle in radians.

| Attachment | Position | Blender Z | Scale |
|---|---|---:|---:|
| Workbench | (-207, -83, 0) | 0 | 1 |
| Dough set | (-207, -83, 14.08) | 0 | 1 |
| Peel | (-201, -87, 14.18) | pi/2 | 1 |
| Round basket | (-174, -85, 11.8) | -0.8 | 0.65 |
| Oval basket | (-165, -89, 11.8) | -0.8 | 0.65 |
| Long basket | (-170, -92, 11.8) | -0.8 | 0.65 |
| Oven | (-205.684005616, -42.550399918, approximately 0) | 1.620197077 | 0.5 |
| Cart (alternate only) | (-111, -127, 0) | -0.5 | 1 |

Workbench, dough and peel are separate parent attachments. Move them together when adjusting the work area. The flour face sits approximately 0.115 source units above the table in the reviewed assembly. No global workbench asset was modified. Road layout assets were not edited; the cart's road position is specifically authorised by Henno.

## Validation and remaining review

All seven final saved sources and the combined kit pass authoring validation. Native FGX readback matches exported positions/UVs, with maximum coordinate error below `5e-6`; all have three UV channels and one static Bone influence at weight 255. Native files match exported copies. Five currently selected XLP entries are unique; Round/Oval are retained inventory outside the current XLP. The initial 15 attachment transforms agreed with independent reconstruction within `3e-5`; later AE edits supersede that historical layout.

Whole-AST reverse comparisons against the independently captured pre-install files show that reversing only the recorded attachment edits and five old-oven visibility edits restores the complete prior semantic AST. A separate parent audit verified preservation of all other AST content, old surface pixels, nonallocated AO pixels, old opacity coverage, state/material bindings, scalar header and installed file parity.

Current evidence is in `production/revision07/final-verification.json`, `revision-install-report.json`, `user-revision-source-audit.json`, `kit-validation.json`, `saved-source-image-resolution.json`, `oven-crown-singularity-proof.json`, native bread usage reports and per-asset validation/export reports. Source checks verify unchanged geometry, transforms, weights and UV2/UV3, with only intended UV1 edits. The independent r031 audit checks the 693-file runtime baseline, exact ImageGen raw crops/composite through atlas and installed DDS, immutable release hashes, freed cell pixels and native triangle-corner attributes. Revision 06 retains the wider shared-normal audit; revision 05 retains prior crown/side UV changes; revision 04 retains initial tray-fit evidence. Revision 02 retains dough-size/bowl/flour checks. Initial placement evidence remains in `production/final-verification.json`, `install-report.json`, `oven-remap.json`, and `oven-parent-transform.json`. These earlier placement audits are historical; later AE changes remain authoritative. Current reviews include oven hero/top/high/bright/rear views and the consolidated basket/cart.

The parent reviewer compared actual tray/cart views with the approved concept. Revision 03 corrected stretched bread shoulders, stretched wicker, misaligned timber grain and canopy-frame intersections; hero/top/rear/side and reduced cart views were inspected. Revision 04's straight-sided tray hero and true-top three-tray layout were independently inspected for shape, bread-carrier fit and clearance. Revision 05's mapped round-bread tray and cart show distinctly fewer, larger forms and a calmer appearance. Final views retain the bolder wheel/frame silhouette, taller abundant stock and functional clearances. The standard SV preset excludes terrain context and road decals, so assembly images are prop/composition previews.

AE cooking, in-game appearance, opacity coverage and terrain/slope behaviour have not been tested. Final placement refinement remains in AE. Do not rerun the initial installer over subsequent AE edits: it is a scoped one-time publication recipe with baseline assertions, not an assembly synchroniser.
