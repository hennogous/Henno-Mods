# Image-guided icon boundary prototype

**Status:** Tailor proof of concept, 21 September 2026. It is a path-authoring
aid, not the accepted icon pipeline or a replacement for the installed atlas.

## Purpose

The prior manually drawn image-space paths picked meaningful shapes but often
missed their rendered boundaries. `project/tools/comfyui/icon_pipeline/snap_icon_paths.py`
uses OpenCV Intelligent Scissors to trace the image edge between a small set of
guide points. The assistant still decides which major shapes receive lines;
the algorithm only improves where the selected line runs. It does not choose
all icon masses, know which garment details are unimportant, or solve weak
texture-only boundaries.

`run_edge_snapped_icon_prototype.py` runs the snapping and imports the resulting
paths into GIMP 3. The XCF has only the original render layer and unstroked
editable paths. `create_editable_icon_outlines.py` generates the outer silhouette
path from render alpha. The colored review PNG is separate and has no effect on
the XCF or icon pixels.

## Tailor run and outcome

Trial assets are under `C:\Users\Shadow\Desktop\Codex\art-work\tailor-edge-snap\prototype\`.
`guide_points.json` defines six selected boundaries: the main roof eave, two
stall canopy edges, upper story floor beam, doorway arch, and cutting cloth.
The run saved `Snapped_Paths_Review.png`, four enlarged crops, `snap_report.json`,
`snapped_paths.json`, and `Editable_Snapped_Paths.xcf`.

The roof eave test used seven coarse anchors and produced a 31-point editable
path. Visual inspection shows the snapped line follows the rendered roof edge
more closely than the earlier broad hand-drawn curve. The canopy, floor beam,
and cloth were also inspected in enlarged previews. Some tile bumps and doorway
stone joints still need human review and curve simplification.

The one-command runner was exercised with Python 3.12, OpenCV 4.10, and GIMP 3
on Shadow. The XCF was saved and reopened: seven paths (including the outer
silhouette), one source render layer, zero painted outline layers. Path control
coordinates survived the round trip within 0.001 px.

## Reuse

Edit the `anchors` in a guide JSON for the current camera render. Use one path
per desired visible boundary, leaving collars, shingles, stone courses, and
other small texture details out of the guide set. Add anchors where nearby
edges might attract the trace. The runner rejects a segment when the snapped
line wanders beyond `max_excursion_px` from its straight guide segment. Review
the full overlay and enlarged crops before using the XCF paths. The code then
simplifies pixel contours with `simplify_px` to make the paths easier to edit.

Example on Shadow (PowerShell):

```powershell
& 'C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe' -B `
  'project\tools\comfyui\icon_pipeline\run_edge_snapped_icon_prototype.py' `
  '<render.png>' '<guide_points.json>' --output-dir '<Codex trial folder>' `
  --gimp-console 'C:\Users\Shadow\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe'
```

Use `--overwrite` only when intentionally rebuilding the same trial folder.
This prototype begins with an existing render and manually selected guide
points. It has not been wired into the planned `.blend` plus stage 2/3/4
prepared-icon command, the tuned ComfyUI img2img output, or the atlas.
