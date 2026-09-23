# AE-matched building icon input

The Tailor icon input now has a repeatable Blender → AE color match → ComfyUI
flow. It uses the current building `.blend` for geometry and the supplied Asset
Editor screenshot for camera/color reference. The AE screenshot's sky and grass
are never copied into the transparent icon input.

From the Henno Mods workspace root on Shadow, with ComfyUI available at
`127.0.0.1:8188`, run with Python 3.12 (which has OpenCV for the existing icon
script):

```powershell
& 'C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe' `
  'project\tools\comfyui\icon_pipeline\render_and_img2img_building_icon.py' `
  'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Tailor\revision-09-terrain-attachments\CSC_TAILORS_Tailor.blend' `
  'project\art-work\tailor-icon-v7\AE_Tailor_Reference.png' `
  'project\art-work\tailor-icon-v7' `
  --name CSC_TAILORS_Tailor --reference-bounds 35 55 700 690
```

The wrapper backs up previous outputs in `History/`, then creates
`*_BlenderRaw.png`, `*_Input.png`, `*_Output.png`, color measurements, logs and a
run manifest with source hashes. It calls the existing `icon_img2img.py` with
its normal settings and does not change the postprocess. The icon atlas is a
separate review/install step.

The 21 September Tailor preset uses a 23° perspective camera, 37 mm lens,
camera distance 1.5 times the scene span, Standard view transform at exposure
0, near-neutral world `(1, 1, 0.9)` at strength 0.8, and front-left sun energy
3. `render_building_icon_input.py` excludes ground/decal context and bisects a
render-only copy at world Z=0 so the whole ground floor stays visible.

`match_ae_icon_input.py` measures roof magenta, timber, cyan cloth, pale
plaster and stone separately in the AE screenshot and Blender render. It
transfers median color and bounded contrast with soft color-family masks while
preserving the render's alpha. This handles the Tailor case where the AE roof,
cloth and stone are brighter but the Blender plaster is already brighter.
`--reference-bounds` limits measurements to the screenshot's building area;
use a different box for another screenshot. Check the report and the treated
input before trusting a new building/material palette.

Verified run: `project/art-work/tailor-icon-v7/CSC_TAILORS_Tailor_Run.json`.
The graded 1024px input is also saved as
`Desktop/Working Files/2D Art/Quarters/Tailors/CSC_TAILORS_Tailor_Input_AE_Matched.png`.
