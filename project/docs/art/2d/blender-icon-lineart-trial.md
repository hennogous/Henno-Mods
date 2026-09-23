# Blender icon linework: Tailor trial

Status: **superseded direction, 21 September 2026**. Henno rejected the automatic
selection of insignificant edges, such as garment collars. The v9 Freestyle trial
below remains technical evidence, but it is not the desired art-selection rule.
The tuned diffusion, LoRA, color grade, and installed atlas were not changed.

## Current direction: assistant-authored shape hierarchy

Inspect the building render and native `Buildings256.dds` examples, then choose
two levels of meaningful shapes. Primary outlines separate the major masses;
secondary outlines describe a few defining components. Mesh-object boundaries
and geometric creases are not sufficient evidence that a line belongs in the icon.
One garment includes its torso, sleeves, collar, and belt; its small construction
details should usually remain painted rather than receive individual black lines.

The v10 trial in `project/art-work/tailor-icon-v10/` implements this direction:
visually authored architectural paths plus flat-ID masks for whole garment groups.
The assistant chooses the groups; the renderer supplies their exact visible
contours. Current architectural paths are camera-specific, not reusable 3D marks.
`Tailor_Shape_Hierarchy.png` visualizes both levels and
`Tailor_Authored_Comparison.png` compares the result with v9 and the native Market.
The new candidate remains pending user review.

## Result and limits

`project/art-work/tailor-icon-v9/Tailor_Freestyle_Comparison.png` compares light,
medium, and bold Blender linework with the existing SAM result at 256 and 50 px.
The Blender variants retain the dormers' modeled shape and provide clean roof,
canopy, doorway, and prop boundaries. This supersedes the v8 experiment's broad
conclusion that automatic Blender-derived outlines are inferior to SAM: v8 used
low-resolution raster edge detection and independent bounding-box alignment.

The geometry method still cannot outline texture-only timber divisions. The
next optional addition is a companion semantic mask for the shared kit texture,
reusing its UVs; this is a proposal, not implemented or accepted. The camera and
object-size split here were tested only on Tailor. They are not universal stage
presets. Small differences between modeled and generated interior details remain
possible even when source camera coordinates are exactly registered.

## Rendering

`project/tools/blender/render_building_icon_lineart.py` loads the existing icon
renderer's 23-degree, 37 mm Tailor preset. Run with the blend loaded in background
Blender, and pass a trial output directory after `--`. It renders the normal
color image and three Freestyle passes. No blend is saved.

Only temporary line-render meshes are evaluated, welded, and given consistent
face normals. Architectural meshes (maximum dimension at least 45 source units
in this trial) receive explicit edge marks at face-normal changes of at least
45 degrees. Narrow incident faces with projected altitude below 4 working pixels
are suppressed: otherwise a tiny roof fold produces a prominent stray stroke.
Small props receive visible contours only. Architecture widths are 3.5, 5.5,
and 8 working pixels; prop widths are 2, 3, and 4. Minimum chained stroke lengths
are 18 and 25 working pixels respectively.

Freestyle occasionally introduces a stroke on an unselected shallow edge during
tessellation of this imported mesh. The renderer exports projected selected-edge
guides; the comparison accepts Freestyle ink only near those guides. Freestyle
provides visibility and antialiasing. This gate is a trial workaround and does not
by itself solve arbitrary malformed geometry. Explicit triangulation did not
improve this asset and is not part of the final renderer.

## Compositing and validation

`project/tools/comfyui/icon_pipeline/compare_building_lineart.py` takes a trial
directory plus `--input`, `--raw`, and `--sam-reference` paths. It restores the
original input alpha onto the saved ComfyUI RGB image, applies the existing
color grade, overlays antialiased Freestyle ink at 1024 px, then calls the
existing silhouette and centering functions. All layers undergo the same final
crop and resize. The generator and postprocess source files are unchanged.

Verified for the delivered comparison:

- New Blender render alpha equals the supplied v7 img2img input alpha exactly.
- Reconstructed no-SAM output equals the saved v8 output pixel for pixel.
- Saved v7 and v8 raw ComfyUI images have identical decoded pixels, so the SAM
  comparison uses the same underlying painting.
- All variants were visually inspected at 1024, 256, and 50 px.
- No replacement was made to the canonical icon or atlas.

The manifests in `project/art-work/tailor-icon-v9/` preserve source paths,
camera matrices, selected mesh groups, line widths, and raw image checksum.

## Intended production interface

Henno's target remains **building blend + stage 2/3/4 → prepared icon**. The AE
screenshot is a one-time camera/color calibration reference, not a required
input for each future building. The existing AE-matching wrapper has not yet
been refactored to that interface; this trial isolates the outline decision.
