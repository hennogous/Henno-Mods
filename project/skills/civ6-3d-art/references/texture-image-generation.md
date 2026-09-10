# Texture image generation directives

Use for base-color texture creation and edits, alongside the available image-generation
tool/skill. A concept illustration and a usable texture atlas are different outputs.
Do not send an isometric building prompt when the deliverable is a flat material sheet.

## Specify the texture before prompting

Establish the material set and its intended mesh assignments. Record atlas dimensions,
region coordinates, grain direction, visible feature size, palette, tiling requirements,
and which regions can be reused. Fit the project's material/atlas budget. A prototype's
dedicated atlas does not set the final district-wide texture architecture.

For an existing model, UV layout is a constraint. For a new model, layout and UVs can
be developed together. Distinguish a reusable material patch (wood, plaster) from a
facade-specific patch (window, door trim). Generate literal board divisions, windows
or structural objects only when the UV plan requires those features in that region.

Label every input image:

- **Edit target/layout authority:** the atlas whose region boundaries must survive.
- **Style reference:** Firaxis material treatment, not a layout to copy.
- **Concept/palette reference:** the building's materials and colors, not baked camera
  perspective or scene lighting.

Inspect local references before using them. Preserve the approved atlas as a versioned
source, and save generated outputs into the project rather than leaving them only in
a tool cache. Use the available image-generation tool for artistic creation/edits;
technical map derivation, measurement, packing and validation remain deterministic work.

## Global image directives

Request a flat, orthographic, edge-to-edge base-color texture sheet. No camera
perspective, 3D scene, decorative border, captions, watermark or unsolicited objects.
Use opaque RGB unless an actual opacity/alpha material is part of the brief.

Describe a restrained digitally painted game texture: broad calm faces, limited
purposeful color variation, abbreviated material marks, selective edge highlights
and soft crevice darkening. Specify exact positive material qualities rather than
relying on “hand-painted,” which can produce thick impasto and mottled surfaces.

Restrained painting does not require desaturating every material. The native campus
atlas combines quiet masonry with strong blue roof/banner accents. Reserve saturation
and contrast deliberately for identity and hierarchy, following the actual brief.

Suppress dramatic directional cast shadows, ambient studio gradients, glossy hotspots
and baked scene lighting. Retain restrained local painted definition when the reference
uses it. Do not demand completely unshaded color if that removes the reference's
stylized material read. Global contact shadows belong in geometry AO, not every swatch.

The inspected native Market is a useful calibration: its base color already depicts
window recesses, crate frames, plank edges and cloth folds; the normal map reinforces
those same features under lighting. Preserve that coordinated construction detail.
Do not make base color so flat that only the normal map explains the object. Broad
color regions can remain quiet while selected facade/prop patches carry strong local
depth cues. Judge base-only and normal-only previews as well as the combined material.

Keep texture detail subordinate to the roof/body/structural accents at game scale.
“More detailed” means more useful construction/material information, not uniform
high-frequency texture across all materials.

## Material-specific directives

| Material | Ask for | Reject or revise |
|---|---|---|
| Timber side grain | Calm warm/muted brown underpainting; a few irregular directional streaks, knots and abbreviated grooves; continuous patch along declared grain axis | Photographic hairline grain, equally dark stripes everywhere, painted board separators on continuous beam swatches |
| Timber end grain | Broad irregular rings and restrained radial cracks in a separate patch | End-grain rings on beam sides; dense concentric targets that dominate tiny props |
| Stonework | Readable courses, substantial block faces, modest block-to-block value shifts, narrow mortar, selective softened/chipped edges | Boulder-like bulging, extreme mottling, deep black grout outlining every stone |
| Plaster | Quiet cream/buff or brief-specific hue, broad subtle variation, sparse fine marks | Scratched rock, noisy speckle, deep cracks without a design reason |
| Terracotta tiles | Clear overlapping courses, broad tile faces, controlled lower lips, modest shape/color variation | Repeated white highlights, deep black scallops, dense chips or shiny plastic appearance |
| Thatch | Broad flowing clumps with readable bundles and a few directional straw marks | Equal-weight individual straws, photographic hay noise, geometry-like shadows unrelated to the roof |
| Cloth | Broad soft folds only where needed, subdued color, sparse weave suited to displayed scale | Coarse checker/weave that overwhelms a small banner; shadows implying folds the mesh cannot support |
| Forged iron | Dark muted gray/blue-gray, broad subtle variation, a few directional scuffs | Chrome gleam baked into the base; white glitter and heavy scratch noise |
| Coals/fire region | Dark coal masses with selective warm fissures, confined to the intended emissive patch | Entire patch uniformly glowing; painted fire outside assigned UV area |

These are starting tendencies. Era, material and the actual source reference can
justify different choices. Avoid turning the blacksmith's terracotta/oak palette
into the default for all civilizations and buildings.

## New-atlas prompt template

Replace braces with an actual brief; omit irrelevant clauses. This is a prompt
template, not a claim that the generator can enforce pixel coordinates perfectly.

