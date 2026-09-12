# Blacksmith skill trial 01 — fresh build

> **Documentation audit — 2026-09-12: Historical.** September 11 experiment with explicit scope and outputs. Preserved as trial provenance; not the default plan for every CSC building and not proof the trial delivered or passed runtime checks.
> Classification: Trial brief. See the [full audit](../../DOCUMENT-AUDIT.md).

Prepared for Henno, 11 September 2026. This is a production trial of the current
`civ6-art` skill in a fresh task, without relying on the research conversation.

## Objective and scope

Build a new Civ VI blacksmith workshop from the original approved concept, using
economical, editable geometry and newly authored textures. Improve its fit beside
native buildings at gameplay scale within comparable resources to the previous
blacksmith. Preserve the earlier versions as the benchmark.

Produce the intact, static building, its visible work-area props, textures and CN6
handoff. Construction/pillaged states, gameplay implementation, art registration,
publishing and additional tool purchases are outside this trial. Continue through
modeling, texturing, baking, export and review without routine approval pauses.
Henno's earlier concept approval remains valid. This commission authorizes automated
modeling and texture creation despite older project notes calling them human-only.

## Read and use

Repository: the active Henno Mods checkout. Document/tool paths below are relative to its root; the art skill is installed separately.

1. Read applicable `AGENTS.md` and `CLAUDE.md`, then use the `civ6-art` skill at
   the installed `civ6-art` skill (`hennogous/civ6-art`, `SKILL.md`) and its relevant
   references, especially texture image generation and geometry/export. Load project
   modding context where needed for export conventions.
2. Read `project/docs/research/art/firaxis-guidance-review.md` for the latest evidence boundaries.
   Use `project/docs/research/art/firaxis-market-study.md` for a compact native building reference.
   Other studies are supporting evidence, not mandatory background reading.
3. Inspect the concept and visual references below. Do not substitute file names or
   text descriptions for actually viewing the images.

Use the skill as it stands. Record missing or misleading guidance in the trial
report; avoid rewriting the skill during the build. Judgment and iteration are
expected, but document consequential decisions the skill did not help resolve.

## Paths and reference roles

All paths in the table are relative to this existing **art root**:

`/Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/Dropzone/Codex`

| Reference | Path under art root | Purpose |
|---|---|---|
| Approved concept | `imagegen/blacksmith-concept-v1.png` | Primary architectural and proportion target; reuse it rather than generating a different design |
| Previous textured model | `blacksmith-v5/CSC_BLACKSMITH_Workshop_v5.blend` | Measure footprint, orientation and scale; compare final appearance |
| Previous clean export | `blacksmith-v5/CSC_BLACKSMITH_Workshop_v5_export.blend` | Inspect existing export setup without overwriting it |
| Previous CN6 and counts | `blacksmith-v5/CSC_BLACKSMITH_Workshop_v5.cn6`, `blacksmith-v5/budget.json` | Measured baseline |
| Previous appearance | `blacksmith-v5/blacksmith-render-v5.png`, `blacksmith-v5/blacksmith-thumbnail-v5.png` | Visual benchmark |
| In-game baseline | `blacksmith-skill-trial-01/references/in-game-baseline.png` | User-supplied neighborhood screenshot; blacksmith is the red-roof workshop in the lower central/right area |
| Native material examples | `research/market-study/texture-sheet.png`, `research/market-study/B.png`, `research/market-study/N.png` | Actual Firaxis texture character and construction relief |
| Native preview comparison | `research/market-study/market-comparison.png`, `research/market-study/Market-material-study.blend` | Qualitative material/construction comparison, not verified game shader parity |

Output directory: `blacksmith-skill-trial-01/` under the art root. Keep its `references/`
intact. Use fresh trial filenames and never overwrite v1–v5. Earlier scripts may
contain obsolete `output/` paths: inspect and adapt rather than running blindly.
Existing exporter and utility code can be reused; build new geometry and a new atlas
rather than modifying the v5 mesh or treating its layout as mandatory.

## Art brief

A compact preindustrial timber-and-plaster blacksmith: a tall, swept terracotta
gable roof; substantial dark roof-edge timbers and posts; a prominent tapered stone
chimney; and a lower open-sided work shelter with a forge and readable anvil.
Warm plaster, orange/red clay, dark timber, gray stone and restrained iron accents.
The building should communicate its trade without requiring a large fire effect
or close-up inspection. Infer coherent rear and side construction from the concept.

