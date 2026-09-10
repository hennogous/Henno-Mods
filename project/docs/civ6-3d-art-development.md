# Developing a repeatable Civ VI 3D art workflow

Native reference calibration: [Firaxis Market study](firaxis-market-study.md), including
controlled material previews, corrected UV coverage and custom-normal measurements.
The [Library study](firaxis-library-study.md) adds two groups within one mesh, curved
shading and material-specific UV coverage. Its rare explicit mipmap variants remain
an isolated research observation, not a production workflow recommendation.
The [campus family comparison](firaxis-campus-family-study.md) verifies shared UV1
artwork alongside disjoint AO regions across Library states and University.

Working proposal and learning record, 2026-09-10. Owner: Henno. First case: the
primitive-built blacksmith, v1–v5. This is a starting point for repeated trials,
not a claim that an autonomous end-to-end asset pipeline is already complete.

## Direction

Keep reusable methods, materials and ordinary props, and design the main masses
for each building's role. A fixed building kit is no longer the only feasible
approach. Parameterized construction can retain the economics of reuse while giving
different buildings more distinctive roofs, footprints and structural accents.

The initial skill lives at
[`project/skills/civ6-3d-art/SKILL.md`](../skills/civ6-3d-art/SKILL.md). It is packaged
here for versioning and cross-machine handoff during development; its modeling rules
are project-neutral. Keep CSC asset paths, trial history and art contracts in project
docs/specs. Existing `civ6-modding` remains responsible for general art/game integration.
After trials, the module can move to a standalone shared skill package or be folded
into that skill's art references without maintaining conflicting copies.

## What the blacksmith establishes

| Observation | Evidence | Scope |
|---|---|---|
| Primitive/custom-face construction can achieve useful silhouette economics | v4/v5: 1,491 CN6 vertices, 781 triangles, one material | Proven for this building, not every asset type |
| Structural width matters more than texture compensation | Bargeboard was too thin; perpendicular width and heavier framing improved shape | Reusable geometric lesson |
| Materials need designed relief | Aligned height and semantic regions replaced indiscriminate color-height inference | Implemented; artistic settings remain asset specific |
| Technical maps need independent roles | Unique UV2 geometry AO; aligned UV1 material maps; UV3 emissive | Validated in the saved Blender case |
| Game scale changes priorities | Supplied in-game screenshot shows the silhouette holding up while small props recede | Visual evidence from the user |
| Destination vertex parity worked | Henno confirmed 1,491 Blender vertices also appeared as 1,491 in Asset Editor; CN6 was measured at 1,491 | Confirmed for the blacksmith; extend testing to other topology |

The screenshot suggested softer tile-edge repetition, a warmer/less pristine chimney,
and clearer emphasis in the working bay. These remain proposed art refinements.
Do not silently record the assistant's critique as the user's confirmed preference.

Artifacts: [`output/blacksmith-v5`](../../output/blacksmith-v5/README.md), including
the blend, clean export scene, CN6, external maps, normal comparison and validation.

## Build three things together

Texture generation is an explicit part of the skill, including
[prompt templates and material directives](../skills/civ6-3d-art/references/texture-image-generation.md),
atlas edit invariants, tiling/padding checks and the separation of artistic B from
aligned technical maps. This was specifically requested by Henno.

1. **A concise skill.** It carries decisions, technical constraints and routing to
   focused references. It should help a fresh session avoid known failures.
2. **A small tested tool library.** Extract stable building operations, material/UV
   routines, render checks and export reports from the successful scripts. Do not
   generalize every blacksmith-specific threshold or profile into a universal tool.
3. **A reference and trial collection.** Keep annotated source examples, approved
   concepts, failures and in-game comparisons. These give the art instructions meaning.

Longer instructions alone will not establish dependable art production. Repeated
results on different buildings, with diminishing manual intervention, are the test.

## First engineering task: remove surprises in export

Inspect the active exporter and pin/hash the version used for trials. The current
CN6 writer keys vertices by source vertex ID and all three UV pairs, but averages
normal/tangent/bitangent data by source vertex on its ordinary path. A generic
position-plus-attributes estimate is not an exact substitute for that implementation.

Prepare five fixtures: hard cube, smooth cylinder, mirrored UV patch, planar quad
triangulation, independent UV2 seam. Export them through the Windows conversion path
and compare the same mesh/LOD in Blender, CN6 and FGX/Asset Editor. The blacksmith
already has user-confirmed parity at 1,491; these fixtures test generality. Check tangent
shading, not just counts. Record whether splits are expected, unnecessary or missing.

Maintain an editable source and a derived export mesh so Blender can expose final
splits. Target equality between the export-prepared mesh and the destination count;
retain the smaller source count as an authoring statistic. Avoid promising equality
with every Blender UI aggregate. Explain mesh groups/attachments/LODs when comparing.

Then extract a reusable budget/validation report and export preparation step. An
exporter fix may be appropriate, but only after the fixtures expose the exact failure
and a regression test protects imported assets as well as authored ones.

