# Saved AE asset to standardized Blender render

`project/tools/blender/render_ae_asset.py` reconstructs the saved AST's Worked
geometry groups, material/texture overrides and recursive attachment transforms.
Save changes in AE before running. [AE owns placement](../ae-owned-assembly-workflow.md).

From the Henno Mods repository root on Shadow:

```powershell
py -3 project/tools/blender/render_ae_asset.py "Civ Supply Chains/Assets/CSC_TAILORS_Textile_Workshop.ast" --L1
```

Supply the AST and one framing flag: **`--L1`, `--L2`, or `--L3`**. These refer
to building levels, not supply-chain stages: Stage 2 → L1, Stage 3 → L2,
Stage 4 → L3. Workshop uses `--L1`, Tailor `--L2`, Fashion House `--L3`.
`--auto-frame` explicitly selects the older prop-bounds framing; it is unsuitable
for reusable main-building XCF paths. The framing flags are mutually exclusive.

Final PNGs are saved **beside the input AST**:
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

**Camera registration override, Henno, 14 October 2026:** prop bounds must not
affect the camera, target, perspective distance, lens or orthographic scale.
Frozen absolute camera matrices and scales live in
`project/tools/blender/ae_render_camera_presets.json`. L1 preserves the accepted
Workshop camera; L2 preserves the saved Tailor camera. L3 uses the Level 3
starter's authored location with a fixed 25% framing reserve. These values are
read as constants, never recalibrated from the input AST or updated starter.
The file participates in render cache invalidation. Explicitly revising its
values is a one-time registration change requiring matching XCF path alignment.

**L1 icon calibration, 14 October 2026:** match Henno's centred resize from
1024 to 1050 px and 35 px upward placement. The L1 icon lens is now
37.939453125 mm (`37 × 1050/1024`) with vertical camera shift -0.0341796875
(`-35/1024`). Camera pose, elevation and perspective stay unchanged; projected
landmarks follow the same centred 1.025390625× enlargement and upward shift.
The render remains 1024². At other resolutions the proportional offset scales
with the canvas. This calibration applies to the L1 icon; the SV profile retains
its separate registration.

**L2/L3 icon calibration, 14 October 2026:** L2 moves up 47 px on the
1024px canvas (shift Y=-0.0458984375). L3 moves right 41 px and up 71 px
(shift X=-0.0400390625, Y=-0.0693359375). Their camera poses, 37 mm lenses
and perspective remain fixed; these are translations only. Both SV profiles
retain their separate registration.

Use the same level, mode and canvas resolution to reuse paths. Registration
remains exact while prop copies/placements/sizes change, provided the main
building geometry and its world placement remain unchanged. Assemblies outside
the fixed frame are recorded in `objects.json` rather than automatically
reframed. No geometry is recentered. The prior bounds-based framing below is
used only by `--auto-frame` or as historical calibration provenance.

| Setting | Icon | Strategic View |
|---|---|---|
| Camera | Perspective, 23°; L1 37.939453125 mm, L2/L3 37 mm | Orthographic, 39.3517526° elevation |
| Apparent turn | 0° | 0° |
| Framing | Frozen per-level camera matrix / lens / film shift | Frozen per-level camera matrix / ortho scale |
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

## Fixed-camera verification — 14 October 2026

`project/tools/blender/test_ae_fixed_camera_registration.py` exercises the actual
Blender setup for six locked class/mode combinations. Moving and enlarging a
prop and adding another far-away prop changes assembly bounds while preserving
camera/framing values and all eight main-building landmark projections exactly.
Two explicit automatic-framing controls correctly change registration. Run it
in background Blender with `--python-exit-code 1`; it writes no render or asset.
Additional icon checks verify L1's 1050/1024 centred zoom and 35-pixel upward
shift, L2's 47-pixel upward shift, and L3's X +41 / Y -71 shift against eight
projected landmarks each. Maximum error is below 0.0001 px.

Workshop L1 and Tailor L2 full-size renders and a Fashion House L3 preview were
visually checked. The current Workshop rock and Tailor tree/shrub can extend
outside fixed frames; those placements are retained and reported, not moved.
The read-only native extractor now handles active model InitialPlacement
scale/shear: the installed managed getter reads offset +16 instead of +32.
The corrected native read guards flags/position and preserves scale metadata;
it does not apply Maya authoring placement to runtime geometry.
