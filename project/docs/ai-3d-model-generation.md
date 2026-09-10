# AI-Assisted 3D Model Generation

Use this when creating a new CSC prop or small building model from scratch. Stop here once the asset is an art-approved Blender source/working file. For game export, use [Export Pipeline Reference](export-pipeline.md).

## Scope

This document covers:

- concept/reference interpretation;
- blockout and Civ VI style decisions;
- AI-assisted base-color texture generation;
- Blender source/working-file hygiene before export cleanup.

It does not cover:

- CN6/FGX/GEO export;
- Asset Editor `.ast`/`.mat`/`.tex` wiring;
- XLP/ArtDef registration;
- ModBuddy cook and in-game testing.

## Quality Target

CSC assets should feel like plausible Firaxis-adjacent cut content: chunky, readable, stylized, and functional at Civ VI's camera distance. Prefer clarity over realism.

Use the nearby references:

- [BUILDING-SHAPES.md](BUILDING-SHAPES.md) for the marble rule, shape hierarchy, proportions, and exaggeration.
- [building-geometry-patterns.md](building-geometry-patterns.md) for vanilla Civ VI mesh patterns and budgets.
- [textures-and-uvs.md](textures-and-uvs.md) for UV/texture architecture.

## From-Scratch Workflow

1. Gather references.
   - Use the project concept image, nearby CSC assets, and one vanilla Civ VI analogue if available.
   - Identify the one or two silhouette features that must read at game scale.
   - Identify the **player-readable signal** of the prop: the part that should still communicate the object at Civ zoom. Make that signal large enough to survive thumbnail scale, even if it means simplifying real-world construction details.

2. Block out the model in Blender.
   - The vertex budget for small standalone props is a hard default target of **300 vertices or fewer**. Exceed it only for a named silhouette/readability reason, and record the final vertex/triangle count before considering the asset done.
   - If a prop cannot read near 300 vertices, simplify the design first: reduce repeated cords, weights, bevels, cylinders, and decorative pieces before accepting a higher-detail mesh.
   - Big shapes first, then intermediate shapes, then small detail.
   - Use independent low-poly pieces/cards where it helps; Civ VI buildings are not clean manifold sculptures.
   - Keep the object readable from the isometric game camera, not from a close beauty render.
   - Prioritize scale exaggeration over literal mechanics. If a historically accurate detail hides the prop's main read, enlarge the readable element and drop the fine detail.

3. Keep geometry economical.
   - For small standalone props, stay near the 300-vertex budget by default. A few hundred to low-thousands of triangles is an exception for high-importance props, not the normal target.
   - If the prop is spinning-wheel-class, use the existing Tailors' spinning wheel as scale reference: roughly 40 units long by 26+ units tall in final mesh data, object scale 1.0, transforms applied before export.
   - Model at any convenient size, then apply final scale to mesh data before AO baking.
   - **Mesh connectivity (welded vs. exploded) is not an export vertex-count lever — don't spend effort there.** CN6/FGX splits a vertex into per-face copies at every UV seam and every hard-normal edge, and the Civ chunky/toy style needs a seam or hard edge almost everywhere a surface changes direction (every wall/roof corner, every panel boundary, per-piece atlas placement). That means a welded, continuous mesh and a manually-exploded, fully-disconnected one usually export to close to the same vertex count — welding is a Blender-authoring convenience, not something that survives into the game data. **The real savings mechanism Firaxis uses is single-sided, non-watertight geometry**: no back faces on walls, no bottom caps, no interior volume, nothing modeled that the isometric camera can never see. If a prop's export footprint needs to shrink, strip camera-invisible geometry first (back faces, caps, solidify-modifier interiors) — that is where the actual vertex/face count lives, not in whether the mesh is joined or disconnected.

