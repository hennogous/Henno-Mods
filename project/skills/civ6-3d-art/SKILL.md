---
name: civ6-3d-art
description: Build and refine Civilization VI buildings and static props in Blender from concepts, using economical geometry, painterly atlases, and verified export budgets. Use for Civ VI 3D asset creation and visual review; use the project's modding workflow for gameplay and art registration.
---

# Civ VI 3D Art

Create assets that read beside Civ VI buildings at gameplay scale. Prefer deliberate
low-complexity construction from primitives and custom face patches for architecture.
Use generated high-poly assets selectively as references or baking sources when they
save total work. A successful blacksmith is evidence for this approach, not proof
that it works equally well for characters, creatures or every architectural style.

This is an initial working skill. Distinguish measured behavior, visual judgments,
and untested hypotheses. Improve it through actual asset trials.

## Establish the asset brief

Read the active project's instructions and relevant art/export docs. Reuse its
asset identifiers, dimensions, attachment conventions and exporter. For CSC, use
the `civ-supply-chains` and `civ6-modding` context already available; otherwise locate
equivalent project references. Do not assume a remembered host path.

Capture the building's gameplay role, era/culture, footprint, reference scale,
approved concept, distinguishing silhouette, material family, exported vertex and
triangle budgets, material/texture budget, and required states. Infer routine
choices from the task. Ask only about missing decisions that materially affect it.
The blacksmith's 1,500-vertex ceiling is an example budget, not a universal Civ VI limit.

**Optimize total rendering cost, not the smallest vertex number.** For these small
building assets, prioritize avoiding unnecessary concurrent materials/render groups,
texture sets and expensive transparency, and preserve useful resource reuse. Treat
registered asset count as a separate compatibility/capacity constraint. Respect an
explicit vertex budget, but spend available vertices on readable silhouettes and
structural depth rather than sacrificing them for marginal count reductions. These
are working priorities; change them when measurements identify another bottleneck.

For budget decisions, read [Performance and resource budgets](references/performance.md).
The ordering above is preventive design guidance, not a measured Civ VI bottleneck
ranking. Inspect the actual workload before spending effort on further optimization.

## Make the silhouette work first

Read [Art direction](references/art-direction.md) for concept design, shape hierarchy
and painterly material decisions. Decompose the concept into major masses, structural
accents and surface detail. Translate the concept into a buildable design; a single
image does not define unseen sides or dimensions.

Build a gray blockout before detailed textures. Judge the intended game view and
other relevant rotations, with a reference building or known dimensions for scale.
Spend geometry on silhouette, meaningful depth and openings. Give beams real width
across their slope; do not substitute texture contrast for structural thickness.
Keep the source editable with named parts and parameters for meaningful dimensions.

Use review checkpoints appropriate to the user's request: concept, gray model and
in-game result. Existing approval remains valid. Do not require a fresh permission
exchange for each ordinary modeling step.

## Construct and count the actual deliverable

Read [Geometry and export](references/geometry-and-export.md) before finalizing
topology or UVs. Maintain an editable source and a separate export-prepared mesh.
Count evaluated geometry, actual exported vertices and triangles, and material
groups. Report the reason for expansion; never report the source count as the
runtime count. Equality with Asset Editor is verified only after conversion and
inspection of the same asset/version and mesh scope on the destination toolchain.

For the project's static-building workflow, preserve exactly UV1, UV2, UV3 in order:
material atlas, AO, emissive. Validate each mapping against the material that samples
it. AO-baked surfaces need an intentional allocation independent of UV1 reuse; an
unbound AO/emissive map does not require a bake. Inspect tangents and shading as well
as counts. A low count with damaged normals is not a passing export.

## Make and validate materials

Read [Texture image generation](references/texture-image-generation.md) before
generating or editing an atlas. It contains material directives, prompt templates,
layout-preservation rules and rejection criteria; do not rely on “Civ VI style” alone.

Generate or paint base color with actual Firaxis visual references when available.
Preserve atlas region boundaries and confirm them visually before mapping. Derive
companion maps from aligned authoring data: explicit structural height where useful,
semantic gloss/metalness, and geometry-baked AO through UV2. Never independently
generate a normal picture and assume registration with the base.

Keep grain along each beam, timber end grain on real cut ends, and courses/tiles at
a deliberate size. Keep active PNGs external beside the blend. Reload replaced
images. Use Non-Color for N/G/M/AO, sRGB for B/E, and the correct tangent convention
for the current renderer. Do not infer normal green-channel orientation just from
the game using DirectX. Verify the conversion/material chain with a known relief.

Review textured and neutral-material normals-off/on renders under identical light,
then at intended gameplay size. Reuse AO if geometry and UV2 are unchanged; rebake
when geometry/occlusion or its mapping changes. Shared AO packing and atlas policy
are project decisions; do not lock a whole project into one atlas per prototype.

## Handoff and learning

Provide source blend/build script, a clean export scene, external textures, actual
export, count/material report, and review images. Keep preview cameras/lights out
of the clean export. Reopen the saved files and check paths and texture spaces.
State exactly which stages were verified: Blender, CN6, converted FGX/Asset Editor,
in game. A screenshot supports visual assessment, not exact vertex-count parity.

If the request includes implementation, pass the validated asset and its manifest
to the existing project workflow for materials, textures, AST/GEO, ArtDefs, XLPs,
ModBuddy registration and gameplay. Keep that orchestration separate from modeling
rules, and preserve the user's authorization boundaries across machines.

Read [Trials and reference intake](references/trials.md) when developing the skill,
incorporating new resources or assessing a candidate tool. Promote only demonstrated
lessons; keep asset-specific tuning out of universal instructions.
