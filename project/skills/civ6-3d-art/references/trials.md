# Trials and reference intake

## Learn from a varied small set

Use the blacksmith as a baseline, then choose meaningfully different assets before
scaling production. Suggested next trials, not yet commissioned or executed:

| Trial | What it tests |
|---|---|
| Open market stall or timber pavilion | Thin surfaces, silhouette thickness, cloth and negative space |
| Masonry kiln or bakery with rounded oven | Curves, mixed smooth/hard shading, readable construction relief |
| A small production prop such as a loom | Budget at prop scale, grain direction, mechanism readability |
| Another building in a fresh session | Whether the skill transfers without blacksmith conversation history |

Set comparable constraints in an asset brief, then review concept, gray model,
materials, actual export and in-game result. Record elapsed work, human interventions,
revision count, actual vertex/material/texture costs and unresolved issues. Measure
time to an accepted usable asset, not merely generation latency.

Do not test only roofs and wood until every result looks like the blacksmith. Include
different eras/cultures when the project needs them. Choose a real project need so
successful trials become usable assets.

## Review rubric

Visual judgments: recognizable role; big/intermediate/fine hierarchy; readable
silhouette at gameplay scale; material character; fit beside target-era references.
Use examples and short explanations rather than pretending these are objective metrics.

Technical checks: actual vertex/triangle/material budgets; correct visible surfaces
and normals; UV order and AO; texture alignment; converted counts; game registration
and required states. A beautiful render cannot compensate for a failed required export.

For each failure record: input/reference, expected behavior, observed behavior,
evidence, likely cause, intervention, new result and remaining uncertainty. Change
one relevant variable when testing a specific diagnosis. A failed trial is useful
when it leaves a reproducible example and a narrower rule.

## Incorporating Henno's references

Accept links, quotes, crops, existing assets and subjective feedback without requiring
a rigid submission template. Organize the material during intake:

1. Identify its source and whether it is official guidance, community interpretation,
   user preference or an observed artifact.
2. Extract the decision it changes: proportions, shape flow, material marks, geometry
   construction, export behavior, or gameplay readability.
3. Write a candidate rule with scope and a visual or technical check.
4. Compare with existing guidance. Preserve contradictions until resolved by source
   priority, context or a controlled trial.
5. Promote a demonstrated rule to the relevant short reference. Keep raw excerpts
   and detailed trial history in the owning project's docs, not the skill entrypoint.

This is a maintained instruction/tool workflow, not model-weight training. It improves
reliability by preserving references, decisions and tests; it does not guarantee that
every future generated asset will be artistically correct without review.

## Reusable tools to extract after trials

Extract repeated, proven construction operations: tapered boxes, profile-swept beams,
curved roof strips, low-sided vessels, face patches, region UV mapping and export-copy
preparation. Keep them parameterized. Reuse material families and ordinary props where
beneficial; allow major architectural masses to vary by building.

Prioritize an actual-export budget report and a reproducible scene build over a large
library of untested components. Use Blender Python for repeatable build/bake/export
and MCP for scene interaction/inspection. A different MCP connection does not by
itself make the geometry more economical or the art direction more faithful.

Evaluate an optional 3D generator on the same approved concept, export budget and
game-view rubric. Include cleanup/retopology and UV time. Adopt it where it improves
the full result, including as a high-poly bake source; avoid judging by a polished
provider preview alone.
