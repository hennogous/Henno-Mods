# Asset Editor IronPython Automation

> **Documentation audit — 2026-09-12: Provisional.** Correctly distinguishes static discovery from a pending live Asset Editor test. CSC_DumpPreviewerKnobs.py exists. Keep as research; it does not establish a working automated AE workflow.
> Classification: Tool investigation. See the [full audit](../../DOCUMENT-AUDIT.md).

Status: investigation note. Static analysis is confirmed against the local SDK scripts; live Asset Editor behavior still needs one manual validation pass.

## What Works

Civilization VI's Asset Editor has a real IronPython scripting surface. The local SDK includes scripts under:

`C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\AssetEditor\Scripts`

Useful shipped examples:

- `Preview_Unit.py` uses `previewSetService.GetPreviewSetData()` and `previewSetService.LoadPreviewSet(...)`.
- `Load_Test_Save.py` uses Asset Editor services plus FireTuner commands.
- `Create_Assets_From_Source_File.py`, `Assign_Geo_To_MultipleAssets.py`, and related scripts show normal asset/project API use.

The Discord `LeaderCapture.py` script goes deeper than the shipped examples by reaching into private previewer service fields:

```python
_ps = previewSetService._PreviewSetCommands__PreviewSetService
_eks = _ps._PreviewerKnobService__EntityKnobSet
knobs = {k.Name: k for k in _eks.Knobs}
```

From there it can call the previewer's `captureScreenshot` knob, set animation state knobs such as `m_sFromState` and `m_sToState`, enable time scrubbing, set `m_fCurrentTime`, and invoke playback.

## CSC Use Cases

The most useful CSC workflow is not leader animation capture. It is repeatable transparent preview capture from Asset Editor for Quarter art.

Good candidates:

- create source/reference images for `project/tools/comfyui/sv_pipeline/sv_img2img.py`;
- capture consistent 3D previews of kit buildings, roof recolors, and Quarter variants;
- make art QA contact sheets for state variants before cooking or in-game checks;
- compare Asset Editor material/texture assignments against expected Quarter palette;
- eventually batch-capture Worked/Unworked/Construction/Pillaged asset states if the relevant preview knobs are exposed for TileBase assets.

This can reduce manual screenshot drift. It also uses the official renderer and materials, which can be more representative than Blender renders once `.ast`, `.mat`, `.tex`, and `.geo` wiring exists.

## Limits And Risks

- This is not headless. It runs inside the Asset Editor IronPython console or script menu.
- The Discord script uses private .NET fields. It may break if Firaxis changes internal names, though that is unlikely for Civ VI's SDK at this stage.
- `captureScreenshot` still opens a Save As dialog. The script bypasses it with Windows UI Automation, which depends on the dialog title and control names.
- Knob names are asset/previewer-specific. Leader/unit animation knobs may not exist for static TileBase assets.
- It should be treated as a capture/QA helper, not as the source of truth for asset registration, ArtDefs, XLPs, or cooking.

## Validation Pass

1. Copy `project/tools/asset_editor/CSC_DumpPreviewerKnobs.py` into the SDK Asset Editor `Scripts` folder.
2. Open Asset Editor and load a CSC TileBase asset, such as a Bakers or Tailors building/district asset.
3. Run the script from Asset Editor.
4. Check the Asset Editor output pane for available knob names.
5. Confirm whether `captureScreenshot` exists for TileBase previews.
6. If it exists, adapt the Discord `capture_to_path(...)` helper and capture one PNG/TGA to a controlled folder.
7. Inspect whether the output has useful alpha and camera framing.
8. Feed the image into `sv_img2img.py` and compare against the current Blender/manual screenshot route.

## Quarter Playbook Hook

Add this to art-sensitive Quarter slices once validated:

- after an asset's `.ast`, `.mat`, `.tex`, `.geo`, XLP, and ArtDef wiring exists, capture an Asset Editor preview image;
- save it beside the working art source, not inside cooked output folders;
- use it as the source image for strategic-view sprite generation or as an art QA reference;
- record the exact asset name, state, and capture script version in the slice notes.

For Tailors, this is most relevant after the first real Tailors kit asset is viewable in Asset Editor. It is not a blocker for the current district-slice placeholder scaffolding.