## Trial sequence

Use real needed assets: an open market stall/pavilion, a masonry bakery or kiln,
and a small production prop such as a loom. The contrasts test open surfaces, curves,
cloth, timber, masonry and small mechanical forms. Set budgets per asset from a
comparable game reference; do not impose the blacksmith budget on everything.

For each trial: brief → approved concept as needed → gray model → atlas/materials
→ measured export → game placement/review. Record total time to acceptance, human
interventions, revisions, counts, material/texture cost and visual assessment. A
successful trial should produce both a usable asset and one or two demonstrated
improvements to the skill/tools.

After these, build a different asset in a fresh session using only the skill,
project brief and references. That tests whether the method survives without this
conversation. This trial is proposed; it has not been run as part of drafting.

## Tool choices

The recommendation is to make the current Blender route dependable before adding
another generative service as a dependency.

| Capability | Recommended role | Evidence / limit |
|---|---|---|
| Blender Python plus the existing Blender MCP | Geometry, UVs, materials, bakes, repeatable builds and inspection | Worked on the blacksmith. Headless scripts produced saved/reviewed artifacts; MCP supplies live scene interaction |
| Existing image generation | Concepts and artistic base-color atlases | Worked here; region fidelity and surface treatment still need inspection |
| Deterministic map/export helpers | Aligned technical maps, budgets, file validation | PBR helper now supports height and region inputs; a general export validator remains to be extracted |
| Windows SDK/CivNexus6/Asset Editor and game access | Converted-count calibration, material cook, registration and in-game acceptance | Blacksmith parity is user-confirmed; repeatable destination tests need this toolchain |
| Higgsfield | Optional comparison for alternative image models, generated organic props or bake sources | Documented capabilities; not tested on our constrained asset brief |

The community [Blender MCP project](https://github.com/ahujasid/blender-mcp) exposes
scene information, object/material edits and Python execution. For noninteractive
work, Blender also supports [background Python execution](https://docs.blender.org/api/3.3/info_tips_and_tricks.html).
The connection is a way to operate Blender; the model-building logic lives in the
scripts and the agent's decisions.

Higgsfield distinguishes its generation MCP from a separate Blender Bridge, which
connects to its installed add-on and open scene. Its Blender page advertises scene
assembly, mesh generation and material/image insertion, and lists Meshy 5 among its
models. These are vendor descriptions; they do not establish our exported vertex
budget, UV/AO conventions or silhouette quality. See the
[Blender plugin page](https://higgsfield.ai/plugins/blender) and
[Bridge explanation](https://higgsfield.ai/blog/higgsfield-blender-plugin).

An optional comparison should use the same approved concept and acceptance rubric
and include cleanup time. Image models may improve a concept/atlas even if their 3D
route is unsuitable. Organic forms or high-poly relief sources are sensible trials.
No Higgsfield tools were callable in this session, and none were installed or invoked.
Its [MCP help page](https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp)
says automated generations consume credits even where web use is unlimited; agree
a small experiment budget before running paid comparisons.

## Toward gameplay idea → working content

Use the project's structured art/gameplay brief to connect stages, with an asset
manifest carrying IDs, dimensions, footprint/origin, states, texture/material names,
attachment points, output paths and validation status. Model generation should
produce a predictable asset package that existing scaffolding tools can consume.

Extend one small real gameplay feature through the whole chain: design/spec,
concept/model, texture/export, converted geometry/materials, AST/ArtDefs/XLP,
ModBuddy registration, gameplay/text/icons where required, and game verification.
Repeat that complete path before scaling an entire Quarter. Construction/pillaged
and worked/unworked or emissive variants belong in the brief when required, not as
late surprises. Animation needs a separate validated path when an asset calls for it.

The same repo and manifest can connect modeling on Mac to conversion and game checks
on Windows. A task description or an installed plugin does not itself grant access
to another machine; use the user's established agent workflow for the handoff.

## Adding references

Henno can supply links, quotations, crops, good/bad comparisons or actual assets in
whatever form is convenient. For each, capture provenance, interpretation, the
modeling decision it changes and a way to test it. Keep original guidance distinct
from our inference. The most useful visual examples show both a close-up and the
same asset at game scale, with a sentence explaining what should be noticed.

Next practical step: finish count/shading calibration, then choose the next real
building trial while continuing to build this reference collection.

## Reference intake: performance discussion

Henno identified performance priorities as the useful topic and subsequently asked
that the pile-specific additions be rolled back pending better evidence. Those
prescriptions have been removed from the skill; the original supplied conversation
remains unchanged as source material. City Lights remains an intended compatibility
target, not a demonstrated compatible configuration.

The current assessment and investigation plan are in
[Art performance and evidence review](art-performance-evidence-review.md).
The skill's [performance reference](../skills/civ6-3d-art/references/performance.md)
distinguishes working design priorities from measured engine bottlenecks.
