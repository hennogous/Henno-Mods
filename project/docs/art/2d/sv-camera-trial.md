# Tailor SV camera trial

**Status:** review render, 22 September 2026. The established SV camera remains
the default in `project/tools/blender/render_building_sv_input.py`.

The existing orthographic review camera is at 39.3517526° elevation, facing
the building from negative Y. After reviewing a 45° trial, Henno preferred
**40° elevation** with an **apparent 10° clockwise building turn**. The helper orbits
the camera 10° counterclockwise around the evaluated scene center, which has
the same visible turn without rotating meshes or saving the source blend.
Lighting, transparent 1024 px canvas, scene-span framing, context hiding and
the render-only foundation clip remain as in the current SV input renderer.

Run from the Henno Mods workspace:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background `
  'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Tailor\revision-09-terrain-attachments\CSC_TAILORS_Tailor.blend' `
  --python-exit-code 1 --python 'project\tools\blender\render_building_sv_input.py' -- `
  'C:\Users\Shadow\Desktop\Codex\art-work\tailor-sv-camera-trial\Tailor_SV_Ortho_E40_TurnCW10.png' `
  --elevation 40 --clockwise-turn 10
```

The 40° trial, earlier 45° trial and matching baseline are in
`C:\Users\Shadow\Desktop\Codex\art-work\tailor-sv-camera-trial\`.
The trial keeps the whole Tailor and prop scene in frame. It has not yet been
run through ComfyUI, graded, fitted to 256 px, or accepted as the SV default.

## 35° painted trial

On 22 September, Henno requested a further **35°** input render at the same
apparent 10° clockwise turn. The render is
`Tailor_SV_Ortho_E35_TurnCW10.png` in the trial folder. Its imagegen study in
`imagegen/Tailor_SV_E35_Painted_Outlined_RoofDetail_v1.png` keeps bold outlines
around the major objects while retaining a restrained painted tile pattern on
the main roof and shop canopy. Simplification should not erase all roof detail.

The matching XCF is
`imagegen/Tailor_SV_E35_Painted_Outlined_RoofDetail_v1.xcf`. It uses a 1024 px
editing canvas with the same relative placement as the default building path
in `sv_postprocess.py`: a 160 px source square centered at (48, 48) on a
256 px canvas, scaled 4× to a 640 px square at (192, 192). GIMP stores a live
Brightness-Contrast filter at **Brightness +5**, Contrast 0 on the painted layer.
`project/tools/gimp/create_sv_painted_xcf.py` produces this placement and XCF
from a painted PNG. This is an art trial; the established SV camera defaults
and ComfyUI pipeline remain unmodified.

## 30° and larger XCF composition

Henno next requested a **30°** input angle, bolder black contours around every
significant object, and the scale he obtained by reducing the previous XCF
canvas from 1024 px to 800 px. The 30° render retains the 10° apparent
clockwise turn: `Tailor_SV_Ortho_E30_TurnCW10.png`. The painted study with roof
tile detail and stronger outlines is
`imagegen/Tailor_SV_E30_Painted_BoldOutlines_v1.png`.

The first 800 px XCF kept the 640 px art square at (80, 80). This was based on
an incorrect reading of "scale the canvas to 800 px" as a crop. It made the
final sprite about 28% larger. The corrected 800 px XCF scales the 1024 px
layout proportionally: **500 px** art square at **(150, 150)**, equivalent to
**160 px** at **(48, 48)** in a 256 px export. Run
`create_sv_painted_xcf.py` with an 800 px canvas was used for that comparison;
it retained the live GIMP Brightness +5 filter. These are review settings,
not new defaults for
`sv_postprocess.py`.

That proportional 500 px placement still produces a larger visible Tailor
than the old `sv_img2img.py` path: the old render's subject occupied only
part of its 1024 px source. The current XCF script therefore requires both
painted PNG and Blender render. A subsequent render-derived scale was too
small beside Henno's accepted Tailor 1200 px export. The current default
matches that export's approximate subject area at 256 px (121 × 117 px),
using each painting's alpha bounds. The 500 px XCF remains a comparison trial.
For the original Tailor XCF with 640 px art on an 800 px canvas, a manual
canvas expansion to **1200 × 1200 px**, with the existing 800 px layer
centred at **(200, 200)** and left unscaled, produced the approved export.
Use GIMP's canvas-size command, not image scaling. The Tailor XCF on disk
still showed its previous 800 px canvas during the 22 September review, so
save the edited XCF if this canvas change is to persist in that file.

## Return to 35°

Henno approved the bolder outlines from the 30° study and requested a return
to the 35° view. The current painted trial is
`imagegen/Tailor_SV_E35_Painted_BoldOutlines_v1.png`, using the earlier 35°
Blender render as the geometry reference. Its matching 800 px XCF is
`imagegen/Tailor_SV_E35_Painted_BoldOutlines_v1.xcf`, made with the earlier
oversized 640 px placement. See
[`sv-imagegen-xcf-workflow.md`](sv-imagegen-xcf-workflow.md) for the repeatable
blend-to-XCF process. The camera choice is selected for this painted study;
the production SV renderer's default is not changed.

That original oversized Tailor XCF is also stored beside the Quarter's SV source PNGs as
`C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Tailors\StrategicView\CSC_TAILORS_SV_Tailor.xcf`.
Henno exports it to `CSC_TAILORS_SV_Tailor.png`; `sv_postprocess.py` now
recognizes that unsuffixed PNG as an already-composed editing canvas.
