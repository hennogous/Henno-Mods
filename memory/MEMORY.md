# CSC Memory Index

`memory/` is agent-facing scratch/reference, not the durable home for collaborator-facing project truth. Durable notes should live in `project/docs/` or public `docs/`.

This folder was cleaned in June 2026: stale session notes were removed, and reusable implementation notes were promoted into durable docs.

## Promoted docs

- Dynamic art properties → `project/docs/dynamic-art-properties.md`
- Bakers service notification UI → `project/docs/bakers-service-notification-ui.md`
- ComfyUI icon implementation notes → `project/docs/icon-pipeline-implementation-notes.md`

## Resolved feedback

- Decal geometry visibility feedback was applied to the generic `civ6-modding` skill: `DecalGeometry` supports normal `GroupStates`; the limitation is reveal-animation keying, not general visibility.

## Removed stale notes

- old session startup order;
- obsolete project notes location pointer;
- Q2 2026 roadmap snapshot;
- old memory-discipline feedback now superseded by repo documentation boundaries;
- CivAssetForge viewer prototype notes, which belong with the separate CivAssetForge repo rather than CSC memory.
