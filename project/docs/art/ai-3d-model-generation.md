# CSC 3D authoring: project tooling bridge

> **Documentation audit — 2026-10-12: Current.** Reusable authoring guidance now lives in civ6-art; CSC retains project bindings and trial evidence. This page routes project tools and preserves relevant CSC examples; it does not duplicate the complete authoring workflow.
> Classification: 3D production. See the [document audit](../DOCUMENT-AUDIT.md).

## Workflow authority

Read the installed **civ6-art** skill reference
`references/geometry-guided-painting.md` for the reusable method: optional
2D/diagram/rough-3D concept guidance; coherent forms and UV regions; geometry as a
structured canvas for painted B; aligned N/G/M; geometry AO; and full-route
comparison with an optional generated high-poly source.

Then read **civ-supply-chains** `references/art-geometry-guided-authoring.md` for
CSC scale, generator bindings, storage atlas decisions, observed trial results and
open questions. Keep generic art direction, texture-generation instructions,
geometry and export principles in civ6-art; do not maintain another full recipe here.

The [building art plan](quarter-building-art-plan.md) governs existing kit/reuse and
composition. Current session approvals remain valid. Preserve Henno-edited geometry,
placements and native transforms under the CSC production conventions.

## Tools and technical contracts

| Work | Current project entry point |
|---|---|
| Companion N/G/M from registered B/height/material masks | `project/tools/blender/csc_generate_pbr_maps.mjs`; inspect live help and [authored relief documentation](textures-and-uvs.md#authored-relief-with-the-companion-map-generator) |
| Shared/independent positional AO packing | [Shared atlas AO](shared-atlas-ao.md) |
| Blender scene decoding, attachments and actual export counts | [Composed scene export](blender-scene-export.md), `project/tools/blender/export_assets.py` |
| Native prop reuse and preserved source geometry/UVs/materials | [Reusable prop library](reusable-prop-library.md) |
| Registration/cooking after a validated handoff | Installed CSC skill `references/art-final-blend-integration.md` |

Put generated art, scripts, reports and intermediates in the active host's authorized
output location. Retain prompts, guides and authoring sources with the versioned asset.
Keep active PNGs relative and external. Reopen the delivered blend and run the saved-file
validator and relevant actual exporter/source checks before reporting it ready.

## Important distinctions retained from the trials

- A continuous reusable **beam-grain swatch** and a **façade-specific painted patch**
  serve different purposes. Boards, shallow joinery, frames and stone divisions may
  be painted when their structure belongs to that mapped patch. Do not ban painted
  construction details or force every separator into geometry.
- Preserve chunky, exaggerated forms. For a loom, the textile panel must read;
  a few substantial cords/weights can convey its mechanism. Fine repeated elements
  should not shrink the main visual signal or consume its geometry budget.
- Use the active asset budget and actual post-UV2 exported count. Blanket claims that
  welding never matters, every hard edge splits identically, or all unseen-in-one-view
  faces can be removed are invalid. Inspect the current exporter and all exposed views.
- A UV1/B change alone does not invalidate an unchanged geometry/UV2 AO bake. H is
  authoring data, not a required building runtime map. UV3 is emissive, not a generic
  substitute for other material data.
- Clean Export scenes follow the composed-scene contract. Do not require all assets
  and native attachments to become one joined mesh or apply their transforms.

Blender preview, serialized CN6 checks, destination conversion and in-game visual
acceptance are separate evidence. State which were actually performed.
