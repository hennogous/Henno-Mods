# Blacksmith v5 — painted color and authored relief

This refinement keeps the approved v4 chunky geometry and changes the material
treatment after studying Henno's Firaxis watermill and commercial texture samples.
The new base atlas uses calmer wood and plaster, clearer stone courses, and more
restrained wear. An aligned editable height map supplies tile lips, stone bevels
and selected grain grooves. Color differences between stones no longer imply
different heights, and plaster is almost flat.

## Open and review

- `CSC_BLACKSMITH_Workshop_v5.blend`: textured scene with preview studio and camera.
- `CSC_BLACKSMITH_Workshop_v5_export.blend`: mesh and armature only.
- `CSC_BLACKSMITH_Workshop_v5.cn6`: selected mesh/armature export.
- `Textures/`: external B, N, G, M, E and AO PNGs, plus authoring-only H. Keep this
  directory beside either blend file.
- `blacksmith-render-v5.png`: final render with the same camera, lights and exposure
  as v4; `texture-comparison-v4-v5.png` places them side by side.
- `relief-comparison.png`: neutral gray material, normals off/on under identical
  lighting. This isolates actual map relief from painted shading.

**1,491 exported vertices, 781 triangles, one material, three UV channels.** The
CN6 vertex and triangle sections are identical to v4, including all UV values.
UV2 and geometry are unchanged, so the existing Cycles geometry AO bake is reused
byte for byte. Normal strength in the Blender shader is now 1.0, previously 0.65.

The preview N uses the OpenGL tangent convention. The generator exposes DirectX
as well; validate the destination material/cook convention during Windows handoff.
This package has not been converted to FGX or tested in the game.

## Reproduce the texture maps

From the repository root, using Python with Pillow/NumPy and Node with Sharp:

```sh
python output/blacksmith-v5/author_relief.py
node project/tools/blender/csc_generate_pbr_maps.mjs \
  --base output/blacksmith-v5/Textures/CSC_BLACKSMITH_Workshop_B.png \
  --height output/blacksmith-v5/Textures/CSC_BLACKSMITH_Workshop_H.png \
  --regions output/blacksmith-v5/material-regions.json \
  --normal-strength 4 --reference-size 1024 --normal-y opengl --overwrite
```

The base color was edited with image generation using the previous atlas as the
layout target and Firaxis textures as style references. `author_relief.py` selects
the inspected seam colors, closes small mask holes, constructs distance bevels,
and adds selected grain detail. These thresholds are specific to this atlas;
review them after any base-color repaint. Edit `_H` directly for more precise art
direction. This is an approximation of designed relief, not a recovered high-poly
sculpt or a claim to reproduce Firaxis's original authoring process.

`apply_textures.py` starts from the sibling v4 blend. `validate_and_review.py`
reopens v5, checks external image paths/color spaces and geometry, renders the
normal comparison, and saves the separate clean export blend. The v4 primitive
source remains in `../blacksmith-v4/CSC_BLACKSMITH_Workshop_v4_source.blend`.

Generator tests: `node --test project/tools/blender/csc_generate_pbr_maps.test.mjs`.
See `validation.json`, `budget.json` and `normal-diagnostics.json` for checks.
The normal statistics describe surface slopes across different atlases; they are
not a quality score or an exact match target.
