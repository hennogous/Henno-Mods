# Icon Pipeline Implementation Notes

Operational notes for CSC's ComfyUI-assisted building/resource icon scripts.

## Output paths

`project/tools/comfyui/icon_img2img.py` and `icon_postprocess.py` default to:

```text
C:\Users\Shadow\Desktop\Working Files\Icons\Buildings\ComfyUI output
```

Override with:

```text
CSC_COMFYUI_OUTPUT_DIR
```

Older dropzone-style runs used:

```text
C:\Users\Shadow\Desktop\Working Files\Dropzone\comfyui
```

## rembg / ONNX provider

`icon_postprocess.py` should create rembg sessions with the CPU provider explicitly:

```python
new_session("u2net", providers=["CPUExecutionProvider"])
```

The Windows Python environment has `onnxruntime-gpu` installed, but CUDA 12 DLLs are not on PATH. Letting rembg probe default providers causes noisy CUDA provider errors even when CPU fallback succeeds.

## SAM fallback

`sam_outline.py` is optional. If absent or broken, the supported fallback is silhouette-only outlining without printing a scary stack/error message.

SAM checkpoint path:

```text
C:\Users\Shadow\.cache\civ_supply_chains\sam\sam_vit_b_01ec64.pth
```

Override with:

```text
CSC_ICON_SAM_CHECKPOINT
```

## Cached ComfyUI runs

ComfyUI can report a fully cached successful run with an empty `outputs` block when the workflow is identical. `icon_img2img.py` avoids this by making `SaveImage.filename_prefix` unique per run and retrying once if history has no images.

Input uploads use a unique run ID for the main source image to avoid stale/ambiguous uploads. The Canny guide is intentionally always written/uploaded as `canny_input.png` so the output folder does not accumulate one Canny file per run.

## Transparent input semantics

The icon img2img path treats transparent input as intentional silhouette:

- Canny is alpha-aware.
- Generated RGB is masked back to the input alpha before saving raw output.
- Postprocess skips rembg when raw input already has transparency.

Final output filenames are derived from the input filename by replacing `Input` with `Output`, e.g.:

```text
CSC_BAKERS_Wind_Mill_Input.png -> CSC_BAKERS_Wind_Mill_Output.png
```

## Postprocess toggles

`icon_postprocess.py` has top-of-file master toggles for each effect:

- background removal;
- rembg padding;
- Canny crease overlay;
- structural outlines;
- SAM outlines;
- silhouette outline;
- canvas centering.

Each can also be overridden with `CSC_ICON_ENABLE_*` environment variables.

## Outline controls

- Outline thickness: `OUTLINE_THICKNESS` / `CSC_ICON_OUTLINE_THICKNESS`
- Outline hug/tightness: `OUTLINE_ALPHA_THRESHOLD` / `CSC_ICON_OUTLINE_ALPHA_THRESHOLD`
  - Default threshold: `160`
  - Purpose: anchors the silhouette outline to the solid subject rather than rembg's low-alpha fringe.

Definition can come from Canny crease overlay and/or structural outlines:

- `CSC_ICON_CREASE_OPACITY`
- `CSC_ICON_CREASE_WIDTH`
- `CSC_ICON_CREASE_THRESHOLD`

## Color grading defaults

Color grading is enabled by default from the `Market_Output.xcf` reference effects:

- midtone color balance: green `+0.054`, blue `+0.015`
- saturation scale: `0.884`
- levels gamma: `0.79`
- color temperature: `6500K -> 6108.6K`

Useful knobs:

- `CSC_ICON_COLOR_BALANCE_MID_GREEN`
- `CSC_ICON_COLOR_BALANCE_MID_BLUE`
- `CSC_ICON_COLOR_SATURATION_SCALE`
- `CSC_ICON_COLOR_LEVELS_GAMMA`
- `CSC_ICON_COLOR_TEMP_ORIGINAL`
- `CSC_ICON_COLOR_TEMP_INTENDED`

## Related docs

- `COMFYUI-SETUP.md` — model/LoRA setup and prompt templates.
- `COMFYUI-MANUAL.md` — manual generation workflow.
- `icons-pipeline.md` — overall icon pipeline reference.