Preserve the concept's mass relationships and useful negative space. The important
improvement over the first attempt is structural weight: particularly the front
sloping bargeboard, eaves, posts and chimney. Bargeboard width must read across the
roof slope, not merely as a vertical offset. Deliberate curves and taper should
support construction rather than make every component randomly crooked.

Aim for convincing architecture and material detail, selectively exaggerated for
the game camera. “High fidelity first” is a community interpretation and a quality
check, not an instruction to start high-poly. The 3:2:1 shape guidance concerns visual
hierarchy, not a literal allocation of polygons. Keep major/intermediate forms clear
in a gray model; fine marks must support them. Simplify minor tools and accessories
where they contribute little at gameplay size.

For textures, follow the skill's full generation directives. Seek controlled,
material-specific detail: tile lips and courses, masonry joints and bevels, directional
timber grain, quieter plaster, selected wear and modest painted local depth. Avoid
uniform noisy grunge, smeared brushwork or equally sharp detail everywhere. Base color
must remain readable without normals; aligned normal relief should add construction
definition without making every color variation a bump. Keep the concept's studio
lighting out of the atlas. Save the generation prompts and authoring inputs.

## Resource and export contract

- Target **at most 1,500 actual exported vertices**, including building and props,
  and **one material/render group** for the intact asset. Previous CN6: 1,491 vertices,
  781 triangles, one material. Do not force the new topology to match those exact counts;
  report triangles as well as vertices and explain material departures before expanding scope.
- Start with one 1024×1024 material atlas and maps no larger than 1024×1024, comparable
  to the baseline. Smaller companion maps are fine. Report each map's dimensions.
- Preserve the baseline's placement scale, footprint and orientation after measuring
  it. Use a new trial identifier so the handoff cannot silently replace a live asset.
- Keep editable source parts plus a separate export-prepared mesh. Spend geometry on
  silhouette, depth and useful openings; detached face patches are a technique, not
  a requirement to disconnect everything. Check seams, normals and tangents after export.
- Exactly three ordered UV sets for this project: UV1 material atlas, UV2 baked AO,
  UV3 emissive. Bake AO for the new geometry; the old bake cannot simply be carried over.
  Document intended bindings. Asset-level AO can override material AO; the native
  studies' UV footprints do not establish final AO texture assignments without ASTs.
- Deliver B/N/G/M/AO and E if the forge uses it; keep authoring height/masks distinct
  from runtime maps. Verify color spaces and normal convention rather than guessing
  from DirectX terminology. Use ordinary mip generation; custom MIP experiments are
  outside this trial.
- Source, evaluated/export-prepared and parsed CN6 counts must be reported separately.
  Henno confirmed the earlier blacksmith's 1,491 vertices in Asset Editor. That is the
  benchmark, not validation of this new export. Never claim new FGX/Asset Editor or
  in-game verification unless those stages were actually completed on this version.

## Work sequence and acceptance

1. Inspect references, measure the old asset and state a concise construction plan.
   Preserve the approved concept; no new concept-generation round is required.
2. Build and review a fresh gray model from the game camera and relevant rotations.
   Correct massing and structural thickness before detailed texture work.
3. Author the atlas and aligned companion maps, bake AO, then review materials under
   consistent light. Use image generation for painted base color where useful, following
   the image-generation skill as well as the Civ VI texture directives.
4. Export and parse the actual CN6; resolve avoidable expansion and shading faults.
   Reopen the saved source/export blends and verify external texture paths.
5. Compare old/new models at the same scale, camera, exposure and lighting, plus small
   game-like views. Include neutral-material normal-off/on comparisons. Native Blender
   references are approximate; a composited screenshot is a mockup, not an in-game test.

Deliver editable `.blend` and reproducible build script, clean export `.blend`, `.cn6`,
external textures with portable relative paths, generation/height authoring inputs,
count/material/texture report, and review images. Keep cameras and lights out of the
clean export. If Windows conversion or the game is unavailable, complete the local
package and provide a short destination checklist; mark those checks pending.

In `trial-report.md`, assess role recognition, concept fidelity, shape hierarchy,
construction/material definition, gameplay readability and technical correctness.
Use concrete observations with images rather than invented numerical art scores.
Record elapsed work, meaningful revisions, human interventions, skill gaps and
remaining uncertainty. A successful outcome is a more convincing usable asset at
comparable cost; a polished close-up alone is insufficient.
