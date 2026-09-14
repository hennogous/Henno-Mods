# Reusable prop contact sheets

The initial library arrived on 13 September 2026 with 33 blends (2 CSC, 26 base
game, 5 Rise and Fall). Its portable location is
`Working Files/3D Art/Props/CSC_Prop_Library/`; resolve Working Files on the current
host. The Windows library catalogue and source blends remain authoritative.

The contact sheets have a complete overview and category pages with two views per
asset, exact source IDs, source pack and measured visible X/Y/Z dimensions. Views
are fitted individually for inspection, not drawn to a common scale. Dimensions
include visible source decals and are source/Blender units, not AE placement units.
The source saved Worked-state visibility is used; this is not a terrain or runtime
state test. The camera uses the approved 39.35-degree elevation, with a 25-degree
yaw for volume and a perpendicular secondary view; narrow racks are framed across
their broad face. Only the cameras move. No source transforms are applied or saved.

## Refresh as the library grows

Use these scripts from the repository root, substituting the current host's paths:

```text
<Blender> --background --factory-startup --python-exit-code 1 --python project/tools/blender/render_prop_contact_previews.py -- --library "<CSC_Prop_Library>" --output "<output-folder>"
<Python-with-Pillow> project/tools/blender/assemble_prop_contact_sheets.py --library "<CSC_Prop_Library>" --output "<output-folder>"
```

Wait for `CONTACT PREVIEWS COMPLETE` before running the assembler. The renderer
discovers all top-level `.blend` files and caches previews by source blend, referenced
texture content and rendering-script content. New/changed files render on the next
run; `--only <asset IDs>` supports focused checks and `--force` rerenders selected
assets. Category sheets are assembled from the current file inventory, with unknown
props falling into Other props and missing catalogue entries marked Uncatalogued.
Numbers are sheet indices, not stable asset IDs. Use exact IDs when discussing props.

Outputs: `contact-sheets/CSC_Prop_Library_Overview.png`, category PNGs, two transparent
images and render metadata per asset in `previews/`, and `contact-sheet-index.json`.
`review-notes.json` optionally adds per-asset material-review flags; reassess these
notes when a source asset is updated. It is a simple review note, not a version system.

On Henno's Mac, use `codex-outputs/csc-prop-library/` beneath Play. Put Blender
`TMPDIR` beneath that output too. Follow the recorded Blender Metal/sandbox workaround
in the CSC skill. Pillow is available in Codex's bundled Python runtime. Source
blends/textures are read only; neither script saves edits into the library.

## Preview fidelity

The initial library's decoded scalar AO/gloss/metalness/opacity maps carry values in
the red channel. Treating AO as RGB tinted the first previews red. The renderer
extracts red as a scalar for these channels, and uses base-texture alpha for
DecalMaterial previews. These are in-memory preview corrections: source textures,
materials and blend files are unchanged. The script records corrections per asset.
Cycles studio lighting is used; Firaxis shader/state/terrain effects remain approximate.

Initial visual review flagged `CSC_ALL_Stand` and `IMP_Quarry_AN_Crate` as unusually
grey/dark. The colour issue remained under Cycles environment lighting and in an
AO-bypass diagnostic; do not assume the AO correction alone fixes these two assets.
Their source-material/UV setup needs a separate review. Their contact-sheet entries
are flagged so shape selection remains possible without treating colour as verified.

Review regenerated sheets visually, confirm current inventory coverage, inspect
transparent bounds for clipped props, and distinguish preview-only fixes from any
later changes to the actual library's Blender materials.

## Authored CSC additions

The Textile Workshop revisions retain 9 authored props (42 library assets), including
the long narrow workbench and seating bench added for uniform-scale placement.
The nearby loom and dye vats are fixed building geometry; four initially proposed
standalone variants were withdrawn before Windows registration. Discover the live catalogue rather than hard-coding those counts.
Entries with `origin: authored_blender` have a contact pivot, three UV channels,
a static Bone rig, and a `registration_status`. `verified_blender` is source
validation; it does not mean an AST/FGX/XLP registration exists.

To add another batch, stage individual blends, their declared textures and a
`catalogue.json`. Run `verify_prop_library.py` on the staged batch, then use
`add_authored_prop_assets.py --library LIB --additions STAGED --audit REPORT`.
The add tool checks all collisions before copying and refuses existing asset IDs;
updates remain an explicit case-by-case decision. Blender generation skips authored
entries, pantry preparation retains them, and catalogue finalization preserves their
state notes. Refresh previews and sheets normally afterward.

The workshop handoff includes attachment identities, full world matrices, parent
inverse matrices and support-relative matrices. Preserve the parent inverse when
reading Blender parenting; `matrix_basis` alone is insufficient. Nonuniformly scaled
supports can produce support-relative shear even while every world placement is a
valid translation/rotation/scale. The Windows exporter must preserve world placement
and implement the support relationship without blindly decomposing that relative
matrix. Ground sampling and state propagation still need AE/in-game verification.

The primary overview and category sheets mix pantry and CSC assets by use, so
scene selection can compare all available options. A supplementary
`07_CSC_props.png` sheet shows CSC assets only, for asset-budget review. Source
blends retain their existing paths. Entries starting `CSC_ALL_` automatically join the
supplementary sheet on refresh; they are not counted twice in the inventory.

## Reusability scope (revision 09)

Only custom CSC asset IDs starting `CSC_ALL_` appear in these reusable-library
sheets. Quarter-specific IDs such as `CSC_TAILORS_` are excluded from both the
overview and category pages, even if an old file remains in the input directory.
Pantry assets retain native IDs and stay included. The workshop's seven shared
props were renamed into CSC_ALL; its two specialized sail props now travel with
the workshop revision. The resulting contact-sheet inventory contains 40 assets, including nine
CSC_ALL entries (seven authored plus the two original shared CSC assets). Nine
older CSC_Attached definitions remain available for historical scenes, giving 49
catalogue records; they are excluded from the reusable sheets. Discover future
counts from the current inventory. See reusable-prop-library.md for the
required reuse proposal and Henno's review before future finalization.

## Revision 10 — one shared bench definition

Henno removed the redundant seating-bench asset. Both workshop Loom_Seat placements
now reference CSC_ALL_Workbench_Long_Narrow at uniform scale 0.5333333, preserving
the prior 16-unit length, pivot and Z rotation. Native proportions give a 6.4-unit
width and approximately 6.93-unit height. Finishing-table placements are unchanged.
The CSC_ALL_Seating_Bench and legacy CSC_Attached_Seating_Bench definitions were
removed from the active library/catalogue, with recovery copies outside it.
The pair now uses 10 custom assets: two buildings, six shared props and two
Tailors-specific props. The reusable sheets contain 39 entries, including eight
CSC_ALL assets; 47 catalogue records remain including other historical definitions.
Use revision-10-shared-bench (five blends and textures) for the current workshop.