4. Generate or paint the `_B` base-color atlas.
   - Image generation is appropriate for the artistic `_B` map only.
   - Prompt for a flat texture atlas, not a 3D render. Ask for clean material regions: wood, textile, rope, clay, metal, etc.
   - Avoid labels, UV wireframes, shadows, logos, and text.
   - Generated `_B` atlases for props must use **continuous material swatches**, not pre-divided boards, planks, bricks, seams, outlines, or object-part shapes.
   - Wood texture should be one or more uninterrupted grain/material regions. Individual wooden pieces must be defined by model geometry and UV placement, not by painted separators in the atlas.
   - Reject or regenerate base maps that include board/plank separators unless that specific asset explicitly requires painted seams.

5. Derive companion maps deterministically.
   - Derive `_N`, `_G`, and `_M` from the final `_B` with `project/tools/blender/csc_generate_pbr_maps.mjs`.
   - Do not generate `_B`, `_N`, `_G`, and `_M` independently with image generation; even small pixel shifts will make atlas seams and material reads disagree.
   - Bake `_AO` from the actual geometry in Blender through UV2. AO is positional, not a painted-material property.

6. Assign UVs deliberately.
   - UV1 maps visible materials. Overlap/reuse material regions where appropriate.
   - For wood, inspect the generated atlas direction and rotate UVs so grain runs along each board, post, spoke, beam, or rim.
   - UV2 must be rebuilt as a non-overlapping pack before AO baking whenever UV1/geometry changes meaningfully.
   - UV3 is for tint/emissive use; leave it simple unless the asset needs it.

7. Preview and iterate.
   - Use temporary cameras/lights freely in the working file.
   - Check the asset at thumbnail scale, from the Civ-style camera angle.
   - Do a human visual check after every texture or UV rewrite. Do not rely only on node graphs, file paths, or generated-map statistics; confirm the visible material regions are on the intended mesh islands.
   - Verify the silhouette, material reads, and any interactive/detail props before export cleanup.

## Readability Examples

- Looms: the woven textile is the gameplay-readable signal. Prefer a large textile panel filling most of the frame over a literal arrangement with many thin warp cords and small hanging weights; those details disappear at Civ zoom and consume vertex budget.
- Repeated fine details such as cords, weights, pegs, carved marks, and small tools should be reduced to a few chunky shapes or texture detail unless they are the prop's main silhouette.

## Handoff To Export

Before switching to the export workflow, decide whether the file is still a working source or a final export scene.

The final export `.blend` must be cleaned to match [Export Pipeline Reference](export-pipeline.md):

- one armature;
- one joined mesh **object** (a single object in the outliner — internal geometry can and often should stay as many disconnected islands/quads; joining objects is an export-format requirement, not a signal to weld topology for vertex savings, see above);
- exactly three UV layers named `UV1`, `UV2`, `UV3`;
- all vertices assigned to the export bone;
- no cameras, lights, references, old iterations, or helper objects;
- external texture PNGs saved beside the asset, not silently packed as the only source of truth.

## Common Mistakes

- Making a beauty-render model instead of a game-scale prop.
- Treating the 300-vertex prop target as optional without recording why the asset needs more geometry.
- Preserving literal real-world construction when it makes the prop's main gameplay signal too small to read.
- Painting board separators into a generated atlas, then fighting accidental stripes in UVs.
- Accepting image-generated wood that is already split into boards or object parts instead of regenerating a continuous swatch atlas.
- Trusting that a material node graph is correct without visually checking that the model is sampling the intended atlas regions.
- Copying UV1 to UV2 and calling it AO-ready.
- Deriving AO from `_B`.
- Assuming a welded/manifold mesh exports with meaningfully more (or fewer) vertices than a manually-exploded one, or re-topologizing to "explode" a model hoping for export savings. The CN6 seam-split mechanic makes joined and exploded topology roughly equivalent in vertex count for chunky, hard-edged CSC geometry; the real savings come from removing camera-invisible geometry (back faces, caps, solidified interior volume), not from mesh connectivity.
- Generating separate normal/gloss/metalness images with imagegen.
- Leaving a Blender working file full of cameras, references, and helper objects and treating it as export-ready.
