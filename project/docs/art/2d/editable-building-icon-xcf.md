# Editable building icon XCF from a blend

Use `project/tools/gimp/create_building_icon_xcf.py` to create an editable GIMP
file from a composed building `.blend` and a required stage (2, 3 or 4).
The stage selects `project/tools/gimp/icon_template_stage_<stage>.xcf` so each
stage can carry its own preset paths. The script renders the 1024 px
transparent Blender image, adds it as the top layer in that template, and
saves `<blend stem>_icon.xcf` beside the source blend. It keeps
the template's paths and layers. It does not stroke any paths, modify the
source blend or overwrite the template.

On Shadow, run from the Henno Mods workspace:

```powershell
& 'C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe' -B `
  'project\tools\gimp\create_building_icon_xcf.py' `
  'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Tailor\revision-09-terrain-attachments\CSC_TAILORS_Tailor.blend' 3
```

The PNG, Blender and GIMP logs, and validation report go to
`Desktop/Codex/art-work/<building>-icon-editable/`. Use `--render-png` to set
another PNG location. If an output XCF exists, the script copies it to that
work folder's `History/` before replacing it. The report checks the template
path names, stroke structure and control points after saving and reopening
the output XCF.

The rendered pixels are positioned 6% of the canvas height higher by default:
61 px on the 1024 px canvas. The script writes a second transparent PNG with
the pixels moved up inside a 1024 px canvas, then places that PNG in a GIMP
layer at offset `(0, 0)`. This keeps the perspective and lighting from Blender
intact. The separate raw render PNG remains unshifted. Use
`--vertical-shift-percent 0` for no move, or provide another percentage when
aligning a different building. The script rejects a move that would crop
visible pixels at the top of the canvas.

The current icon skill provides one calibrated camera and light setup from
the Tailor stage 3 trial: 23° elevation, 37 mm perspective lens, 1.5× scene
span distance, Standard view transform at exposure 0, near-neutral world
`(1, 1, 0.9)` at strength 0.8, and front-left sun energy 3. The script's
stage 2/3/4 camera mapping currently uses this same tested setup with automatic
scene-span framing. The stage matters today for template selection. Distinct
stage camera presets have not been calibrated and should be added to
`CAMERA_BY_STAGE` only after a visual comparison. A missing stage template is
reported before Blender starts. `--template` can override the selected file.

The Blender helper hides terrain/decals, clips the buried foundation below
world Z=0 and keeps the full ground floor. The XCF handoff stops at the
render and template paths; the user can edit and stroke those paths in GIMP.
For scenes without an editable World Background node, the renderer creates a
temporary node-based world in memory and still uses the calibrated light
settings. The blend is never saved. The wrapper now asks Blender to return a
failure code for Python exceptions and renders to a fresh pending file, so a
failed run cannot silently reuse an earlier PNG.

Tailor verification, 22 September 2026: the script generated
`CSC_TAILORS_Tailor_icon.xcf` beside the current Tailor blend.
GIMP reopened it with one 1024 px render layer and all nine paths in the
earlier shared template;
path control coordinates were unchanged within 0.001 px. The regenerated layer
stays at offset `(0, 0)`; the visible pixel bounds moved from Y=217–940 to
Y=156–879, exactly 61 px upward within the layer.

After `icon_template_stage_3.xcf` replaced the shared template, the stage 3
Tailor run was repeated and preserved all ten paths in the current template.

Textile Workshop verification, 22 September 2026: a stage 2 run against
`CSC_TAILORS_Textile_Workshop_FINAL.blend` used the current
`icon_template_stage_2.xcf` and created the render and
`CSC_TAILORS_Textile_Workshop_FINAL_icon.xcf`. The renderer created a
temporary World Background for this blend. GIMP reopened the XCF with the
template's one path and one 1024 px render layer at `(0, 0)`; the pixels were
moved 61 px upward inside that layer.
