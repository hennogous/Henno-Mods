# Painted SV XCF from a building blend

**Status:** Codex-run art workflow, calibrated on the Tailor on 22 September
2026. This produces an editable SV study for Henno's review. It does not
replace the ComfyUI SV frontend or game-state asset production.

## User input and output

The user provides the current composed building `.blend` and confirms the
output folder for the XCF. Those are the only inputs needed to start; no
building-stage parameter or AE screenshot is needed. The SV camera frames the
evaluated visible scene. Codex completes the render, painting, visual check
and GIMP packaging without an intermediate handoff. Name the editable file
`CSC_<QUARTER>_SV_<Building>.xcf` in the user's chosen folder. If no output
folder is specified, use that Quarter's `Desktop/Working Files/2D
Art/Quarters/<Quarter>/StrategicView/` folder. Keep intermediate render and
painting trials under `Desktop/Codex/art-work/`. Do not overwrite prior
trials or the blend.

## Fixed stages

1. **Render.** Run Blender 5.1 in background with
   `project/tools/blender/render_building_sv_input.py`, explicitly passing
   `--elevation 35 --clockwise-turn 10`. The renderer uses an orthographic
   1024 px transparent canvas, hides terrain/review context, bisects the
   foundation at world Z=0 on a render-only mesh copy, and applies the
   upper-left key light. Inspect the output before painting.
2. **Paint with built-in imagegen.** Use the fresh render as the authoritative
   geometry/camera reference. Use the accepted bold-outline Tailor study only
   as a style reference; do not copy its architecture or palette to another
   building. Identify the important masses and props visible in the fresh
   render and name them in the prompt. Request simplified painted surfaces,
   a restrained visible pattern of roof/canopy tiles, and prominent clean
   near-black contours around the outer silhouette and every significant
   object. Keep tiles, folds, joinery and stone joints as colored detail,
   not black contour grids. Preserve the transparent background, object
   inventory and occlusion boundaries. Save the selected painted PNG in the
   art-trial folder.
3. **Inspect at intended size.** Look for lost props, invented objects,
   camera drift, roof detail washed out, and outlines too thin after
   downscaling. If a specific defect remains, make one focused imagegen edit
   and recheck. The prompt alone is not a guarantee of object fidelity.
4. **Package in GIMP.** Run
   `project/tools/gimp/create_sv_painted_xcf.py PAINTED.png RENDER.png
   OUTPUT.xcf`, using the fresh Blender render from step 1. Its standard
   behavior makes a 1600 px transparent XCF and sizes the painted source by
   its alpha bounds to match the accepted Tailor export's approximate subject
   area at 256 px (about 121 × 117 px). The Blender render remains the scene
   reference and is recorded in the XCF report. It
   centres the art and stores GIMP Brightness-Contrast at Brightness +5 /
   Contrast 0 as a live layer filter. It reopens the XCF and verifies the
   filter exists.
5. **Deliver.** Show Henno the result; in-game judgment and any requested
   paint edits remain his review checkpoint. Do not silently package DDS,
   state variants, shadow plates or ArtDefs from this study.

Henno exports the selected XCF as the matching unsuffixed PNG, for example
`CSC_TAILORS_SV_Tailor.png`. Run
`python project/tools/comfyui/sv_pipeline/sv_postprocess.py
<exported PNG>` to produce the six Visible/Revealed and state PNGs. The
postprocessor recognizes that canonical basename without `_PreShadow`, scales
the **whole** 1600 px editing canvas to 256 px, then adds the normal shadow
plates and state treatments. Existing `_Visible_PreShadow.png` files still use
the former sprite-fitting route. For a differently named exported PNG, pass
`--from-preshadow --preplaced-canvas`; for a raw input with a canonical name,
pass `--raw-input`. Without an explicit output path, the six PNGs are written
beside the exported PNG and replace files with the same names; pass a separate
`<output folder>/CSC_<QUARTER>_SV_<Building>_Visible.png` as the second
argument for a review run.

The earlier 800 px Tailor XCF kept a 640 px painted square after a canvas
crop, making its final sprite too large. A later render-derived rule made the
Textile Workshop too small beside Henno's revised Tailor export. On 22
September, Henno accepted a 1200 px Tailor PNG canvas with a 567 × 548 px
subject alpha box. At 256 px, this is about 121 × 117 px. The current XCF
script uses that subject area as its default scale target while adapting the
painted square to each generated image's alpha bounds. It does not assume a
fixed art-square size for every building. As of 22 September, the default XCF
canvas is 1600 px; the painted square and its offsets double from the earlier
800 px composition, preserving the final image-to-canvas proportions.

## Automation boundary

Codex can run all five stages after receiving the `.blend` path and XCF
destination. Its built-in imagegen is a Codex tool and cannot be invoked by
a repository Python script.
Keep Blender and GIMP deterministic, and keep imagegen as an agent-driven
step with visual inspection. A standalone unattended script would require a
separate image-generation API workflow and credentials; do not switch to it
without an explicit user choice. When repeating this for other buildings,
the style reference should eventually be a small approved cross-Quarter
sprite sheet rather than the Tailor alone.
