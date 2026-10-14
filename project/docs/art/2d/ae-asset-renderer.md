# Saved AE asset to standardized Blender render

`project/tools/blender/render_ae_asset.py` reconstructs the saved AST's Worked
geometry groups, material/texture overrides and recursive attachment transforms.
Save changes in AE before running. [AE owns placement](../ae-owned-assembly-workflow.md).

From the Henno Mods repository root on Shadow:

```powershell
py -3 project/tools/blender/render_ae_asset.py "Civ Supply Chains/Assets/CSC_TAILORS_Textile_Workshop.ast"
```

Only the AST argument is required. Final PNGs are saved **beside the input AST**:
`<asset>_Icon_Input.png` and `<asset>_SV_Input.png`. These stable filenames are
updated on each run, including when reusing a cached render. For example,
Tailor renders save `CSC_TAILORS_Tailor_Icon_Input.png` and
`CSC_TAILORS_Tailor_SV_Input.png` in `Civ Supply Chains/Assets/`.

Packed blends, geometry/ID passes and conversion evidence stay beneath
`Desktop/Codex/asset-renders/<asset>/<content-and-settings-hash>/`. Successful
exact outputs are reused after hash validation; consumed source/tool/settings
changes create a new run. Native extraction is cached by FGX and extractor
hashes. The extractor compiles automatically using the installed .NET compiler
and repo Firaxis libraries. No open Blender, screenshot, ComfyUI or model call
is needed. Python uses only the standard library; the Blender worker targets
the installed Blender 5.1 API.

Options: `--mode icon|sv|both`, `--icon-texture light|runtime`, `--resolution 256`,
`--samples 8`, `--force` (repeat), `--prepare-only` (resolve/extract without render).
`--image-output-dir` overrides the final PNG folder. `--output` overrides the
render package/cache root; that supporting package is kept outside the source
mod/SDK. `--mod-root`, `--sdk` and `--blender` override source/tool paths.

## Fixed presets

| Setting | Icon | Strategic View |
|---|---|---|
| Camera | Perspective, 37 mm, 23° elevation | Orthographic, 39.3517526° elevation |
| Apparent turn | 0° | 0° |
| Framing | Distance = 1.5 × visible span | Ortho scale = 1.70 × visible span |
| Sun direction | `(-240,-280,360)` | `(-300,-280,500)` |
| Sun energy / angular size | 3 / 8° | 3 / 8° |
| World RGB / strength | `(1,1,0.9)` / 0.8 | `(0.7,0.8,1)` / 0.65 |
| Transform / exposure / gamma | Standard / 0 / 1 | AgX / +0.35 / 1 |
| Building texture | Matching light-roof `_2` atlas | Saved runtime atlas |

These follow the skill's icon AE-reference preset and production SV preset,
rather than exploratory SV camera trials. Both exclude ground/decal context and
bisect the main building at world Z=0 in the snapshot. Placements stay unchanged.
AO Multiply Fac is 0.5. Normal maps use the established Blender preview convention,
with no speculative green inversion. Gloss previews as inverse roughness;
metalness and opacity are connected. Single-UV native AO
previews use UV1 and are reported.

**Henno, 13 October 2026:** omit emissive image textures entirely from icon/SV
render materials, with emission strength zero. This applies to the building and
all props; runtime material/texture bindings in AE remain unchanged.

Scalar AO/gloss/metalness/opacity maps explicitly read the red channel. Firaxis
R8 DDS maps may decode as red-only RGB; averaging RGB makes opaque surfaces
transparent and tints AO. Packed-channel alpha prevents base-color RGB loss.

Defaults: 1024² RGBA, Cycles CPU, four threads, 32 samples, seed 0, fixed sampling,
OpenImageDenoise. No adaptive sampling/animated seeds. Reproducibility is scoped
to the same Blender build/environment, not cross-version/hardware pixel identity.
Volatile PNG timestamps/path stamps are removed without touching pixel or color
profile chunks, allowing exact image/mask hashes on repeated runs.

## Outputs

Each `icon/` and `sv/` folder contains:

- `<asset>_Input.png`: transparent image for the existing painting pipeline.
- `<asset>_<mode>.blend`: portable packed-texture render snapshot.
- `Geometry.exr`: 32-bit multilayer Combined, world Normal, Depth and Object Index.
- `ObjectIndex.png`: raw 16-bit grayscale IDs; pixel integer = object's pass index,
  background = 0. Labels are not antialiased.
- `objects.json`: IDs mapped to AE placement/mesh groups, source matrices, camera
  and lighting. Select meaningful masses for outlining; do not outline every detail.

The root retains resolved `job.json`, source/output hashes in `manifest.json`,
`render-report.json`, Blender log, extracted JSON and texture PNGs. Masks must
match their mode and fingerprint. An AE placement edit invalidates old image-space
outlines. Assembly selection is the input AST; the icon roof swap does not select
alternate props.

The runner refuses missing/ambiguous sources, cycles, missing owners/bones,
invalid state/group bindings and conversion failures. XLP entry mapping is honored,
including base/DLC XLPs sharing filenames. It checks for mid-run source edits.
Source AST/GEO/FGX/MTL/TEX/DDS/XLP files are never modified.

## Limits and test target

This is a flat-ground static Worked/bind-pose reconstruction. It reads native
bone anchors, but does not evaluate animation clips, slopes, snow/burn/FOW or
all Firaxis shader features. Animations and unsupported channels are reported.
Compound X/Y/Z attachment rotations invert the CSC export convention; AE visual
calibration remains pending. Blender shading is an approximation of AE/game shading.

First target: `CSC_TAILORS_Textile_Workshop.ast`, with 20 saved attachments and
24 visible mesh-group objects (four root groups plus 20 props). Hidden state
geometry and decals are excluded from both intact inputs. Downstream painted
icon/SV generation and runtime acceptance are separate.

Verified on 13 October 2026, Blender 5.1.2: both 1024px inputs and both ID masks
are byte-identical across repeated rendering after volatile metadata removal.
Reopened snapshots retain all 20 AE placements and packed textures; maximum
attachment translation residual is 0.000013 source units (float precision).
Ten resolver/PNG regression tests pass. Cached reruns complete without rendering.
Final reviewed package on Shadow:
`Desktop/Codex/asset-renders/CSC_TAILORS_Textile_Workshop/ca2725004affa958/`.

Henno accepted the view and requested removal of emissive textures. The updated
icon/SV package is `Desktop/Codex/asset-renders/CSC_TAILORS_Textile_Workshop/44cb654393389185/`;
both saved snapshots omit emissive image nodes and use zero emission.
