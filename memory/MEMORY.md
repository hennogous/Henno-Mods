# CSC Memory Index

`memory/` is agent-facing scratch/reference, not the durable home for collaborator-facing project truth. Durable notes should live in `project/docs/` or public `docs/`.

This folder was cleaned in June 2026: stale session notes were removed, and reusable implementation notes were promoted into durable docs.

## Promoted docs

- Dynamic art properties → `project/docs/dynamic-art-properties.md`
- Bakers service notification UI → `project/docs/bakers-service-notification-ui.md`
- ComfyUI icon implementation notes → `project/docs/icon-pipeline-implementation-notes.md`

## Resolved feedback

- Decal geometry visibility feedback was applied to the generic `civ6-modding` skill: `DecalGeometry` supports normal `GroupStates`; the limitation is reveal-animation keying, not general visibility.

## Local tooling lessons

- Shadow's normal Windows environment has Python installed at `C:\Users\Shadow\AppData\Local\Programs\Python\Python312\` with the launcher at `C:\Users\Shadow\AppData\Local\Programs\Python\Launcher\py.exe`. If Codex command execution cannot resolve or run `py`/`python`, describe it as a Codex sandbox/runtime limitation, not as "Python is not on PATH" for the user. For Codex-side tests, use the bundled runtime at `C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` unless the user's local Python environment is specifically required.

## Removed stale notes

- old session startup order;
- obsolete project notes location pointer;
- Q2 2026 roadmap snapshot;
- old memory-discipline feedback now superseded by repo documentation boundaries;
- CivAssetForge viewer prototype notes, which belong with the separate CivAssetForge repo rather than CSC memory.
