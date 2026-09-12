# CSC Memory Index

`memory/` is agent-facing scratch/reference, not the durable home for collaborator-facing project truth. Durable notes should live in `project/docs/` or public `docs/`.

This folder was cleaned in June 2026: stale session notes were removed, and reusable implementation notes were promoted into durable docs.

## Active notes

- [Quarter building art plan](../project/docs/art/quarter-building-art-plan.md) — agreed 12 September 2026: retain Henno’s kit, Quarter roof/beam colours, assistant-built chunky prop scenes, storage/crane animation, Industrial Era variants and later cultural additions. [Internal docs index](../project/docs/README.md); studies now live under `project/docs/research/`.

- [Art Dropzone location and catalog intake](project_art-dropzone.md) — current Google Drive art/output root; research catalog scope and validation notes.
- [Civ VI 3D art skill development](../project/docs/research/art/civ6-3d-art-development.md) — first portable skill draft, texture-generation directives, trial plan and tool assessment; blacksmith 1,491-vertex Asset Editor parity confirmed by Henno.
- [Blacksmith v5 texture refinement](session_blacksmith_v5.md) — latest blend/package paths, authored relief, generator changes and validation.
- [Civ VI shape hierarchy feedback](feedback_csc_shape_hierarchy.md) — chunky structural forms must read in clay; bargeboard thickness must be measured across the slope.
- [Working Files reachable from Mac](project_working-files-mac-access.md) — Shadow's Working Files syncs via Google Drive `Other computers/My PC/`
- [Art performance & material architecture](project_art-performance-and-materials.md) — revised evidence boundary: resource discipline and geometry budgets; no measured universal Civ VI bottleneck ranking.

## Promoted docs

- Dynamic art properties → `project/docs/art/dynamic-art-properties.md`
- Bakers service notification UI → `project/docs/integrations/bakers-service-notification-ui.md`
- ComfyUI icon implementation notes → `project/docs/art/2d/icon-pipeline-implementation-notes.md`

## Resolved feedback

- Decal geometry visibility feedback was applied to the generic `civ6-gameplay` skill: `DecalGeometry` supports normal `GroupStates`; the limitation is reveal-animation keying, not general visibility.

## Local tooling lessons

- Shadow's normal Windows environment has Python installed at `C:\Users\Shadow\AppData\Local\Programs\Python\Python312\` with the launcher at `C:\Users\Shadow\AppData\Local\Programs\Python\Launcher\py.exe`. If Codex command execution cannot resolve or run `py`/`python`, describe it as a Codex sandbox/runtime limitation, not as "Python is not on PATH" for the user. For Codex-side tests, use the bundled runtime at `C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` unless the user's local Python environment is specifically required.

## Active implementation reset

- Tailors contract-first restart → `session_tailors_contract_restart.md`

## Removed stale notes

- old session startup order;
- obsolete project notes location pointer;
- Q2 2026 roadmap snapshot;
- old memory-discipline feedback now superseded by repo documentation boundaries;
- CivAssetForge viewer prototype notes, which belong with the separate CivAssetForge repo rather than CSC memory.