```text
Use case: stylized-concept
Asset type: flat base-color UV atlas for a Civilization VI {building/prop}.
Output: {dimensions/aspect}, opaque, edge-to-edge texture sheet, no perspective.
Input roles: Image 1 is the approved palette/concept. Image 2 is a Firaxis
material-style reference only; do not copy its atlas layout or objects.

Layout, top-left image coordinates:
{each region: normalized or pixel bounds, material, grain direction,
 approximate number/scale of courses or other required features}

Painting: restrained digitally painted game materials, broad calm faces,
purposeful abbreviated marks, modest color variation, selective edge definition.
{Material-specific instructions from the table, tailored to this asset.}

Lighting: soft local material definition; no directional scene shadows,
studio lighting, baked glossy hotspots or vignette. Structural relief will
be authored in an aligned height/normal map.

Constraints: clean fixed region boundaries; preserve material identity and
orientation; no text, labels, framing or added objects. {Actual tiling/alpha needs.}
```

For surface patches intended to tile, request matching opposite edges and no obvious
isolated centerpiece, then inspect repeated copies. “Seamless” in the prompt is not
proof that the seams match. Do not require an entire multi-material atlas to tile.

## Editing an approved atlas

Use the existing atlas as the explicit edit target, not merely a style reference.
State each invariant on every edit. Prefer a narrow material or paint-treatment
change to repeated whole-atlas redesigns. Example:

```text
Use case: style-transfer
Image 1 is the EDIT TARGET and exact layout authority.
Image 2 is a Firaxis STYLE REFERENCE only.

Change only {roof material treatment}: soften the repeated bright tile lips
and dark scalloped seams; keep broad muted terracotta faces and readable
overlapping courses. Preserve the existing tile positions and sizes.

Keep every atlas boundary, material region, grain direction, color family
and all other swatches unchanged. No new objects or labels. Flat base-color
texture sheet; no 3D view, lighting setup, vignette or border.
```

If repeated atlas edits drift boundaries, use a more controlled region edit workflow
supported by the available image tool, or generate separate material patches and
pack them deterministically into specified rectangles. Do not silently warp existing
UVs after every generation. Check borders/padding and rebake/rederive affected data
when a layout change is intentional. This separate-patch option is a fallback to
test, not a method already validated by the blacksmith experiment.

## Acceptance checks before Blender reload

1. Verify actual output dimensions, image mode/alpha and saved project path. Requested
   dimensions are not proof of returned dimensions.
2. Inspect region boundaries against the intended UV rectangles. Check for leaked
   materials, white borders, unexpected objects and encroaching swatches.
3. Verify grain orientation and material identity; view the actual mapped model too.
4. Check course/tile size on the model against its scale and nearby references.
5. Inspect a reduced-size view. Repeated bright edges and fine noise should not
   overpower the building's main material/color masses.
6. For reusable atlas patches, check inset/padding and lower-resolution filtering
   for neighboring-material bleed. For tiling patches, inspect repeated edges.
7. Preserve the previous approved version until the replacement passes. Record the
   prompt and which references/settings produced the accepted result.

Use the normal automatic mip-generation workflow. If distant textures blur, shimmer
or bleed between atlas regions, inspect filtering, generated mips and padding as part
of diagnosing that problem. Custom mip authoring is not part of the default workflow.

Reject before investing in detailed maps when the atlas layout is unusable or the
painting is fundamentally wrong. A stronger normal map will not repair either.

## From base color to technical maps

Choose structural heights from the aligned features: tile lips, mortar and block
bevels, selected grain and shallow folds. Do not globally equate brightness with
height. Independent image-generated N/G/M/AO maps can shift features and are not
an acceptable default pipeline. Semantic masks/regions define material properties;
geometry and UV2 determine AO. Keep a reusable H source for art-directed relief.

Read supplied `.mtl` bindings and `.tex`/DDS formats instead of guessing from suffixes.
The native Market binds `_A` as AO; its A/G/M maps are R8 data, B/N are RGBA8 at
1024 square, and E is RGBA8 at 512 square. Decode scalar red-channel data explicitly;
some image readers expose R8 as red RGB, whose luminance would change the values.
These are observed source/export formats, not a universal runtime texture prescription.

Do not generate a full set of maps merely because a material exists. The supplied
Foundation_Modern_01 binds B/N/G but leaves AO, metalness, opacity and emissive empty.
Keep atlas coverage/bake validation separate for each bound material domain. For
family AO atlases, reserve distinct padded regions for model/state-specific bakes;
overlapping material UVs do not imply overlapping AO. Shared-bake exceptions need
an explicit visual/occlusion justification rather than a UV1-only correspondence.

For the CSC helper, use `--height`, `--regions`, `--reference-size` and an explicit
`--normal-y` as documented in the project's texture reference. These are tool options,
not image-generation prompt fields. Do not use image generation to draw RGB normal
colors. Verify normals on a neutral material and verify the destination tangent
convention. Use the intended shader and game lighting for final material judgment.
